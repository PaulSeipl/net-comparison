from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import (
    NormalizedOffer,
    ProviderEnum,
    NetworkRequestData,
    BaseProvider
)
from app.dependencies.providers import get_all_providers, make_provider_getter
from app.auth import verify_api_key
import logging
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(debug=False)
#logger_uvicorn = logging.getLogger("uvicorn.error")
#logger_uvicorn.propagate = False

api_v1_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(verify_api_key)]  # Apply authentication to ALL routes in this router
)

settings = get_settings()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"{settings.FRONTEND_URL}",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*", "X-API-Key"],  # Allow X-API-Key header
)

@app.get("/", response_model=dict[str, str])
async def root():
    return {"message": "Internet Provider Comparison API"}


@api_v1_router.get("/providers", response_model=list[ProviderEnum])
async def get_providers(
    providers: list[BaseProvider] = Depends(get_all_providers),
):
    """
    Get a list of all available providers.
    Authentication is handled at router level.
    """
    return [provider.name for provider in providers]


@api_v1_router.post(
    "/providers/offers", response_model=list[NormalizedOffer]
)
async def get_offers(
    request_data: NetworkRequestData,
    providers: list[BaseProvider] = Depends(get_all_providers),
):
    """
    Get offers from all available providers.
    Authentication is handled at router level.
    """
    offers = []

    for provider in providers:
        offer = await provider.get_offers(request_data=request_data)
        offers.append((offer))
        
    # flatten list of offers
    offers = [offer for sublist in offers for offer in sublist]

    return offers


@api_v1_router.post("/providers/offers/byteMe", response_model=list[NormalizedOffer])
async def get_offers_byte_me(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.BYTEME)),
):
    """
    Get offers from ByteMe provider.
    Authentication is handled at router level.
    """
    offers = await provider.get_offers(request_data=request_data)

    return offers


@api_v1_router.post("/providers/offers/webWunder", response_model=list[NormalizedOffer])
async def get_offers_web_wunder(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.WEBWUNDER)),
):
    """
    Get offers from WebWunder provider.
    Authentication is handled at router level.
    """
    offers = await provider.get_offers(request_data=request_data)

    return offers


@api_v1_router.post("/providers/offers/pingPerfect", response_model=list[NormalizedOffer])
async def get_offers_ping_perfect(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.PINGPERFECT)),
):
    """
    Get offers from Ping Perfect provider.
    Authentication is handled at router level.
    """
    offers = await provider.get_offers(request_data=request_data)

    return offers


@api_v1_router.post("/providers/offers/verbynDich", response_model=list[NormalizedOffer])
async def get_offers_verbyn_dich(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.VERBYNDICH)),
):
    """
    Get offers from VerbynDich provider.
    Authentication is handled at router level.
    """
    offers = await provider.get_offers(request_data=request_data)

    return offers


@api_v1_router.post("/providers/offers/servusSpeed", response_model=list[NormalizedOffer])
async def get_offers_servus_speed(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.SERVUSSPEED)),
):
    """
    Get offers from Servus Speed provider.
    Authentication is handled at router level.
    """
    offers = await provider.get_offers(request_data=request_data)

    return offers

app.include_router(api_v1_router, tags=["API v1"])
