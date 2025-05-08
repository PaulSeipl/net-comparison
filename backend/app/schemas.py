from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from abc import ABC, abstractmethod


class Address(BaseModel):
    street: str = Field(..., example=" Musterstraße")
    house_number: str = Field(..., example="5")
    zip: int = Field(..., example="80333", ge=10000, le=99999)
    city: str = Field(..., example="München")
    country_code: str = Field(..., example="DE")

    @field_validator("zip")
    def validate_zip(cls, value):
        if len(str(value)) != 5:
            raise ValueError("ZIP code must be exactly 5 digits")
        return value


class NetworkRequestData(BaseModel):
    installation: bool = Field(..., example=True)
    connection_type: Literal["DSL", "CABLE", "FIBER", "MOBILE"] = Field(
        ..., example="DSL"
    )
    address: Address


class ApiRequestHeaders(BaseModel):
    content_type: str = Field("text/xml; charset=utf-8", alias="Content-Type")
    x_api_key: str = Field(..., alias="X-Api-Key")

    class Config:
        validate_by_name = True


class ByteMeQueryParams(BaseModel):
    street: str = Field(..., example="Musterstraße")
    house_number: str = Field(..., example="5", alias="houseNumber")
    city: str = Field(..., example="München")
    plz: int = Field(..., example=80333)

    class Config:
        validate_by_name = True


class PingPerfectHeaders(BaseModel):
    x_client_id: str = Field(..., alias="X-Client-Id")
    x_signature: str = Field(..., alias="X-Signature")
    x_timestamp: str = Field(..., alias="X-Timestamp")
    content_type: str = Field("application/json", alias="Content-Type")

    class Config:
        validate_by_name = True


class PingPerfectRequestData(BaseModel):
    city: str = Field(..., example="München")
    house_number: str = Field(..., example="5", alias="houseNumber")
    plz: int = Field(..., example=80333)
    street: str = Field(..., example="Musterstraße")
    wants_fiber: bool = Field(False, alias="wantsFiber")

    class Config:
        validate_by_name = True


class PingPerfectProductInfo(BaseModel):
    speed: int = Field(..., example=30)
    contract_duration_in_months: int = Field(..., alias="contractDurationInMonths")
    connection_type: Literal["DSL", "CABLE", "FIBER", "MOBILE"] = Field(
        ..., example="DSL"
    )
    tv: str = Field(..., example="PING TV")
    limit_from: Optional[str] = Field(None, alias="limitFrom")
    max_age: Optional[str] = Field(None, alias="maxAge")

    class Config:
        validate_by_name = True


class PingPerfectPricingDetails(BaseModel):
    monthly_cost_in_cent: int = Field(..., alias="monthlyCostInCent")
    installation_service: str = Field(..., example="no", alias="installationService")

    class Config:
        validate_by_name = True


class PingPerfectResponseData(BaseModel):
    provider_name: str = Field(..., alias="providerName")
    product_info: PingPerfectProductInfo = Field(..., alias="productInfo")
    pricing_details: PingPerfectPricingDetails = Field(..., alias="pricingDetails")

    class Config:
        validate_by_name = True


class ProviderEnum(str, Enum):
    WEBWUNDER = "WebWunder"
    BYTEME = "ByteMe"
    PINGPERFECT = "Ping Perfect"
    VERBYNDICH = "VerbynDich"
    SERVUSSPEED = "Servus Speed"


class BaseProvider(BaseModel, ABC):
    # Make circuit_breaker a class attribute so it can be used as a decorator
    # circuit_breaker = circuit_breaker
    #    db: str
    name: ProviderEnum

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def get_offers(self, address: Address) -> List[Dict[str, Any]]:
        """
        Fetch offers from the provider for the given address.
        Returns a list of normalized offer data.
        """
        pass

    @abstractmethod
    def normalize_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        pass

    async def get_cached_offers(self) -> List[Dict[str, Any]]:
        """
        Get offers from cache if available and valid.
        """
        return
        return await self.cache.get_cached_offers(self.provider_name)

    async def _cache_offer(
        self, raw_offer: Dict[str, Any], normalized_offer: Dict[str, Any]
    ):
        """
        Cache the offer in the database.
        """
        return
        await self.cache.cache_offer(
            self.provider_name,
            normalized_offer["offer_id"],
            raw_offer,
            normalized_offer,
        )

    def _create_normalized_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a normalized offer with common fields.
        """
        normalized = self.normalize_offer(raw_offer)
        return {
            "provider": self.provider_name,
            "offer_id": normalized.get("offer_id"),
            "download_speed": normalized.get("download_speed"),
            "upload_speed": normalized.get("upload_speed"),
            "price": normalized.get("price"),
            "contract_length": normalized.get("contract_length"),
            "setup_fee": normalized.get("setup_fee"),
            "cancellation_fee": normalized.get("cancellation_fee"),
            "provider_specific": normalized.get("provider_specific", {}),
            "fetched_at": datetime.utcnow().isoformat(),
        }


# class Provider(BaseModel):
#     {ProviderEnum}: BaseProvider
