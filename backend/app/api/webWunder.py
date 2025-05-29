from pydantic import PrivateAttr
from app.schemas import (
    ProviderEnum,
    NetworkRequestData,
    ApiRequestHeaders,
    BaseProvider,
    WebWunderProduct
)
from app.config import get_settings
from typing import Dict, List, Any
import aiohttp
import xml.etree.ElementTree as ET
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class WebWunder(BaseProvider):
    """
    WebWunder provider implementation.
    Handles fetching and processing of internet service offers from the WebWunder provider.
    """
    name: str = ProviderEnum.WEBWUNDER.value
    _logger: logging.Logger = PrivateAttr()
    REQUEST_TIMEOUT: int = 10  # Request timeout in seconds
    
    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger

    @property
    def name(self) -> str:
        return self.name

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
        payload = self._create_soap_payload(request_data)
        headers = ApiRequestHeaders(x_api_key=settings.WEBWUNDER_API_KEY).model_dump(by_alias=True)

        async with aiohttp.ClientSession(headers=headers) as session:
            # Get all products in a single request
            response_text = await self._fetch_products(
                session=session,
                payload=payload,
            )
            
            if not response_text:
                self._logger.warning(f"No available products at the given address.")
                return []
            
            # Parse the XML response and extract products
            products = self._parse_xml_response(response_text)
            self._logger.info(f"Found {len(products)} products")
        
        # Process and normalize results
        processed_results = []
        for product in products:
            processed_results.append(self.normalize_offer(product))
            
        self._logger.info(f"Successfully fetched {len(processed_results)} offers from {self.provider_name}")
        return processed_results
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientResponseError)
    )
    async def _fetch_products(
        self,
        session: aiohttp.ClientSession,
        payload: str,
    ) -> str:
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
                
                return response_text

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
            return ""
            
        except Exception as e:
            self._logger.exception(
                f"Unexpected error while fetching offers",
                exc_info=e,
            )
            return ""
    
    @staticmethod
    def _create_soap_payload(request_data: NetworkRequestData) -> str:
        address = request_data.address
        return f"""<?xml version="1.0" encoding="UTF-8"?>
                            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                                            xmlns:gs="http://webwunder.gendev7.check24.fun/offerservice">
                            <soapenv:Header/>
                                <soapenv:Body>
                                    <gs:legacyGetInternetOffers>
                                        <gs:input>
                                            <gs:installation>{request_data.installation}</gs:installation>
                                            <gs:connectionEnum>{request_data.connection_type}</gs:connectionEnum>
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
        print(response)
        root = ET.fromstring(response)

        # Define namespaces
        namespaces = {
            'SOAP-ENV': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns2': 'http://webwunder.gendev7.check24.fun/offerservice'
        }

        # Find all product entries
        products = root.findall('.//ns2:products', namespaces)

        # Extract data
        product_list = []
        for product in products:
            product_data = {
                'product_id': product.find('ns2:productId', namespaces).text,
                'provider_name': product.find('ns2:providerName', namespaces).text,
                'speed': product.find('.//ns2:speed', namespaces).text,
                'monthly_cost_in_cent': product.find('.//ns2:monthlyCostInCent', namespaces).text,
                'monthly_cost_in_cent_from_25th_month': product.find('.//ns2:monthlyCostInCentFrom25thMonth', namespaces).text,
                'contract_duration_in_months': product.find('.//ns2:contractDurationInMonths', namespaces).text,
                'connection_type': product.find('.//ns2:connectionType', namespaces).text
            }
            product_list.append(WebWunderProduct(**product_data))

        return product_list
    
    def normalize_offer(self, raw_offer: WebWunderProduct) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        # TODO: Implement the normalization logic.
        # For now, just returning a placeholder
        self._logger.debug(f"Normalizing raw offer: {raw_offer}...")
        if not raw_offer:
            return {}
        return raw_offer.model_dump()

