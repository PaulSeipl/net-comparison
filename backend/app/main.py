#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from typing import Any, List, Dict, Tuple
import logfire
from fastapi import FastAPI
import uvicorn
from app.schemas import (
    Provider,
    ProviderEnum,
    WebWunderRequestData,
)
from app.api import WebWunder, ByteMe
from app.config import get_settings

app = FastAPI()

#logfire.configure()
#logfire.instrument_fastapi(app, capture_headers=True)

providers = {
    ProviderEnum.WEBWUNDER: WebWunder('db'),
    ProviderEnum.BYTEME: ByteMe('db')
    # Add other providers here
}


@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "Internet Provider Comparison API"}

@app.get("/providers", response_model=list[ProviderEnum])
async def get_providers():
    return list(providers.keys())

@app.post('/providers/offers', response_model=List[Tuple[ProviderEnum, List[Dict[str, Any]]]])
async def get_offers(request_data: WebWunderRequestData):
    offers = []
    
    for provider_name, provider in providers.items():
        offer = await provider.get_offers(request_data=request_data)
        offers.append((provider_name, offer))
        
    return offers

@app.post('/providers/offers/byteme', response_model=List[Dict[str, Any]])
async def get_offers(request_data: WebWunderRequestData):
    offers = await providers[ProviderEnum.BYTEME].get_offers(request_data=request_data)
    
    print(offers)
    return offers

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000, env_file='.env')