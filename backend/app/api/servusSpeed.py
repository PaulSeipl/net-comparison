import aiohttp
import asyncio
import logging
from typing import Dict, List, Any, Union
from pydantic import PrivateAttr
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.schemas import (
    ProviderEnum,
    NetworkRequestData,
    ServusSpeedAvailableProducts,
    ServusSpeedHeaders,
    ServusSpeedRequestData,
    ServusSpeedRequestAddress,
    ServusSpeedProduct,
    BaseProvider,
)


class ServusSpeed(BaseProvider):
    """
    ServusSpeed provider implementation.
    Handles fetching and processing of internet service offers from the ServusSpeed provider.
    """
    name: str = ProviderEnum.SERVUSSPEED.value
    _logger: logging.Logger = PrivateAttr()
    CONCURRENCY_LIMIT: int = 10  # Maximum number of concurrent requests (provider limit)
    REQUEST_TIMEOUT: int = 10  # Request timeout in seconds
    REQUEST_DELAY: float = 0.1  # Small delay between requests to avoid overwhelming the API

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
        payload = self._get_payload(request_data)
        basic_auth = self._get_basic_auth()

        async with aiohttp.ClientSession(
            base_url=settings.SERVUSSPEED_BASE_URL,
            headers=ServusSpeedHeaders().model_dump(by_alias=True),
            auth=basic_auth,
        ) as session:
            # Get available products first
            response = await self._get_available_products(
                session=session,
                payload=payload,
            )
            
            product_ids = response.available_products

            if not product_ids:
                self._logger.warning(
                    f"No available products at the given address."
                )
                return []
            
            self._logger.info(
                f"Found {len(product_ids)} available products: "
                f"{product_ids}"
            )
            
            # Fetch product details with limited concurrency
            semaphore = asyncio.Semaphore(self.CONCURRENCY_LIMIT)
            async def _get_product_with_rate_limit(product):
                async with semaphore:
                    return await self._get_offer(session, payload, product)
                
            tasks = [_get_product_with_rate_limit(product)
                    for product in product_ids]

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, filtering out exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                product_id = (
                    product_ids[i]
                    if i < len(product_ids)
                    else "unknown"
                )
                self._logger.error(f"Error fetching product {product_id}: {result}", exc_info=result)
            elif result:  # Filter out empty results
                processed_results.append(self.normalize_offer(result))
                
        self._logger.info(f"Successfully fetched {len(processed_results)} offers")
        return processed_results

    def _get_payload(self, request_data: NetworkRequestData) -> ServusSpeedRequestData:
        """
        Create the payload for the request to the provider.
        
        Args:
            request_data: The network request data containing address information
            
        Returns:
            A ServusSpeedRequestData object
        """
        address = ServusSpeedRequestAddress(
            street=request_data.address.street,
            house_number=request_data.address.house_number,
            zip=request_data.address.zip,
            city=request_data.address.city,
            country_code=request_data.address.country_code,
        )
        return ServusSpeedRequestData(address=address)
    
    def _get_basic_auth(self) -> aiohttp.BasicAuth:
        """Get the basic auth helper for the provider.
        
        Returns:
            An aiohttp.BasicAuth object
        """
        settings = get_settings()
        return aiohttp.BasicAuth(
            login=settings.SERVUSSPEED_USERNAME,
            password=settings.SERVUSSPEED_PASSWORD,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientResponseError)
    )
    async def _get_offer(
        self,
        session: aiohttp.ClientSession,
        payload: ServusSpeedRequestData,
        product_id: str,
    ) -> ServusSpeedProduct | Dict[str, Any]:
        """
        Get the offer for a specific product from the provider.
        Automatically retries on certain errors with exponential backoff.
        
        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The request payload
            product: The product ID to fetch
            
        Returns:
            A ServusSpeedProduct object or an empty dict on failure
        """
        settings = get_settings()
        await asyncio.sleep(self.REQUEST_DELAY)  # Small delay between requests
        payload_dict = payload.model_dump(by_alias=True)
        raw_response_json = {}
        
        try:
            async with session.post(
                f"{settings.SERVUSSPEED_GET_PRODUCT_ENDPOINT}/{product_id}",
                json=payload_dict,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(
                    f"Offer for product {product_id} - Status: {response.status}"
                )
                
                # Raise exception for 429 or other errors so tenacity can retry
                if response.status == 429:
                    self._logger.warning(f"Rate limit hit ({response.status}) for product {product_id}, will retry...")
                    response.raise_for_status()
                
                if response.status != 200:
                    self._logger.error(
                        f"Error fetching product {product_id}: {response.status}"
                    )
                    return {}

                raw_response_json = await response.json()
                self._logger.debug(
                    f"Offer for product {product_id} - Raw response: {raw_response_json}"
                )

                return self._map_json_to_product(raw_response_json)

        except aiohttp.ClientResponseError as e:
            # Attempt to get response text for better error logging
            response_text = "N/A"
            if hasattr(e, "response") and e.response is not None:
                try:
                    response_text = await e.response.text()
                except Exception:
                    pass  # Ignore if can't read text
                    
            self._logger.error(
                f"HTTP error API, product {product_id}: {e.status} {e.message}. "
                f"Response: {response_text}",
                exc_info=False,
            )
            raise  # Let tenacity handle the retry
            
        except aiohttp.ClientError as e:
            self._logger.exception(
                f"AIOHTTP ClientError API, product {product_id}",
                exc_info=e,
            )
            return {}
            
        except Exception as e:
            self._logger.exception(
                f"Unexpected error in _get_offer, product {product_id}",
                exc_info=e,
            )
            return {}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientResponseError)
    )
    async def _get_available_products(
        self,
        session: aiohttp.ClientSession,
        payload: ServusSpeedRequestData,
    ) -> ServusSpeedAvailableProducts:
        """
        Get a list of available products from the provider.
        Automatically retries on certain errors with exponential backoff.
        
        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The request payload
            
        Returns:
            A ServusSpeedAvailableProducts object containing product IDs
        """
        payload_dict = payload.model_dump(by_alias=True)
        settings = get_settings()
        
        try:
            self._logger.info(f"Fetching available products...")
            async with session.post(
                f"{settings.SERVUSSPEED_PRODUCTS_ENDPOINT}",
                json=payload_dict,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                response.raise_for_status()  # Will trigger retry via tenacity decorator
                
                if response.status != 200:
                    self._logger.error(
                        f"Error fetching available products: {response.status}"
                    )
                    return ServusSpeedAvailableProducts(available_products=[])
                
                raw_response = await response.json()
                self._logger.debug(f"Available products response: {raw_response}")
                
                return ServusSpeedAvailableProducts(
                    available_products=raw_response.get("availableProducts", [])
                )
                
        except aiohttp.ClientResponseError as e:
            self._logger.error(
                f"HTTP error fetching available products: {e.status} {e.message}",
                exc_info=False
            )
            raise  # Let tenacity handle the retry
            
        except Exception as e:
            self._logger.exception(f"Error fetching available products: {str(e)}")
            return ServusSpeedAvailableProducts(available_products=[])

    def _map_json_to_product(
        self, raw_response_json: Dict[str, Any]
    ) -> ServusSpeedProduct:
        """
        Map the raw JSON response from the API to a ServusSpeedProduct object.
        
        Args:
            raw_response_json: The raw JSON response from the API
            
        Returns:
            A ServusSpeedProduct object
            
        Raises:
            ValueError: If the JSON structure is invalid or missing required fields
        """
        product_data = raw_response_json.get("servusSpeedProduct")
        if not product_data:
            error_msg = "Failed to parse: 'servusSpeedProduct' key missing or data is empty"
            self._logger.error(f"{error_msg}: {raw_response_json}")
            raise ValueError(f"{error_msg}")

        try:
            return ServusSpeedProduct(**product_data)
        except Exception as e:
            self._logger.error(
                f"Error parsing: {e}. Data: {product_data}",
                exc_info=True
            )
            raise ValueError(f"Error parsing: {e}")

    def normalize_offer(self, offer: ServusSpeedProduct) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        
        Args:
            offer: The raw offer data from the provider

        Returns:
            A normalized offer dictionary
        """
        # TODO: Implement normalization logic if needed
        self._logger.debug(
            f"Normalizing raw offer: {offer}..."
        )
        if not offer:
            return {}
        return offer.model_dump()
