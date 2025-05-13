import aiohttp
from pydantic import PrivateAttr
from app.schemas import (
    ProviderEnum,
    NetworkRequestData,
    VerbynDichRequestData,
    VerbynDichQueryParams,
    BaseProvider
)
from app.config import get_settings
from typing import Dict, List, Any
import logging
import asyncio


class VerbynDich(BaseProvider):
    name: str = ProviderEnum.VERBYNDICH.value
    _logger: logging.Logger = PrivateAttr()
    MAX_PAGE: int = 17
    CONCURRENCY_LIMIT: int = 5 # Defines a concurrency limit for the number of requests to be made at once; 5 is max
    
    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger

    def provider_name(self) -> str:
        return self.name

    async def get_offers(
        self, request_data: NetworkRequestData
    ) -> List[Dict[str, Any]]: # Return type should be List of results from _get_offer
        
        payload = VerbynDichRequestData.from_address(request_data.address)
        tasks = []
        # Create a semaphore to limit the number of concurrent requests
        semaphore = asyncio.Semaphore(self.CONCURRENCY_LIMIT)
        
        async with aiohttp.ClientSession() as session:
            for page in range(0, self.MAX_PAGE):
                tasks.append(self._get_offer_with_semaphore(session, payload=payload, page=page, semaphore=semaphore))

            results = await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions=True is good for debugging

        # Process results, filter out exceptions if any
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                self._logger.error(f"Error in _get_offer task: {result}", exc_info=result)
            elif result:
                processed_results.append(result)
        return processed_results

    async def _get_offer_with_semaphore(
        self, session: aiohttp.ClientSession, payload: VerbynDichRequestData, page: int, semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        async with semaphore: # This will wait if too many tasks are already running
            self._logger.debug(f"Semaphore acquired for page {page}")
            try:
                return await self._get_offer(session, payload, page)
            finally:
                self._logger.debug(f"Semaphore released for page {page}")

    async def _get_offer(
        self, session: aiohttp.ClientSession, payload: VerbynDichRequestData, page: int = 0
    ) -> Dict[str, Any]:
        settings = get_settings()

        query_params = VerbynDichQueryParams(
            api_key=settings.VERBYNDICH_API_KEY,
            page=page
        ).model_dump(by_alias=True)
        
        await asyncio.sleep(0.1)

        try:
            self._logger.info(f"Requesting VerbynDich page {page}...")
            async with session.post(
                settings.VERBYNDICH_URL,
                data=payload.body,
                params=query_params,
                timeout=aiohttp.ClientTimeout(total=10) # 10 seconds total timeout
            ) as response:
                self._logger.debug(f"VerbynDich page {page} - Status: {response.status}, Headers: {response.headers}")
                
                if response.status == 429:
                    ...
                    # TODO: use tenacity to retry after a delay
                    
                raw_response_json = await response.json() # This might fail if response is not JSON (e.g. on 429 if not caught above)
                self._logger.debug(f"VerbynDich page {page} - Raw response: {raw_response_json}")

                response.raise_for_status() 

                return self.normalize_offer(raw_response_json)

        except aiohttp.ClientResponseError as e: 
            # Log the response text if available, especially for 429 if not handled above
            response_text_on_error = raw_response_json if raw_response_json else "N/A"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    response_text_on_error = await e.response.text()
                except Exception:
                    pass # Ignore if can't read text
            self._logger.error(f"HTTP error for {self.provider_name()} API, page {page}: {e.status} {e.message}. Response text: {response_text_on_error}", exc_info=False)
            return {}
        except aiohttp.ClientError as e: 
            self._logger.exception(f"AIOHTTP ClientError for {self.provider_name()} API, page {page}", exc_info=e)
            return {}
        except Exception as e:
            self._logger.exception(f"Unexpected error in _get_offer for {self.provider_name()}, page {page}", exc_info=e)
            return {}
        

    def normalize_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        # TODO: Implement the normalization logic.
        # For now, just returning a placeholder
        self._logger.debug(f"Normalizing raw offer for {self.provider_name()}: {raw_offer}...")
        if not raw_offer:
            return {}
        return raw_offer
        
