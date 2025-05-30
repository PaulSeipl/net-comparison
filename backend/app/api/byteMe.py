from datetime import datetime
import logging
import csv
import aiohttp
from typing import Dict, List, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.schemas import (
    ByteMeProduct,
    NormalizedOffer,
    PriceDetails,
    ProviderEnum,
    NetworkRequestData,
    ByteMeQueryParams,
    WebWunderRequestHeaders,
    BaseProvider,
)
from pydantic import PrivateAttr
from app.config import get_settings
from app.utils.connection_mapper import ConnectionTypeMapper
from app.utils.discount_calculator import DiscountCalculator, DiscountResult


class ByteMe(BaseProvider):
    """
    ByteMe provider implementation.
    Handles fetching and processing of internet service offers from the ByteMe provider.
    """

    name: str = ProviderEnum.BYTEME.value
    _logger: logging.Logger = PrivateAttr()
    _discount_calculator: DiscountCalculator = (
        PrivateAttr()
    )  # Placeholder for discount calculator
    REQUEST_TIMEOUT: int = 10  # Request timeout in seconds
    PROMOTION_LENGTH: int = 24  # Length of promotion in months

    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger
        self._discount_calculator = DiscountCalculator(
            promotion_length=self.PROMOTION_LENGTH
        )

    async def get_offers(
        self, request_data: NetworkRequestData
    ) -> List[Dict[str, Any]]:
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

        # Prepare session and request parameters
        settings = get_settings()
        headers = WebWunderRequestHeaders(
            content_type="text/xml; charset=utf-8", x_api_key=settings.BYTEME_API_KEY
        ).model_dump(by_alias=True)

        address = request_data.address
        query_params = ByteMeQueryParams(
            street=address.street,
            house_number=address.house_number,
            city=address.city,
            plz=address.zip,
        )

        async with aiohttp.ClientSession(headers=headers) as session:
            # Get all products in a single request
            products = await self._fetch_products(
                session=session,
                query_params=query_params,
            )

            if not products:
                self._logger.warning(f"No available products at the given address.")
                return []
            self._logger.info(f"Found {len(products)} products")
        # Process and normalize results
        processed_results = []
        for product in products:
            processed_results.append(self.normalize_offer(product))

        self._logger.info(f"Successfully fetched {len(processed_results)} offers")
        return processed_results

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(aiohttp.ClientResponseError),
    )
    async def _fetch_products(
        self,
        session: aiohttp.ClientSession,
        query_params: ByteMeQueryParams,
    ) -> List[ByteMeProduct]:
        """
        Fetch products from the ByteMe provider.
        Automatically retries on certain errors with exponential backoff.

        Args:
            session: The aiohttp ClientSession to use for requests
            query_params: The query parameters for the request

        Returns:
            A list of ByteMeProduct objects
        """
        settings = get_settings()

        try:
            self._logger.info(f"Fetching available products...")
            async with session.get(
                settings.BYTEME_BASE_URL,
                params=query_params.model_dump(by_alias=True),
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(f"Offers - Status: {response.status}")

                # Check if the response status is OK
                if response.status != 200:
                    self._logger.error(
                        f"Failed to fetch offers: {response.status} - {response.reason}"
                    )
                    response.raise_for_status()

                raw_response_text = await response.text()
                self._logger.debug(f"Raw response text: {raw_response_text}")

                # Parse the CSV response and convert to ByteMeProduct objects
                return self._parse_csv_to_products(raw_response_text)

        except aiohttp.ClientResponseError as e:
            # Attempt to get response text for better error logging
            response_text = "N/A"
            if hasattr(e, "response") and e.response is not None:
                try:
                    response_text = await e.response.text()
                except Exception:
                    pass  # Ignore if can't read text

            self._logger.error(
                f"HTTP error API: {e.status} {e.message}. "
                f"Response: {response_text}",
                exc_info=False,
            )
            raise  # Let tenacity handle the retry

        except aiohttp.ClientError as e:
            self._logger.exception(
                f"AIOHTTP ClientError API while fetching offers",
                exc_info=e,
            )
            return []

        except Exception as e:
            self._logger.exception(
                f"Unexpected error while fetching offers",
                exc_info=e,
            )
            return []

    def _parse_csv_to_products(self, csv_data: str) -> List[ByteMeProduct]:
        """
        Parse the CSV response and convert it into a list of ByteMeProduct objects.

        Args:
            csv_data: CSV data as a string

        Returns:
            A list of ByteMeProduct objects

        Raises:
            ValueError: If the CSV data is invalid or cannot be parsed
        """
        try:
            # Parse CSV into dictionaries
            raw_products = [
                product for product in csv.DictReader(csv_data.splitlines())
            ]

            # Remove any duplicates
            raw_products = self._remove_duplicates_from_dict_list(raw_products)

            # Convert to ByteMeProduct objects
            return [ByteMeProduct(**product) for product in raw_products]
        except Exception as e:
            self._logger.error(
                f"Error parsing CSV data: {e}. Data length: {len(csv_data)}...",
                exc_info=True,
            )
            raise ValueError(f"Error parsing CSV data: {e}")

    def _remove_duplicates_from_dict_list(
        self, dict_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicates from a list of dictionaries.

        Args:
            dict_list: List of dictionaries to deduplicate

        Returns:
            A list of unique dictionaries
        """
        return [dict(unique) for unique in {tuple(d.items()) for d in dict_list}]

    def _get_price_details(self, raw_offer: ByteMeProduct) -> PriceDetails:
        """Extract price details from the raw offer."""
        base_monthly_cost = raw_offer.monthly_cost_in_cent
        discount_result = DiscountResult()
        if raw_offer.voucher_type == "percentage":
            discount_result = self._discount_calculator.calculate_discount(
                base_monthly_cost, voucher_percentage=raw_offer.voucher_value
            )
        elif raw_offer.voucher_type == "absolute":
            discount_result = self._discount_calculator.calculate_discount(
                base_monthly_cost, discount_in_cent=raw_offer.voucher_value
            )

        return PriceDetails(
            monthly_cost=base_monthly_cost,
            monthly_cost_with_discount=discount_result.monthly_cost_with_discount,
            monthly_savings=discount_result.monthly_discount,
            monthly_cost_after_promotion=raw_offer.after_two_years_monthly_cost,
            total_savings=discount_result.total_savings,
            discount_percentage=discount_result.discount_percentage,
        )

    def normalize_offer(self, raw_offer: ByteMeProduct) -> NormalizedOffer:
        """
        Normalize the provider-specific offer format into a common format.

        Args:
            offer: The ByteMeProduct object

        Returns:
            A normalized offer dictionary
        """
        price_details = self._get_price_details(raw_offer)

        return NormalizedOffer(
            provider=self.name,
            offer_id=raw_offer.product_id,
            name=raw_offer.provider_name,
            speed=raw_offer.speed,
            connection_type=ConnectionTypeMapper.map_connection_type(
                raw_offer.connection_type
            ),
            installation_service=raw_offer.installation_service,
            contract_duration=raw_offer.duration_in_months,
            promotion_length=self.PROMOTION_LENGTH,
            tv_service=raw_offer.tv,
            data_limit=raw_offer.limit_from,
            fetched_at=datetime.now().isoformat(timespec="seconds"),
            price_details=price_details,
        )
