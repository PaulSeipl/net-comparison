from typing import Any
import logfire
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.schemas import (
    NormalizedOffer,
    ProviderEnum,
    NetworkRequestData,
    BaseProvider
)
from app.dependencies.providers import get_all_providers, make_provider_getter
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)
logger_uvicorn = logging.getLogger("uvicorn.error")
logger_uvicorn.propagate = False

api_v1_router = APIRouter(prefix="/api/v1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://localhost:8080",  # In case you use HTTPS later
        "https://127.0.0.1:8080"
    ],
    # allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# logfire.configure()
# logfire.instrument_fastapi(app, capture_headers=True)


@api_v1_router.get("/", response_model=dict[str, str])
async def root():
    return {"message": "Internet Provider Comparison API"}


@api_v1_router.get("/providers", response_model=list[ProviderEnum])
async def get_providers(
    providers: list[BaseProvider] = Depends(get_all_providers),
):
    """
    Get a list of all available providers.
    """
    return [provider.name for provider in providers]


@api_v1_router.post(
    "/providers/offers", response_model=list[NormalizedOffer]
)
async def get_offers(
    request_data: NetworkRequestData,
    providers: list[BaseProvider] = Depends(get_all_providers),
):
    offers = []

    for provider in providers:
        offer = await provider.get_offers(request_data=request_data)
        offers.append((offer))

    return offers


@api_v1_router.post("/providers/offers/byteMe", response_model=list[dict[str, Any]])
async def get_offers_byte_me(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.BYTEME)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


@api_v1_router.post("/providers/offers/webWunder", response_model=list[NormalizedOffer])
async def get_offers_web_wunder(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.WEBWUNDER)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


@api_v1_router.post("/providers/offers/pingPerfect", response_model=list[NormalizedOffer])
async def get_offers_ping_perfect(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.PINGPERFECT)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


@api_v1_router.post("/providers/offers/verbynDich", response_model=list[NormalizedOffer])
async def get_offers_verbyn_dich(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.VERBYNDICH)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


@api_v1_router.post("/providers/offers/servusSpeed", response_model=list[NormalizedOffer])
async def get_offers_servus_speed(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.SERVUSSPEED)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers

app.include_router(api_v1_router, tags=["API v1"])

# if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000, env_file='.env')
