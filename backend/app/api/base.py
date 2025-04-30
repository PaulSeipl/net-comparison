from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..schemas import Address

class BaseProvider(ABC):
    # Make circuit_breaker a class attribute so it can be used as a decorator
    #circuit_breaker = circuit_breaker
    
    def __init__(self, db):
        self.db = db
        #self.cache = CacheService(db)
        #self.circuit_breaker = CircuitBreaker(self.provider_name, db)
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
    
    @abstractmethod
    async def get_offers(self, address: Address) -> List[Dict[str, Any]]:
        """
        Fetch offers from the provider for the given address.
        Returns a list of normalized offer data.
        """
        pass
    
    @abstractmethod
    def normalize_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        pass
    
    async def get_cached_offers(self) -> List[Dict[str, Any]]:
        """
        Get offers from cache if available and valid.
        """
        return
        return await self.cache.get_cached_offers(self.provider_name)
    
    async def _cache_offer(self, raw_offer: Dict[str, Any], normalized_offer: Dict[str, Any]):
        """
        Cache the offer in the database.
        """
        return
        await self.cache.cache_offer(
            self.provider_name,
            normalized_offer["offer_id"],
            raw_offer,
            normalized_offer
        )
    
    def _create_normalized_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a normalized offer with common fields.
        """
        normalized = self.normalize_offer(raw_offer)
        return {
            "provider": self.provider_name,
            "offer_id": normalized.get("offer_id"),
            "download_speed": normalized.get("download_speed"),
            "upload_speed": normalized.get("upload_speed"),
            "price": normalized.get("price"),
            "contract_length": normalized.get("contract_length"),
            "setup_fee": normalized.get("setup_fee"),
            "cancellation_fee": normalized.get("cancellation_fee"),
            "provider_specific": normalized.get("provider_specific", {}),
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    def _validate_address(self, address: str) -> bool:
        """
        Validate the address format.
        """
        parts = address.split(";")
        return len(parts) == 4  # street;house number;city;plz
    
    def _format_address(self, address: str) -> str:
        """
        Format the address according to provider requirements.
        """
        if not self._validate_address(address):
            raise ValueError("Invalid address format. Expected: street;house number;city;plz")
        return address.strip() 