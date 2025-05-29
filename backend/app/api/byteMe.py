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
    ProviderEnum,
    NetworkRequestData,
    ByteMeQueryParams,
    ApiRequestHeaders,
    BaseProvider,
)
from pydantic import PrivateAttr
from app.config import get_settings


class ByteMe(BaseProvider):
    """
    ByteMe provider implementation.
    Handles fetching and processing of internet service offers from the ByteMe provider.
    """
    name: str = ProviderEnum.BYTEME.value
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
        headers = ApiRequestHeaders(
            content_type="text/xml; charset=utf-8", 
            x_api_key=settings.BYTEME_API_KEY
        ).model_dump(by_alias=True)
        
        address = request_data.address
        query_params = ByteMeQueryParams(
            street=address.street,
            house_number=address.house_number,
            city=address.city,
            plz=address.zip,
        ).model_dump(by_alias=True)

        async with aiohttp.ClientSession(headers=headers) as session:
            # Get all products in a single request
            products = await self._fetch_products(
                session=session,
                query_params=query_params,
            )
            
            if not products:
                self._logger.warning(
                    f"No available products at the given address."
                )
                return []
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
        query_params: Dict[str, Any],
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
                params=query_params,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(f"Offers - Status: {response.status}")
                
                # Check if the response status is OK
                if response.status != 200:
                    self._logger.error(f"Failed to fetch offers: {response.status} - {response.reason}")
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
            raw_products = [product for product in csv.DictReader(csv_data.splitlines())]
            
            # Remove any duplicates
            raw_products = self._remove_duplicates_from_dict_list(raw_products)
            
            # Convert to ByteMeProduct objects
            return [ByteMeProduct(**product) for product in raw_products]
        except Exception as e:
            self._logger.error(
                f"Error parsing CSV data: {e}. Data: {csv_data[:200]}...",
                exc_info=True
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
        
    def normalize_offer(self, offer: ByteMeProduct) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        
        Args:
            offer: The ByteMeProduct object
            
        Returns:
            A normalized offer dictionary
        """
        self._logger.debug(f"Normalizing raw offer: {offer}")
        if not offer:
            return {}
        
        return offer.model_dump()
