from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    WEBWUNDER_API_KEY: str
    WEBWUNDER_BASE_URL: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    

@lru_cache()
def get_settings() -> Settings:
    return Settings()