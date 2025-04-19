from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Address(BaseModel):
    street: str = Field(min_length=1, description="Street name")
    house_number: str = Field(min_length=1, description="House number")
    city: str = Field(min_length=1, description="City name")
    postal_code: str = Field(min_length=4, max_length=10, description="Postal code")

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v):
        if not v.isdigit():
            raise ValueError('Postal code must contain only digits')
        return v

    def to_string(self) -> str:
        """Convert address to the format required by providers: street;house number;city;plz"""
        return f"{self.street};{self.house_number};{self.city};{self.postal_code}"

class ProviderType(str, Enum):
    WEBWUNDER = "webwunder"
    BYTEME = "byteme"
    PINGPERFECT = "pingperfect"
    VERBYNDICH = "verbyndich"
    SERVUSSPEED = "servusspeed"

class ProviderSpecific(BaseModel):
    technology: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    availability: Optional[str] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)

class InternetOffer(BaseModel):
    provider: ProviderType
    offer_id: str
    download_speed: float = Field(gt=0, description="Download speed in Mbps")
    upload_speed: float = Field(gt=0, description="Upload speed in Mbps")
    price: float = Field(gt=0, description="Monthly price in EUR")
    contract_length: int = Field(gt=0, description="Contract length in months")
    setup_fee: float = Field(ge=0, description="Setup fee in EUR")
    cancellation_fee: float = Field(ge=0, description="Cancellation fee in EUR")
    provider_specific: ProviderSpecific = Field(default_factory=ProviderSpecific)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

class OfferResponse(BaseModel):
    total_offers: int = Field(ge=0)
    offers: List[InternetOffer]
    cached: bool = Field(default=False)
    providers_used: List[ProviderType]

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    provider: Optional[ProviderType] = None

class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    providers_status: Dict[ProviderType, bool] 