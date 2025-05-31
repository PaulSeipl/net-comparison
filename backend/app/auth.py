"""
Authentication module for API key validation using FastAPI security.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import get_settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create API Key security scheme
# This will automatically add the security scheme to OpenAPI docs
api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="API key required for authentication"
)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the X-API-Key header.
    
    Args:
        api_key: The API key from the header
        
    Returns:
        str: The verified API key
        
    Raises:
        HTTPException: If the API key is invalid or missing
    """
    settings = get_settings()
    
    # Compare with the configured API key
    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
    
    logger.debug("API key validation successful")
    return api_key