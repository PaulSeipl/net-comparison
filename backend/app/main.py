import logfire
from fastapi import FastAPI
from .schemas import (
    Provider,
    ProviderEnum,
)
from .config import get_settings

app = FastAPI()

logfire.configure()
logfire.instrument_fastapi(app, capture_headers=True)

providers = {
    ProviderEnum.WEBWUNDER: 'placeholder',
    # Add other providers here
}


@app.get("/", response_model=dict[str, str])
async def root():
    return {"message": "Internet Provider Comparison API"}

@app.get("/providers", response_model=list[ProviderEnum])
async def get_providers():
    return list(providers.keys())