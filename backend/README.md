# Backend - Internet Provider Comparison API

This directory contains the FastAPI backend service for the Internet Provider Comparison application. It fetches offers from multiple provider SOAP/REST APIs, normalizes and aggregates them.

## Challenge

Build a resilient API aggregator that handles unreliable third-party provider APIs (WebWunder, ByteMe, Ping Perfect, VerbynDich, Servus Speed) while ensuring smooth user experience. Given an address, fetch offers from all providers in parallel, handle failures gracefully, normalize heterogeneous data formats, and return unified results.

## Solution Approach


1. **Individual Provider Resilience**: Each provider class has proper retry logic with exponential backoff (tenacity library), semaphore-based concurrency limiting, and timeout controls.

2. **Data Normalization**: Solid pipeline from raw provider responses → parsed objects → standardized `NormalizedOffer` schema with unified pricing/speeds.

3. **Individual Provider Endpoints**: `/providers/offers/{provider}` endpoints work well for testing single providers and multiple calls.

**Critical Issues:**

## Implementation Details

**Provider Pattern**: Each provider (`app/api/`) implements:
```python
class Provider(BaseProvider):
    async def get_offers(self, request_data: NetworkRequestData) -> List[NormalizedOffer]:
        # Fetch, parse, normalize
```

**Retry & Circuit Breaking**: Using tenacity for exponential backoff:
```python
@retry(stop=stop_after_attempt(10), wait=wait_exponential(min=2, max=60))
async def _fetch_products_with_semaphore(self, ...):
```

**Concurrency Control**: Semaphores prevent API overload:
```python
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests per provider
```

**Data Normalization**: All providers output standardized `NormalizedOffer` objects with:
- Unified pricing (cents), speeds (Mbps), connection types
- Discount calculations via `DiscountCalculator`
- Connection type mapping via `ConnectionTypeMapper`

## Architecture
- **FastAPI** application with async/await throughout
- Provider implementations (`app/api/`) inheriting from `BaseProvider` 
- **Pydantic** schemas for strict data validation and normalization
- **aiohttp** for async HTTP with **tenacity** retry mechanisms
- XML/JSON parsing utilities (`app/utils/xml_parser.py`)
- Business logic utilities (discount calculation, connection type mapping)
- Dependency injection pattern for provider management
- API key authentication with CORS for frontend integration

## Getting Started

1. **Setup Environment**:
   ```pwsh
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure API Keys** (copy `.env.example` to `.env`):
   ```env
   WEBWUNDER_API_KEY=your_key_here
   BYTE_ME_API_KEY=your_key_here
   PING_PERFECT_CLIENT_ID=your_id_here
   PING_PERFECT_SIGNATURE_SECRET=your_secret_here
   VERBYNDICH_API_KEY=your_key_here
   SERVUSSPEED_USERNAME=your_username_here
   SERVUSSPEED_PASSWORD=your_password_here
   FRONTEND_URL=http://localhost:5173
   API_KEY=your_frontend_api_key
   ```

3. **Run Development Server**:
   ```pwsh
   fastapi .\app\main.py dev
   ```
   API available at `http://localhost:8000/api/v1`

4. **Test Individual Providers**:
   ```pwsh
   curl -X POST "http://localhost:8000/api/v1/providers/offers/webWunder" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"address": {"street": "Musterstraße", "house_number": "5", "zip": 80333, "city": "München", "country_code": "DE"}}'
   ```

   or goto [SwaggerUI](http://localhost:8000/docs)

## Development Guide

**Adding New Providers**:
1. Create `app/api/new_provider.py` inheriting from `BaseProvider`
2. Add to `ProviderEnum` in `schemas.py`
3. Register in `dependencies/providers.py`
4. Add endpoint in `main.py`

**Key Files**:
- `app/main.py`: FastAPI app and endpoints
- `app/schemas.py`: Pydantic models and validation
- `app/api/`: Provider implementations
- `app/utils/`: Business logic (discounts, parsing, mapping)
- `app/dependencies/`: Dependency injection setup

***Testing**

- Big Todo :)

**Debugging**: Set logging level in individual provider files for detailed API interaction logs.
