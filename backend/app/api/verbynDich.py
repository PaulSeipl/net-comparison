import aiohttp
import asyncio
import logging
import re
from datetime import datetime
from typing import Any
from pydantic import PrivateAttr
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.schemas import (
    PriceDetails,
    ProviderEnum,
    NetworkRequestData,
    VerbynDichProduct,
    VerbynDichRequestData,
    VerbynDichQueryParams,
    BaseProvider,
    NormalizedOffer,
)
from app.config import get_settings
from app.utils.connection_mapper import ConnectionTypeMapper
from app.utils.discount_calculator import DiscountCalculator, DiscountResult


class VerbynDich(BaseProvider):
    """
    VerbynDich provider implementation.
    Handles fetching and processing of internet service offers from the VerbynDich provider.
    """

    name: str = ProviderEnum.VERBYNDICH.value
    _logger: logging.Logger = PrivateAttr()
    _discount_calculator: DiscountCalculator = (
        PrivateAttr()
    )  # Placeholder for discount calculator
    MAX_PAGE: int = 17
    REQUEST_TIMEOUT: int = 10  # Request timeout in seconds
    CONCURRENCY_LIMIT: int = (
        5  # Limit concurrent requests to avoid overwhelming the API
    )
    REQUEST_DELAY: float = (
        0.1  # Small delay between requests to avoid overwhelming the API
    )
    PROMOTION_LENGTH: int = 24  # Length of promotion in months

    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger
        self._discount_calculator = DiscountCalculator(
            promotion_length=self.PROMOTION_LENGTH
        )


    async def get_offers(
        self, request_data: NetworkRequestData
    ) -> list[NormalizedOffer]:
        """
        Fetch offers from the provider for the given address.
        Returns a list of normalized offer data.

        Args:
            request_data: The network request data containing address information

        Returns:
            A list of offer data dictionaries
        """
        self._logger.info(f"Fetching offers...")
        self._logger.debug(f"Request data: {request_data}")

        # Prepare request payload
        payload = self._get_payload(request_data)

        # Create a semaphore to limit the number of concurrent requests
        semaphore = asyncio.Semaphore(self.CONCURRENCY_LIMIT)

        async with aiohttp.ClientSession() as session:
            # Create tasks for each page with semaphore for rate limiting
            tasks = []
            for page in range(0, self.MAX_PAGE):
                tasks.append(
                    self._get_offer_with_rate_limit(session, payload, page, semaphore)
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, filter out exceptions if any
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self._logger.error(
                    f"Error fetching page {i}: {result}", exc_info=result
                )
            elif result:  # Filter out empty results
                processed_results.append(result)

        self._logger.info(
            f"Successfully fetched {len(processed_results)} offers"
        )
        return processed_results

    def _get_payload(self, request_data: NetworkRequestData) -> VerbynDichRequestData:
        """Create the payload for the request to the provider"""
        return VerbynDichRequestData.from_address(request_data.address)

    async def _get_offer_with_rate_limit(
        self,
        session: aiohttp.ClientSession,
        payload: VerbynDichRequestData,
        page: int,
        semaphore: asyncio.Semaphore,
    ) -> NormalizedOffer:
        """
        Get an offer with rate limiting via semaphore.

        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The request payload
            page: The page number to fetch
            semaphore: Semaphore to limit concurrent requests

        Returns:
            A dictionary containing the offer data or an empty dict on failure
        """
        async with semaphore:
            self._logger.debug(f"Semaphore acquired for page {page}")
            try:
                return await self._get_offer(session, payload, page)
            finally:
                self._logger.debug(f"Semaphore released for page {page}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientResponseError),
    )
    async def _get_offer(
        self,
        session: aiohttp.ClientSession,
        payload: VerbynDichRequestData,
        page: int = 0,
    ) -> NormalizedOffer:
        """
        Get an offer from the provider for a specific page.
        Automatically retries on certain errors with exponential backoff.

        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The request payload
            page: The page number to fetch

        Returns:
            A dictionary containing the offer data or an empty dict on failure
        """
        settings = get_settings()
        await asyncio.sleep(self.REQUEST_DELAY)  # Small delay between requests

        query_params = VerbynDichQueryParams(
            api_key=settings.VERBYNDICH_API_KEY, page=page
        ).model_dump(by_alias=True)

        raw_response_json = {}

        try:
            self._logger.info(f"Requesting page {page}...")
            async with session.post(
                settings.VERBYNDICH_URL,
                data=payload.body,
                params=query_params,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(
                    f"Page {page} - Status: {response.status}, Headers: {response.headers}"
                )

                # Raise exception for 429 so tenacity can retry
                if response.status == 429:
                    self._logger.warning(
                        f"Rate limit hit ({response.status}) for page {page}, will retry..."
                    )
                    response.raise_for_status()

                if response.status != 200:
                    self._logger.error(f"Error fetching page {page}: {response.status}")
                    return {}

                response.raise_for_status()

                raw_response_json = await response.json()
                self._logger.debug(f"Page {page} - Raw response: {raw_response_json}")

                return self.normalize_offer(raw_response_json)

        except aiohttp.ClientResponseError as e:
            # Attempt to get response text for better error logging
            response_text = "N/A"
            if hasattr(e, "response") and e.response is not None:
                try:
                    response_text = await e.response.text()
                except Exception:
                    pass  # Ignore if can't read text

            self._logger.error(
                f"HTTP error, page {page}: {e.status} {e.message}. "
                f"Response: {response_text}",
                exc_info=False,
            )
            raise  # Let tenacity handle the retry

        except aiohttp.ClientError as e:
            self._logger.exception(
                f"AIOHTTP ClientError, page {page}",
                exc_info=e,
            )
            return {}

        except Exception as e:
            self._logger.exception(
                f"Unexpected error in _get_offer, page {page}",
                exc_info=e,
            )
            return {}
        
    def _get_price_details(self, raw_offer: VerbynDichProduct) -> PriceDetails:
        """Extract price details from the raw offer."""
        base_monthly_cost = raw_offer.monthly_cost_in_cent
        discount_result = self._discount_calculator.calculate_discount(
            base_monthly_cost,
            voucher_percentage=raw_offer.discount_percentage,
            max_discount_in_cent=raw_offer.max_discount,
            discount_in_cent=raw_offer.absolute_discount_in_cent,
        )

        return PriceDetails(
            monthly_cost=base_monthly_cost,
            monthly_cost_with_discount=discount_result.monthly_cost_with_discount,
            monthly_savings=discount_result.monthly_discount,
            monthly_cost_after_promotion=raw_offer.price_after_promotion,
            total_savings=discount_result.total_savings,
            discount_percentage=discount_result.discount_percentage,
        )

    def normalize_offer(self, raw_offer: dict[str, Any]) -> NormalizedOffer:
        """
        Normalize the provider-specific offer format into a common format.

        Args:
            raw_offer: Raw offer data from VerbynDich API

        Returns:
            Normalized offer data matching NormalizedOffer schema
        """
        self._logger.debug(f"Normalizing raw offer: {raw_offer}")
        if not raw_offer or not raw_offer.get("valid", False):
            return None

        try:
            # Extract basic information
            product_name = raw_offer.get("product", "")
            description = raw_offer.get("description", "")
            if not product_name or not description:
                self._logger.warning("Missing product name or description")
                raise ValueError(
                    "Missing product name or description in raw offer"
                )

            # Parse the description to extract offer details
            parsed_data = self._parse_description(description)
            print(f"Parsed data: {parsed_data}")
            price_details = self._get_price_details(parsed_data)

            # Create normalized offer using NormalizedOffer schema
            return NormalizedOffer(
                provider=self.name,
                offer_id=self._generate_offer_id(product_name),
                name=product_name,
                speed=parsed_data.speed,
                connection_type=ConnectionTypeMapper.map_connection_type(
                    parsed_data.connection_type
                ),  
                contract_duration=parsed_data.contract_duration,
                installation_service=False,
                promotion_length=self.PROMOTION_LENGTH,
                tv_service=parsed_data.tv,
                data_limit=parsed_data.data_limit,
                price_details=price_details,
                fetched_at=datetime.now().isoformat(timespec="seconds"),
            )

        except Exception as e:
            self._logger.error(f"Error normalizing offer: {e}", exc_info=True)
            return None

    def _parse_description(self, description: str) -> VerbynDichProduct:
        """
        Parse the German description text to extract offer details.

        Args:
            description: German description text from VerbynDich

        Returns:
            Dictionary with parsed offer details
        """
        parsed = {}

        # Extract monthly cost: "Für nur 30€ im Monat"
        cost_match = re.search(r"Für nur (\d+)€ im Monat", description)
        if cost_match:
            parsed["monthly_cost_in_cent"] = (
                int(cost_match.group(1)) * 100
            )  # Convert to cents
        else:
            self._logger.warning("Could not extract monthly cost from description")
            raise ValueError(
                "Missing monthly cost in description"
            )

        # Extract connection type: "DSL-Verbindung", "Cable-Verbindung", "Fiber-Verbindung"
        connection_match = re.search(r"(DSL|Cable|Fiber|Mobile)-Verbindung", description)
        if connection_match:
            parsed["connection_type"] = connection_match.group(1).upper()
        else:
            self._logger.warning("Could not extract connection type from description")
            raise ValueError(
                "Missing connection type in description"
            )

        # Extract speed: "Geschwindigkeit von 25 Mbit/s"
        speed_match = re.search(r"Geschwindigkeit von (\d+) Mbit/s", description)
        if speed_match:
            parsed["speed"] = int(speed_match.group(1))
        else:
            self._logger.warning("Could not extract speed from description")
            raise ValueError(
                "Missing speed in description"
            )

        # Extract contract duration: "Mindestvertragslaufzeit 12 Monate"
        contract_match = re.search(r"Mindestvertragslaufzeit (\d+) Monate", description)
        if contract_match:
            parsed["contract_duration"] = int(contract_match.group(1))
        else:
            self._logger.warning("Could not extract contract duration from description")
            raise ValueError(
                "Missing contract duration in description"
            )

        # Extract price after promotion: "Ab dem 24. Monat beträgt der monatliche Preis 29€"
        promo_price_match = re.search(
            r"Ab dem \d+\. Monat beträgt der monatliche Preis (\d+)€", description
        )
        if promo_price_match:
            parsed["price_after_promotion"] = (
                int(promo_price_match.group(1)) * 100
            )
        else:
            parsed["price_after_promotion"] = parsed['monthly_cost_in_cent']

        # Extract TV services: "Fernsehsender enthalten RobynTV+"
        tv_match = re.search(r"Fernsehsender enthalten ([^.]+)", description)
        if tv_match:
            parsed["tv"] = f"{tv_match.group(1).strip()}"

        # Extract data limit: "Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt"
        data_limit_match = re.search(
            r"Ab (\d+)GB pro Monat wird die Geschwindigkeit gedrosselt", description
        )
        if data_limit_match:
            parsed["data_limit"] = int(data_limit_match.group(1))

        # Extract age restriction: "nur für Personen unter 27 Jahren"
        age_match = re.search(r"nur für Personen unter (\d+) Jahren", description)
        if age_match:
            parsed["age_restriction"] = int(age_match.group(1))

        # Extract discount information: "Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat"
        discount_match = re.search(
            r"Rabatt von (\d+)% auf Ihre monatliche Rechnung bis zum (\d+)\. Monat",
            description,
        )
        if discount_match:
            parsed["discount_percentage"] = int(discount_match.group(1))

        # Extract maximum discount: "Der maximale Rabatt beträgt 107€"
        max_discount_match = re.search(
            r"Der maximale Rabatt beträgt (\d+)€", description
        )
        if max_discount_match:
            parsed["max_discount"] = int(max_discount_match.group(1)) * 100
            
        # Extract absolute discount: "einmaligen Rabatt von 107€ auf Ihre monatliche Rechnung"
        absolute_discount_match = re.search(
            r"einmaligen Rabatt von (\d+)€ auf Ihre monatliche Rechnung", description
        )
        if absolute_discount_match:
            parsed["absolute_discount_in_cent"] = int(absolute_discount_match.group(1)) * 100


        # Extract minimum order value: "Der Mindestbestellwert beträgt 7€."
        min_order_value_match = re.search(
            r"Der Mindestbestellwert beträgt (\d+)€", description
        )
        if min_order_value_match:
            parsed["min_order_value_in_cent"] = int(min_order_value_match.group(1)) * 100
        
        return VerbynDichProduct(**parsed)

    def _generate_offer_id(self, product_name: str) -> str:
        """
        Generate a unique offer ID from the product name.

        Args:
            product_name: The product name from VerbynDich

        Returns:
            A unique offer ID
        """
        # Remove spaces and special characters, convert to lowercase
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", product_name.lower())
        return f"verbyndich_{clean_name}"
