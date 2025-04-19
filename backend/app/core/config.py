from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    
    # API Keys
    WEBWUNDER_API_KEY: str
    BYTEME_API_KEY: str
    PINGPERFECT_CLIENT_ID: str
    PINGPERFECT_SIGNATURE_SECRET: str
    VERBYNDICH_API_KEY: str
    SERVUSSPEED_USERNAME: str
    SERVUSSPEED_PASSWORD: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Settings
    API_TIMEOUT: int = 30  # seconds
    CACHE_TTL: int = 3600  # 1 hour in seconds
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60  # seconds
    
    # Provider URLs
    WEBWUNDER_BASE_URL: str = "https://api.webwunder.com"
    BYTEME_BASE_URL: str = "https://api.byteme.com"
    PINGPERFECT_BASE_URL: str = "https://api.pingperfect.com"
    VERBYNDICH_BASE_URL: str = "https://verbyndich.gendev7.check24.fun"
    SERVUSSPEED_BASE_URL: str = "https://api.servusspeed.com"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings() 