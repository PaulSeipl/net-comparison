import asyncio
from pydantic import PrivateAttr
from app.schemas import (
    NormalizedOffer,
    ProviderEnum,
    NetworkRequestData,
    ApiRequestHeaders,
    BaseProvider,
    WebWunderProduct,
    WebWunderFetchReturn,
)
from app.config import get_settings
from typing import Dict, List, Any
import aiohttp
import xml.etree.ElementTree as ET
import logging
from math import floor
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
    REQUEST_TIMEOUT: int = 10  # Request timeout in seconds
    PROMOTION_LENGTH: int = 24
    CONNECTION_TYPES: list[str] = [
        "DSL",
        "CABLE",
        "FIBER",
        "MOBILE",
    ]
    CONNCURENCY_LMIT: int = 5  # Limit concurrent requests

    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger

    @property
    def name(self) -> str:
        return self.name

    async def get_offers(
        self, request_data: NetworkRequestData
    ) -> List[NormalizedOffer]:
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
        headers = ApiRequestHeaders(x_api_key=settings.WEBWUNDER_API_KEY).model_dump(
            by_alias=True
        )
        
        semaphore = asyncio.Semaphore(self.CONNCURENCY_LMIT)

        async with aiohttp.ClientSession(headers=headers) as session:
            # Get all products in a single request
            tasks = []
            for installation_service in [True, False]:
                for connection_type in self.CONNECTION_TYPES:
                    payload = self._create_soap_payload(
                        request_data, connection_type, installation_service
                    )
                    tasks.append(
                        self._fetch_products(
                            session=session,
                            payload=payload,
                            installation_service=installation_service,
                            connection_type=connection_type,
                        )
                    )
            results = await asyncio.gather(*tasks, return_exceptions=False)

        # Parse the XML response and extract products
        processed_products = []
        for result in results:
            if not result.response_text:
                self._logger.warning(
                    f"Empty response received for one of the connection types."
                )
                continue
            
            raw_offers = self._parse_xml_response(result.response_text)
            if not raw_offers:
                self._logger.warning(
                    f"No products found in the response for installation_service {result.installation_service} and connection_type {result.connection_type}."
                )
                continue

            for raw_offer in raw_offers:
                processed_products.append(
                    self.normalize_offer(
                        raw_offer,
                        installation_service=result.installation_service,
                    )
                )
                

        self._logger.info(f"Successfully fetched {len(processed_products)} offers")
        return processed_products


    async def _fetch_offer_with_rate_limit(
        self, 
        session: aiohttp.ClientSession, 
        payload: str, 
        installation_service: bool,
        connection_type: str,
        semaphore: asyncio.Semaphore
    ) -> WebWunderFetchReturn:
        """
        Get an offer with rate limiting via semaphore.
        
        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The request payload
            installation_service: Whether the installation service is required
            connection_type: The connection type to use
            semaphore: Semaphore to limit concurrent requests

        Returns:
            A dictionary containing the offer data or an empty dict on failure
        """
        async with semaphore:
            self._logger.debug(f"Semaphore acquired for installation_service {installation_service} and connection_type {connection_type}")
            try:
                return await self._fetch_offer(session, payload, installation_service, connection_type)
            finally:
                self._logger.debug(f"Semaphore released for installation_service {installation_service} and connection_type {connection_type}")

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=60),
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
        Fetch products from the WebWunder provider.
        Automatically retries on certain errors with exponential backoff.

        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The SOAP XML payload for the request

        Returns:
            The XML response as a string
        """
        settings = get_settings()

        try:
            self._logger.info(f"Fetching available products...")
            async with session.post(
                settings.WEBWUNDER_BASE_URL,
                data=payload,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(f"Offers - Status: {response.status}")

                if response.status != 200:
                    self._logger.error(f"Failed to fetch offers: {response.status}")
                    response.raise_for_status()

                response_text = await response.text()
                self._logger.debug(f"Raw response text: {response_text[:200]}...")

                return WebWunderFetchReturn(
                    installation_service=installation_service,
                    connection_type=connection_type,
                    response_text=response_text,
                )

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
                f"Response: {response_text[:200]}...",
                exc_info=False,
            )
            raise  # Let tenacity handle the retry

        except aiohttp.ClientError as e:
            self._logger.exception(
                f"AIOHTTP ClientError API while fetching offers",
                exc_info=e,
            )
            # TODO custom exception with association to installation_service and connection_type
            return WebWunderFetchReturn(
                installation_service=installation_service,
                connection_type=connection_type,
                response_text="",
            )

        except Exception as e:
            self._logger.exception(
                f"Unexpected error while fetching offers",
                exc_info=e,
            )
            return WebWunderFetchReturn(
                installation_service=installation_service,
                connection_type=connection_type,
                response_text="",
            )

    @staticmethod
    def _create_soap_payload(
        request_data: NetworkRequestData, connection_type: str, installation_service: bool
    ) -> str:
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

    def _parse_xml_response(self, response: str) -> List[WebWunderProduct]:
        # Parse the XML
        root = ET.fromstring(response)

        # Define namespaces
        namespaces = {
            "SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
            "ns2": "http://webwunder.gendev7.check24.fun/offerservice",
        }

        # Find all product entries
        products = root.findall(".//ns2:products", namespaces)

        # Extract data
        product_list = []
        for (
            product
        ) in (
            products
        ):  # Extract voucher information - search directly for fields, None if not found
            percentage_elem = product.find(".//ns2:percentage", namespaces)
            discount_elem = product.find(".//ns2:discountInCent", namespaces)
            max_discount_elem = product.find(".//ns2:maxDiscountInCent", namespaces)
            min_order_elem = product.find(".//ns2:minOrderValueInCent", namespaces)

            # Extract values, handling None cases
            voucher_percentage = (
                int(percentage_elem.text) if percentage_elem is not None else None
            )
            discount_in_cent = (
                int(discount_elem.text) if discount_elem is not None else None
            )
            voucher_max_discount = (
                int(max_discount_elem.text) if max_discount_elem is not None else None
            )
            min_order_value = (
                int(min_order_elem.text) if min_order_elem is not None else None
            )

            product_data = {
                "product_id": product.find("ns2:productId", namespaces).text,
                "provider_name": product.find("ns2:providerName", namespaces).text,
                "speed": int(product.find(".//ns2:speed", namespaces).text),
                "monthly_cost_in_cent": int(
                    product.find(".//ns2:monthlyCostInCent", namespaces).text
                ),
                "monthly_cost_in_cent_from_25th_month": int(
                    product.find(
                        ".//ns2:monthlyCostInCentFrom25thMonth", namespaces
                    ).text
                ),
                "contract_duration_in_months": int(
                    product.find(".//ns2:contractDurationInMonths", namespaces).text
                ),
                "connection_type": product.find(
                    ".//ns2:connectionType", namespaces
                ).text,
                "voucher_percentage": voucher_percentage,
                "max_discount_in_cent": voucher_max_discount,
                "discount_in_cent": discount_in_cent,
                "min_order_value_in_cent": min_order_value,
            }
            product_list.append(WebWunderProduct(**product_data))

        return product_list

    def normalize_offer(
        self, raw_offer: WebWunderProduct, installation_service: bool
    ) -> NormalizedOffer:
        """
        Normalize the provider-specific offer format into a common format.
        """
        if not raw_offer:
            return {}

        raw_offer_dict = raw_offer.model_dump()

        base_monthly_cost = raw_offer_dict["monthly_cost_in_cent"]

        # Calculate effective pricing based on voucher type
        monthly_discount = None
        total_savings_during_promotional_period = None
        monthly_cost_with_discount = None
        discount_percentage = None
        
        connection_type_mapping = {
                'CABLE': 'Cable',
                'FIBER': 'Fiber', 
                'MOBILE': 'Mobile',
                'DSL': 'DSL'  # DSL stays the same
        }
        connection_type = connection_type_mapping.get(
            raw_offer_dict["connection_type"], raw_offer_dict["connection_type"]
        )

        # Handle percentage voucher
        if raw_offer_dict.get("voucher_percentage"):
            # Calculate absolute discount based on percentage
            voucher_percentage = raw_offer_dict["voucher_percentage"]
            max_discount = raw_offer_dict.get(
                "max_discount_in_cent", 10**10
            )  # Default to a very high value if not specified
            monthly_discount_temp = int(base_monthly_cost * (voucher_percentage / 100))
            complete_discount = monthly_discount_temp * self.PROMOTION_LENGTH

            # Cap the discount by max discount
            absolute_discount = min(complete_discount, max_discount)

            # Calculate total savings during promotional period
            monthly_discount = absolute_discount / self.PROMOTION_LENGTH
            monthly_cost_with_discount = base_monthly_cost - monthly_discount
            total_savings_during_promotional_period = absolute_discount
            discount_percentage = floor((monthly_discount / base_monthly_cost) * 100)

        # Handle absolute voucher (distributed over 24 months)
        elif raw_offer_dict.get("discount_in_cent"):
            absolute_discount = raw_offer_dict["discount_in_cent"]
            monthly_discount = int(absolute_discount / self.PROMOTION_LENGTH)

            monthly_cost_with_discount = base_monthly_cost - monthly_discount
            total_savings_during_promotional_period = absolute_discount
            discount_percentage = floor((monthly_discount / base_monthly_cost) * 100)

        return NormalizedOffer(
            provider=ProviderEnum.WEBWUNDER,
            offer_id=raw_offer_dict["product_id"],
            name=raw_offer_dict["provider_name"],
            speed=raw_offer_dict["speed"],
            connection_type=connection_type,
            monthly_cost=base_monthly_cost,
            monthly_cost_with_discount=monthly_cost_with_discount,
            monthly_cost_after_promotion=raw_offer_dict.get(
                "monthly_cost_in_cent_from_25th_month"
            ),
            monthly_savings=monthly_discount,
            total_savings=total_savings_during_promotional_period,
            installation_service=installation_service,
            contract_duration=raw_offer_dict["contract_duration_in_months"],
            discount_percentage=discount_percentage,  # Not applicable for absolute discount
            promotion_length=self.PROMOTION_LENGTH,  # Promotional period length
            fetched_at=datetime.now().isoformat(timespec="seconds"),
        )
