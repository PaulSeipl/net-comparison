from pydantic import PrivateAttr
from app.schemas import (
    PingPerfectRequestData,
    PingPerfectHeaders,
    ProviderEnum,
    NetworkRequestData,
    BaseProvider,
)
from app.config import get_settings
from typing import Dict, List, Any
import aiohttp
import logging
import time
import json
import hmac
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class PingPerfect(BaseProvider):
    """
    PingPerfect provider implementation.
    Handles fetching and processing of internet service offers from the PingPerfect provider.
    """
    name: str = ProviderEnum.PINGPERFECT.value
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
        
        settings = get_settings()
        current_timestamp = int(time.time())

        # Prepare request payload and headers
        payload = self._get_payload(request_data=request_data)
        payload_dict = payload.model_dump(by_alias=True)
        payload_as_json = json.dumps(
            payload_dict, ensure_ascii=False, separators=(",", ":")
        )
        payload_hashed = self._get_hashed_payload(
            payload_as_json, current_timestamp, settings.PINGPERFECT_SIGNATURE_SECRET
        )

        headers = self._get_headers(
            payload_hashed=payload_hashed,
            client_id=settings.PINGPERFECT_CLIENT_ID,
            current_timestamp=current_timestamp,
        ).model_dump(by_alias=True)

        async with aiohttp.ClientSession(headers=headers) as session:
            # Get all products in a single request
            response_data = await self._fetch_products(
                session=session,
                payload=payload_as_json,
            )
            
            if not response_data:
                self._logger.warning(f"No available products at the given address.")
                return []
            
            self._logger.info(f"Found products")
        
        # Process and normalize results
        processed_results = []
        # For PingPerfect, the response is already a list of products
        if isinstance(response_data, list):
            for product in response_data:
                processed_results.append(self.normalize_offer(product))
        else:
            # Handle case where response is a single product or has different structure
            processed_results.append(self.normalize_offer(response_data))
            
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
    ) -> Dict[str, Any]:
        """
        Fetch products from the PingPerfect provider.
        Automatically retries on certain errors with exponential backoff.
        
        Args:
            session: The aiohttp ClientSession to use for requests
            payload: The JSON payload for the request
            
        Returns:
            The JSON response data
        """
        settings = get_settings()
        
        try:
            self._logger.info(f"Fetching available products...")
            async with session.post(
                settings.PINGPERFECT_URL,
                data=payload,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(f"Offers - Status: {response.status}")
                
                if response.status != 200:
                    self._logger.error(f"Failed to fetch offers: {response.status}")
                    response.raise_for_status()
                
                response_data = await response.json()
                self._logger.debug(f"Raw response data: {response_data}")
                
                return response_data

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
            return {}
            
        except Exception as e:
            self._logger.exception(
                f"Unexpected error while fetching offers",
                exc_info=e,
            )
            return {}
            
    def normalize_offer(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        
        Args:
            product: The product data dictionary
            
        Returns:
            A normalized offer dictionary
        """
        self._logger.debug(f"Normalizing raw offer: {product}")
        if not product:
            return {}
        
        return product
        
    def _get_payload(self, request_data: NetworkRequestData) -> PingPerfectRequestData:
        """
        Create the payload for the API request.
        
        Args:
            request_data: The network request data containing address information
            
        Returns:
            A PingPerfectRequestData object
        """
        payload = PingPerfectRequestData(
            city=request_data.address.city,
            house_number=request_data.address.house_number,
            plz=request_data.address.zip,
            street=request_data.address.street,
            wants_fiber=request_data.connection_type == "FIBER",
        )

        return payload
        
    def _get_headers(
        self, payload_hashed: str, client_id: str, current_timestamp: int
    ) -> PingPerfectHeaders:
        """
        Create the headers for the API request.
        
        Args:
            payload_hashed: The hashed payload
            client_id: The client ID
            current_timestamp: The current timestamp
            
        Returns:
            A PingPerfectHeaders object
        """
        headers = PingPerfectHeaders(
            x_client_id=client_id,
            x_signature=payload_hashed,
            x_timestamp=str(current_timestamp),
            content_type="application/json",
        )

        return headers
        
    def _get_hashed_payload(
        self, payload_as_json: str, current_timestamp: int, secret: str
    ) -> str:
        """
        Hash the payload using HMAC with SHA256.
        
        Args:
            payload_as_json: The payload as a JSON string
            current_timestamp: The current timestamp
            secret: The signature secret
            
        Returns:
            The hashed payload as a hexadecimal string
        """
        json_and_timestamp = f"{current_timestamp}:{payload_as_json}"

        hashed_payload = hmac.new(
            key=secret.encode(),
            msg=json_and_timestamp.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hashed_payload
