from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any, Optional, Annotated
import asyncio
from .core.config import get_settings
from .db.models import Base
from .api.providers.webwunder import WebWunderProvider
from .schemas import (
    Address,
    ProviderType,
    OfferResponse,
    ErrorResponse,
    HealthCheck,
    InternetOffer
)
# Import other providers here

settings = get_settings()

# Database setup
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Internet Provider Comparison API",
    description="API for comparing internet provider offers from multiple sources",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Provider instances
providers = {
    ProviderType.WEBWUNDER: WebWunderProvider,
    # Add other providers here
}

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "Internet Provider Comparison API"}

@app.get("/providers", response_model=List[ProviderType])
async def get_providers():
    return list(providers.keys())

@app.get("/offers", response_model=OfferResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_offers(
    street: str = Query(..., description="Street name"),
    house_number: str = Query(..., description="House number"),
    city: str = Query(..., description="City name"),
    postal_code: str = Query(..., description="Postal code"),
    provider: Optional[ProviderType] = Query(None, description="Specific provider to query"),
    db: AsyncSession = Depends(get_db)
) -> OfferResponse:
    """
    Get offers from all providers or a specific provider for the given address.
    """
    try:
        # Create Address model from query params
        address = Address(
            street=street,
            house_number=house_number,
            city=city,
            postal_code=postal_code
        )
        
        # Get offers from specified provider or all providers
        selected_providers = [provider] if provider else list(providers.keys())
        
        # Try to get cached offers first
        all_offers: List[InternetOffer] = []
        providers_to_fetch = []
        providers_used: List[ProviderType] = []
        
        for provider_name in selected_providers:
            if provider_name not in providers:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid provider: {provider_name}"
                )
            
            provider_instance = providers[provider_name](db)
            cached_offers = await provider_instance.get_cached_offers()
            
            if cached_offers:
                all_offers.extend([InternetOffer.model_validate(offer) for offer in cached_offers])
                providers_used.append(provider_name)
            else:
                providers_to_fetch.append((provider_instance, provider_name))
        
        # Fetch fresh offers from providers without cache
        if providers_to_fetch:
            tasks = [
                provider.get_offers(address.to_string())
                for provider, _ in providers_to_fetch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for idx, provider_offers in enumerate(results):
                provider_name = providers_to_fetch[idx][1]
                if isinstance(provider_offers, Exception):
                    # Log the error but continue with other providers
                    print(f"Error fetching offers from {provider_name}: {str(provider_offers)}")
                    continue
                
                all_offers.extend([InternetOffer.model_validate(offer) for offer in provider_offers])
                providers_used.append(provider_name)
        
        return OfferResponse(
            total_offers=len(all_offers),
            offers=all_offers,
            cached=len(providers_to_fetch) == 0,
            providers_used=providers_used
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Check the health status of the API and all providers.
    """
    providers_status = {
        provider: True for provider in providers.keys()
    }
    
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        providers_status=providers_status
    ) 