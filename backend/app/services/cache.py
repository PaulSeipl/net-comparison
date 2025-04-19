from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.models import ProviderOffer
from ..core.config import get_settings

settings = get_settings()

class CacheService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _is_cache_valid(self, offer: ProviderOffer) -> bool:
        if not offer.cache_expires_at:
            return False
        return datetime.utcnow() < offer.cache_expires_at
    
    async def get_cached_offers(self, provider_name: str) -> List[Dict[str, Any]]:
        query = select(ProviderOffer).where(
            ProviderOffer.provider_name == provider_name,
            ProviderOffer.is_active == True,
            ProviderOffer.fetch_status == "success"
        )
        result = await self.db.execute(query)
        offers = result.scalars().all()
        
        valid_offers = [offer for offer in offers if self._is_cache_valid(offer)]
        return [offer.normalized_data for offer in valid_offers]
    
    async def cache_offer(self, provider_name: str, offer_id: str, raw_data: Dict[str, Any], normalized_data: Dict[str, Any]):
        cache_expires_at = datetime.utcnow() + timedelta(seconds=settings.CACHE_TTL)
        
        query = select(ProviderOffer).where(
            ProviderOffer.provider_name == provider_name,
            ProviderOffer.offer_id == offer_id
        )
        result = await self.db.execute(query)
        offer = result.scalar_one_or_none()
        
        if offer:
            offer.raw_data = raw_data
            offer.normalized_data = normalized_data
            offer.cache_expires_at = cache_expires_at
            offer.last_fetched = datetime.utcnow()
            offer.fetch_status = "success"
        else:
            offer = ProviderOffer(
                provider_name=provider_name,
                offer_id=offer_id,
                raw_data=raw_data,
                normalized_data=normalized_data,
                cache_expires_at=cache_expires_at,
                last_fetched=datetime.utcnow(),
                fetch_status="success",
                is_active=True
            )
            self.db.add(offer)
        
        await self.db.commit()
    
    async def mark_offer_inactive(self, provider_name: str, offer_id: str):
        query = select(ProviderOffer).where(
            ProviderOffer.provider_name == provider_name,
            ProviderOffer.offer_id == offer_id
        )
        result = await self.db.execute(query)
        offer = result.scalar_one_or_none()
        
        if offer:
            offer.is_active = False
            await self.db.commit()
    
    async def record_fetch_error(self, provider_name: str, offer_id: str, error_message: str):
        query = select(ProviderOffer).where(
            ProviderOffer.provider_name == provider_name,
            ProviderOffer.offer_id == offer_id
        )
        result = await self.db.execute(query)
        offer = result.scalar_one_or_none()
        
        if offer:
            offer.fetch_status = "error"
            offer.last_fetched = datetime.utcnow()
        else:
            offer = ProviderOffer(
                provider_name=provider_name,
                offer_id=offer_id,
                fetch_status="error",
                last_fetched=datetime.utcnow(),
                is_active=False
            )
            self.db.add(offer)
        
        await self.db.commit() 