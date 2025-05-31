# API Authentication Guide

This API uses API key authentication via the `X-API-Key` header.

## Setup

1. **Configure your API key** in the `.env` file:
   ```bash
   API_KEY=your-secret-api-key-here
   ```

2. **Copy the example environment file** and update it with your settings:
   ```bash
   cp .env.example .env
   ```

## Usage

### Making Authenticated Requests

Include the API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secret-api-key-here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/providers
```

### Public Endpoints (No Authentication Required)

- `GET /api/v1/` - API root endpoint
- `GET /docs` - Swagger documentation
- `GET /redoc` - ReDoc documentation

### Protected Endpoints (Authentication Required)

All provider-related endpoints require authentication:

- `GET /api/v1/providers` - Get list of available providers
- `POST /api/v1/providers/offers` - Get offers from all providers
- `POST /api/v1/providers/offers/{provider}` - Get offers from specific provider

## Example Requests

### JavaScript/Fetch
```javascript
const response = await fetch('http://localhost:8000/api/v1/providers', {
  headers: {
    'X-API-Key': 'your-secret-api-key-here',
    'Content-Type': 'application/json'
  }
});
```

### Python/Requests
```python
import requests

headers = {
    'X-API-Key': 'your-secret-api-key-here',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/v1/providers', headers=headers)
```

### cURL
```bash
curl -H "X-API-Key: your-secret-api-key-here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/providers
```

## Error Responses

### 401 Unauthorized
When API key is missing or invalid:
```json
{
  "detail": "Missing X-API-Key header"
}
```

```json
{
  "detail": "Invalid API key"
}
```

## Security Best Practices

1. **Keep your API key secret** - never commit it to version control
2. **Use environment variables** to store the API key
3. **Rotate keys regularly** for production use
4. **Use HTTPS** in production to encrypt the API key header
5. **Implement rate limiting** for production deployments

## FastAPI Security Integration

This implementation uses FastAPI's built-in `APIKeyHeader` security class, which provides:

- **Automatic OpenAPI documentation** - The security scheme appears in `/docs` with an "Authorize" button
- **Built-in validation** - FastAPI automatically validates the presence of the header
- **Dependency injection** - Clean integration with FastAPI's dependency system
- **Type safety** - Full type hints and IDE support
- **Flexibility** - Easy to switch between different authentication methods

### Alternative: Bearer Token Authentication

If you prefer using `Authorization: Bearer` headers instead of `X-API-Key`, you can use the example in `app/auth_bearer_example.py` which uses `HTTPBearer` security class.

## Testing

Use the provided test script to verify authentication:

```bash
python test_api_auth.py
```

Make sure to update the `API_KEY` variable in the script with your actual key.
