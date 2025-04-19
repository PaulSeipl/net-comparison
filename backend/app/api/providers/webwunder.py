from typing import Dict, List, Any
import zeep
from zeep import Client
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from ...core.config import get_settings
from ...schemas import ProviderType, ProviderSpecific
from .base import BaseProvider
from datetime import datetime
import asyncio

settings = get_settings()

class WebWunderProvider(BaseProvider):
    @property
    def provider_name(self) -> str:
        return ProviderType.WEBWUNDER
    
    def __init__(self, db):
        super().__init__(db)
        self.client = self._create_client()
    
    def _create_client(self) -> Client:
        wsdl = f"{settings.WEBWUNDER_BASE_URL}/wsdl"
        transport = Transport()
        return Client(
            wsdl=wsdl,
            transport=transport,
            wsse=UsernameToken(settings.WEBWUNDER_API_KEY)
        )
    
    @BaseProvider.circuit_breaker
    async def get_offers(self, address: str) -> List[Dict[str, Any]]:
        formatted_address = self._format_address(address)
        street, house_number, city, plz = formatted_address.split(";")
        
        try:
            # SOAP clients are typically synchronous, wrap in run_in_executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.service.GetOffers(
                    street=street,
                    houseNumber=house_number,
                    city=city,
                    postalCode=plz
                )
            )
            
            offers = []
            for raw_offer in response.offers:
                normalized_offer = self.normalize_offer(raw_offer)
                await self._cache_offer(raw_offer, normalized_offer)
                offers.append(normalized_offer)
            
            return offers
        
        except Exception as e:
            await self.cache.record_fetch_error(
                self.provider_name,
                "unknown",
                str(e)
            )
            raise
    
    def normalize_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize WebWunder's SOAP response into a common format.
        """
        provider_specific = ProviderSpecific(
            technology=raw_offer.get("technology"),
            features=raw_offer.get("features", []),
            availability=raw_offer.get("availability"),
            additional_info={}
        )
        
        return {
            "provider": self.provider_name,
            "offer_id": raw_offer.get("id"),
            "download_speed": float(raw_offer.get("downloadSpeed", 0)),
            "upload_speed": float(raw_offer.get("uploadSpeed", 0)),
            "price": float(raw_offer.get("monthlyPrice", 0)),
            "contract_length": int(raw_offer.get("contractLength", 24)),
            "setup_fee": float(raw_offer.get("setupFee", 0)),
            "cancellation_fee": float(raw_offer.get("cancellationFee", 0)),
            "provider_specific": provider_specific.model_dump(),
            "fetched_at": datetime.utcnow().isoformat()
        } 