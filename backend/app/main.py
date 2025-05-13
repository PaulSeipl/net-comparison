from typing import Any, List, Dict, Tuple
import logfire
from fastapi import Depends, FastAPI
import uvicorn
from app.schemas import (
    ProviderEnum,
    NetworkRequestData,
    BaseProvider
)
from app.dependencies.providers import get_all_providers, make_provider_getter
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
# logfire.configure()
# logfire.instrument_fastapi(app, capture_headers=True)


@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "Internet Provider Comparison API"}


@app.get("/providers", response_model=list[ProviderEnum])
async def get_providers(
    providers: Dict[ProviderEnum, BaseProvider] = get_all_providers(),
):
    """
    Get a list of all available providers.
    """
    return list(providers.keys())


@app.post(
    "/providers/offers", response_model=List[Tuple[ProviderEnum, List[Dict[str, Any]]]]
)
async def get_offers(
    request_data: NetworkRequestData,
    providers: Dict[ProviderEnum, BaseProvider] = Depends(get_all_providers),
):
    offers = []

    for provider_name, provider in providers.items():
        offer = await provider.get_offers(request_data=request_data)
        offers.append((provider_name, offer))

    return offers


@app.post("/providers/offers/byteme", response_model=List[Dict[str, Any]])
async def get_offers(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.BYTEME)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


@app.post("/providers/offers/webwunder", response_model=List[Dict[str, Any]])
async def get_offers(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.WEBWUNDER)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


@app.post("/providers/offers/pingperfect", response_model=List[Dict[str, Any]])
async def get_offers(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.PINGPERFECT)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


@app.post("/providers/offers/verbynDich", response_model=List[Dict[str, Any]])
async def get_offers(
    request_data: NetworkRequestData,
    provider: BaseProvider = Depends(make_provider_getter(ProviderEnum.VERBYNDICH)),
):
    offers = await provider.get_offers(request_data=request_data)

    print(offers)
    return offers


# if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000, env_file='.env')
