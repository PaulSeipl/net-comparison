"""
WebWunder provider configuration and constants.
"""
from typing import List


class WebWunderConfig:
    """Configuration constants for WebWunder provider."""
    
    BASE_URL: str = 'https://webwunder.gendev7.check24.fun:443/endpunkte/soap/ws'
    
    # API Configuration
    REQUEST_TIMEOUT: int = 10  # Request timeout in seconds
    CONCURRENCY_LIMIT: int = 5  # Limit concurrent requests
    
    # Business Logic Constants
    PROMOTION_LENGTH: int = 24  # Promotional period length in months
    
    # Supported connection types (API format)
    CONNECTION_TYPES: List[str] = [
        "DSL",
        "CABLE", 
        "FIBER",
        "MOBILE",
    ]
    
    # Installation service options
    INSTALLATION_SERVICE_OPTIONS: List[bool] = [True, False]
    
    # Retry Configuration
    MAX_RETRY_ATTEMPTS: int = 10
    RETRY_MIN_WAIT: int = 2
    RETRY_MAX_WAIT: int = 60
    RETRY_MULTIPLIER: int = 1
