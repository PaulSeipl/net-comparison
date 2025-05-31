from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # API Authentication
    API_KEY: str
    
    # Provider API configurations
    WEBWUNDER_API_KEY: str
    BYTEME_API_KEY: str
    PINGPERFECT_CLIENT_ID: str
    PINGPERFECT_SIGNATURE_SECRET: str
    VERBYNDICH_API_KEY: str
    SERVUSSPEED_USERNAME: str
    SERVUSSPEED_PASSWORD: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

@lru_cache()
def get_settings() -> Settings:
    return Settings()