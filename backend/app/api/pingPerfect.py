from datetime import datetime
from pydantic import PrivateAttr
from app.schemas import (
    NormalizedOffer,
    PingPerfectProduct,
    PingPerfectRequestData,
    PingPerfectHeaders,
    PriceDetails,
    ProviderEnum,
    NetworkRequestData,
    BaseProvider,
)
from app.utils.connection_mapper import ConnectionTypeMapper
from app.config import get_settings
from typing import Any
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
    BASE_URL: str = 'https://pingperfect.gendev7.check24.fun/internet/angebote/data'
    
    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger
        
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
        for product in response_data:
            processed_results.append(self.normalize_offer(product))
            
        self._logger.info(f"Successfully fetched {len(processed_results)} offers")
        return processed_results    
    
    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type(aiohttp.ClientResponseError)
    )
    async def _fetch_products(
        self,
        session: aiohttp.ClientSession,
        payload: str,
    ) -> list[PingPerfectProduct]:
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
                self.BASE_URL,
                data=payload,
                timeout=aiohttp.ClientTimeout(total=self.REQUEST_TIMEOUT),
            ) as response:
                self._logger.debug(f"Offers - Status: {response.status}")
                
                if response.status != 200:
                    self._logger.error(f"Failed to fetch offers: {response.status}")
                    response.raise_for_status()
                
                response_data = await response.json()
                self._logger.debug(f"Raw response data: {response_data}")

                return [PingPerfectProduct(**data) for data in response_data]

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
            
    def normalize_offer(self, raw_offer: PingPerfectProduct) -> NormalizedOffer:
        """
        Normalize the provider-specific offer format into a common format.
        
        Args:
            product: The product data dictionary
            
        Returns:
            A normalized offer dictionary
        """
        self._logger.debug(f"Normalizing raw offer: {raw_offer}")

        price_details = PriceDetails(
            monthly_cost=raw_offer.pricing_details.monthly_cost_in_cent,
        )

        normalized_offer = NormalizedOffer(
            provider=self.name,
            offer_id=self._generate_offer_id(raw_offer.provider_name),
            name=raw_offer.provider_name,
            speed=raw_offer.product_info.speed,
            connection_type=ConnectionTypeMapper.map_connection_type(raw_offer.product_info.connection_type),
            price_details=price_details,
            contract_duration=raw_offer.product_info.contract_duration_in_months,
            installation_service=raw_offer.pricing_details.installation_service,
            tv_service=raw_offer.product_info.tv,
            max_age=raw_offer.product_info.max_age,
            data_limit=raw_offer.product_info.limit_from,
            fetched_at=datetime.now().isoformat(timespec="seconds"),
        )
        
        return normalized_offer
    
    def _generate_offer_id(self, product_name: str) -> str:
        return f"{self.name}_{product_name}"

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
            wants_fiber=False, # Always False to get all products
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
