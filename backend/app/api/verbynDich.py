import aiohttp
import asyncio
import logging
from typing import Dict, List, Any
from pydantic import PrivateAttr
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.schemas import (
    ProviderEnum,
    NetworkRequestData,
    VerbynDichRequestData,
    VerbynDichQueryParams,
    BaseProvider
)
from app.config import get_settings


class VerbynDich(BaseProvider):
    """
    VerbynDich provider implementation.
    Handles fetching and processing of internet service offers from the VerbynDich provider.
    """
    name: str = ProviderEnum.VERBYNDICH.value
    _logger: logging.Logger = PrivateAttr()
    MAX_PAGE: int = 17
    REQUEST_TIMEOUT: int = 10  # Request timeout in seconds
    CONCURRENCY_LIMIT: int = 5  # Limit concurrent requests to avoid overwhelming the API
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
        
        # Prepare request payload
        payload = self._get_payload(request_data)
        
        # Create a semaphore to limit the number of concurrent requests
        semaphore = asyncio.Semaphore(self.CONCURRENCY_LIMIT)
        
        async with aiohttp.ClientSession() as session:
            # Create tasks for each page with semaphore for rate limiting
            tasks = []
            for page in range(0, self.MAX_PAGE):
                tasks.append(self._get_offer_with_rate_limit(session, payload, page, semaphore))
                
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, filter out exceptions if any
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self._logger.error(f"Error fetching page {i}: {result}", exc_info=result)
            elif result:  # Filter out empty results
                processed_results.append(result)
                
        self._logger.info(f"Successfully fetched {len(processed_results)} offers from {self.provider_name}")
        return processed_results

    def _get_payload(self, request_data: NetworkRequestData) -> VerbynDichRequestData:
        """
        Create the payload for the request to the provider.
        
        Args:
            request_data: The network request data containing address information
            
        Returns:
            A VerbynDichRequestData object
        """
        return VerbynDichRequestData.from_address(request_data.address)

    async def _get_offer_with_rate_limit(
        self, 
        session: aiohttp.ClientSession, 
        payload: VerbynDichRequestData, 
        page: int,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
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
        retry=retry_if_exception_type(aiohttp.ClientResponseError)
    )
    async def _get_offer(
        self, 
        session: aiohttp.ClientSession, 
        payload: VerbynDichRequestData, 
        page: int = 0
    ) -> Dict[str, Any]:
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
            api_key=settings.VERBYNDICH_API_KEY,
            page=page
        ).model_dump(by_alias=True)
        
        raw_response_json = {}
        
        try:
            self._logger.info(f"Requesting page {page}...")
            async with session.post(
                settings.VERBYNDICH_URL,
                data=payload.body,
                params=query_params,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT)
            ) as response:
                self._logger.debug(f"Page {page} - Status: {response.status}, Headers: {response.headers}")
                
                # Raise exception for 429 so tenacity can retry
                if response.status == 429:
                    self._logger.warning(f"Rate limit hit ({response.status}) for page {page}, will retry...")
                    response.raise_for_status()
                    
                if response.status != 200:
                    self._logger.error(
                        f"Error fetching page {page}: {response.status}"
                    )
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

    def normalize_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        # TODO: Implement the normalization logic.
        # For now, just returning a placeholder
        self._logger.debug(f"Normalizing raw offer: {raw_offer}...")
        if not raw_offer:
            return {}
        return raw_offer

