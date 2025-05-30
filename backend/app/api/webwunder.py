import asyncio
from pydantic import PrivateAttr
from app.schemas import (
    NormalizedOffer,
    PriceDetails,
    ProviderEnum,
    NetworkRequestData,
    WebWunderRequestHeaders,
    BaseProvider,
    WebWunderProduct,
    WebWunderFetchReturn,
)
from app.config import get_settings
from app.api.webwunder_config import WebWunderConfig
from app.utils.xml_parser import WebWunderXMLParser

from app.utils.discount_calculator import DiscountCalculator
from app.utils.connection_mapper import ConnectionTypeMapper
from typing import List
import aiohttp
import logging
from datetime import datetime
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class WebWunder(BaseProvider):
    """
    WebWunder provider implementation.
    Handles fetching and processing of internet service offers from the WebWunder provider.
    """

    name: str = ProviderEnum.WEBWUNDER.value
    _logger: logging.Logger = PrivateAttr()
    _discount_calculator: DiscountCalculator = PrivateAttr()

    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger
        self._discount_calculator = DiscountCalculator(
            promotion_length=WebWunderConfig.PROMOTION_LENGTH
        )

    @property
    def name(self) -> str:
        return self.name

    async def get_offers(
        self, request_data: NetworkRequestData
    ) -> List[NormalizedOffer]:
        """
        Fetch offers from the provider for the given address.

        Args:
            request_data: The network request data containing address information

        Returns:
            A list of normalized offer data
        """
        self._logger.info(f"Fetching offers...")
        self._logger.debug(f"Request data: {request_data}")

        try:
            # Fetch raw offers from API
            fetch_results = await self._fetch_all_offers(request_data)
            # Process and normalize offers
            normalized_offers = self._process_fetch_results(fetch_results)

            self._logger.info(f"Successfully fetched {len(normalized_offers)} offers")
            return normalized_offers

        except Exception as e:
            self._logger.exception("Failed to fetch WebWunder offers")
            raise

    async def _fetch_all_offers(
        self, request_data: NetworkRequestData
    ) -> List[WebWunderFetchReturn]:
        """
        Fetch offers for all connection types and installation service combinations.

        Args:
            request_data: Network request data

        Returns:
            List of fetch results
        """
        headers = self._create_api_headers()
        semaphore = asyncio.Semaphore(WebWunderConfig.CONCURRENCY_LIMIT)

        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = self._create_fetch_tasks(session, request_data, semaphore)
            results = await asyncio.gather(*tasks, return_exceptions=False)

        return results

    def _create_api_headers(self) -> dict:
        """Create API headers for requests."""
        settings = get_settings()
        return WebWunderRequestHeaders(x_api_key=settings.WEBWUNDER_API_KEY).model_dump(
            by_alias=True
        )

    def _create_fetch_tasks(
        self,
        session: aiohttp.ClientSession,
        request_data: NetworkRequestData,
        semaphore: asyncio.Semaphore,
    ) -> List:
        """
        Create fetch tasks for all connection type and installation service combinations.

        Args:
            session: HTTP session
            request_data: Network request data
            semaphore: Semaphore to limit concurrent requests

        Returns:
            List of async tasks
        """
        tasks = []
        for installation_service in WebWunderConfig.INSTALLATION_SERVICE_OPTIONS:
            for connection_type in WebWunderConfig.CONNECTION_TYPES:
                payload = self._create_soap_payload(
                    request_data, connection_type, installation_service
                )
                tasks.append(
                    self._fetch_products_with_semaphore(
                        session=session,
                        payload=payload,
                        installation_service=installation_service,
                        connection_type=connection_type,
                        semaphore=semaphore,
                    )
                )
        return tasks

    def _create_soap_payload(
        self,
        request_data: NetworkRequestData,
        connection_type: str,
        installation_service: bool,
    ) -> str:
        """
        Create SOAP payload for WebWunder API request.

        Args:
            request_data: Network request data containing address information
            connection_type: Type of connection (DSL, CABLE, FIBER, MOBILE)
            installation_service: Whether installation service is requested

        Returns:
            SOAP XML payload as string
        """
        address = request_data.address
        return f"""<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                                    xmlns:gs="http://webwunder.gendev7.check24.fun/offerservice">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <gs:legacyGetInternetOffers>
                                <gs:input>
                                    <gs:installation>{installation_service}</gs:installation>
                                    <gs:connectionEnum>{connection_type}</gs:connectionEnum>
                                    <gs:address>
                                        <gs:street>{address.street}</gs:street>
                                        <gs:houseNumber>{address.house_number}</gs:houseNumber>
                                        <gs:city>{address.city}</gs:city>
                                        <gs:plz>{address.zip}</gs:plz>
                                        <gs:countryCode>{address.country_code}</gs:countryCode>
                                    </gs:address>
                                </gs:input>
                            </gs:legacyGetInternetOffers>
                        </soapenv:Body>
                    </soapenv:Envelope>"""

    def _process_fetch_results(
        self, fetch_results: List[WebWunderFetchReturn]
    ) -> List[NormalizedOffer]:
        """
        Process fetch results and convert to normalized offers.

        Args:
            fetch_results: List of fetch results from API

        Returns:
            List of normalized offers
        """
        normalized_offers = []

        for result in fetch_results:
            if not result.response_text:
                self._logger.warning(
                    f"Empty response for connection_type={result.connection_type}, "
                    f"installation_service={result.installation_service}"
                )
                continue

            try:
                raw_offers = WebWunderXMLParser.parse_response(result.response_text)

                if not raw_offers:
                    self._logger.warning(
                        f"No products found for connection_type={result.connection_type}, "
                        f"installation_service={result.installation_service}"
                    )
                    continue

                for raw_offer in raw_offers:
                    normalized_offer = self.normalize_offer(
                        raw_offer, installation_service=result.installation_service
                    )
                    normalized_offers.append(normalized_offer)

            except Exception as e:
                self._logger.error(
                    f"Failed to process response for connection_type={result.connection_type}, "
                    f"installation_service={result.installation_service}: {e}"
                )
                continue

        return normalized_offers

    @retry(
        stop=stop_after_attempt(WebWunderConfig.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=WebWunderConfig.RETRY_MULTIPLIER,
            min=WebWunderConfig.RETRY_MIN_WAIT,
            max=WebWunderConfig.RETRY_MAX_WAIT,
        ),
        retry=retry_if_exception_type(aiohttp.ClientResponseError),
    )
    async def _fetch_products(
        self,
        session: aiohttp.ClientSession,
        payload: str,
        installation_service: bool,
        connection_type: str,
    ) -> WebWunderFetchReturn:
        """
        Fetch products from the WebWunder provider with retry logic.

        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The SOAP XML payload for the request
            installation_service: Whether installation service is requested
            connection_type: The connection type

        Returns:
            WebWunderFetchReturn with response data
        """
        settings = get_settings()

        try:
            self._logger.debug(
                f"Fetching products for connection_type={connection_type}, "
                f"installation_service={installation_service}"
            )

            async with session.post(
                settings.WEBWUNDER_BASE_URL,
                data=payload,
                timeout=aiohttp.ClientTimeout(total=WebWunderConfig.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(f"Response status: {response.status}")

                if response.status != 200:
                    self._logger.error(
                        f"API request failed with status: {response.status}"
                    )
                    response.raise_for_status()

                response_text = await response.text()
                self._logger.debug(
                    f"Received response: {len(response_text)} characters"
                )

                return WebWunderFetchReturn(
                    installation_service=installation_service,
                    connection_type=connection_type,
                    response_text=response_text,
                )

        except aiohttp.ClientResponseError as e:
            response_text = await self._get_error_response_text(e)
            self._logger.error(
                f"HTTP error {e.status}: {e.message}. Response: {response_text[:200]}..."
            )
            raise  # Let tenacity handle the retry

        except aiohttp.ClientError as e:
            self._logger.exception(f"AIOHTTP ClientError: {e}")
            return self._create_empty_fetch_return(
                installation_service, connection_type
            )

        except Exception as e:
            self._logger.exception(f"Unexpected error: {e}")
            return self._create_empty_fetch_return(
                installation_service, connection_type
            )

    async def _get_error_response_text(self, error: aiohttp.ClientResponseError) -> str:
        """
        Safely extract response text from HTTP error.

        Args:
            error: The HTTP error

        Returns:
            Response text or "N/A" if unavailable
        """
        if hasattr(error, "response") and error.response is not None:
            try:
                return await error.response.text()
            except Exception:
                pass
        return "N/A"

    def _create_empty_fetch_return(
        self, installation_service: bool, connection_type: str
    ) -> WebWunderFetchReturn:
        """
        Create an empty fetch return for error cases.

        Args:
            installation_service: Installation service flag
            connection_type: Connection type

        Returns:
            Empty WebWunderFetchReturn
        """
        return WebWunderFetchReturn(
            installation_service=installation_service,
            connection_type=connection_type,
            response_text="",
        )

    def normalize_offer(
        self, raw_offer: WebWunderProduct, installation_service: bool
    ) -> NormalizedOffer:
        """
        Normalize the provider-specific offer format into a common format.

        Args:
            raw_offer: Raw offer data from WebWunder
            installation_service: Whether installation service is included

        Returns:
            Normalized offer data
        """
        if not raw_offer:
            raise ValueError("Raw offer cannot be empty")

        raw_offer_dict = raw_offer.model_dump()
        base_monthly_cost = raw_offer_dict["monthly_cost_in_cent"]

        # Calculate discounts
        discount_result = self._discount_calculator.calculate_discount(
            base_monthly_cost=base_monthly_cost,
            voucher_percentage=raw_offer_dict.get("voucher_percentage"),
            max_discount_in_cent=raw_offer_dict.get("max_discount_in_cent"),
            discount_in_cent=raw_offer_dict.get("discount_in_cent"),
        )

        # Map connection type to schema format
        connection_type = ConnectionTypeMapper.map_connection_type(
            raw_offer_dict["connection_type"]
        )

        price_details = PriceDetails(
            monthly_cost=base_monthly_cost,
            monthly_cost_with_discount=discount_result.monthly_cost_with_discount,
            monthly_savings=discount_result.monthly_discount,
            monthly_cost_after_promotion=raw_offer_dict.get(
                "monthly_cost_in_cent_from_25th_month"
            ),
            total_savings=discount_result.total_savings,
            discount_percentage=discount_result.discount_percentage,
        )

        return NormalizedOffer(
            provider=ProviderEnum.WEBWUNDER,
            offer_id=raw_offer_dict["product_id"],
            name=raw_offer_dict["provider_name"],
            speed=raw_offer_dict["speed"],
            connection_type=connection_type,
            price_details=price_details,
            installation_service=installation_service,
            contract_duration=raw_offer_dict["contract_duration_in_months"],
            promotion_length=WebWunderConfig.PROMOTION_LENGTH,
            fetched_at=datetime.now().isoformat(timespec="seconds"),
        )

    async def _fetch_products_with_semaphore(
        self,
        session: aiohttp.ClientSession,
        payload: str,
        installation_service: bool,
        connection_type: str,
        semaphore: asyncio.Semaphore,
    ) -> WebWunderFetchReturn:
        """
        Fetch products with semaphore-controlled concurrency.

        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The SOAP XML payload for the request
            installation_service: Whether installation service is requested
            connection_type: The connection type
            semaphore: Semaphore to limit concurrent requests

        Returns:
            WebWunderFetchReturn with response data
        """
        async with semaphore:
            self._logger.debug(
                f"Semaphore acquired for connection_type={connection_type}, "
                f"installation_service={installation_service}"
            )
            try:
                return await self._fetch_products(
                    session=session,
                    payload=payload,
                    installation_service=installation_service,
                    connection_type=connection_type,
                )
            finally:
                self._logger.debug(
                    f"Semaphore released for connection_type={connection_type}, "
                    f"installation_service={installation_service}"
                )
