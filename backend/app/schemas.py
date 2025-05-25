from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, validator
from abc import ABC, abstractmethod


class Address(BaseModel):
    street: str = Field(..., examples=[" Musterstraße"])
    house_number: str = Field(..., examples=["5"])
    zip: int = Field(..., examples=["80333"], ge=10000, le=99999)
    city: str = Field(..., examples=["München"])
    country_code: str = Field(..., examples=["DE"])

    @field_validator("zip")
    def validate_zip(cls, value):
        if len(str(value)) != 5:
            raise ValueError("ZIP code must be exactly 5 digits")
        return value


class NetworkRequestData(BaseModel):
    installation: bool = Field(..., examples=[True])
    connection_type: Literal["DSL", "CABLE", "FIBER", "MOBILE"] = Field(
        ..., examples=["DSL"]
    )
    address: Address


class ApiRequestHeaders(BaseModel):
    content_type: str = Field("text/xml; charset=utf-8", alias="Content-Type")
    x_api_key: str = Field(..., alias="X-Api-Key")

    class Config:
        validate_by_name = True


class WebWunderProduct(BaseModel):
    product_id: str = Field(..., alias="productId")
    provider_name: str = Field(..., alias="providerName")
    speed: str = Field(..., alias="speed")
    monthly_cost_in_cent: str = Field(..., alias="monthlyCostInCent")
    monthly_cost_in_cent_from_25th_month: str = Field(
        ..., alias="monthlyCostInCentFrom25thMonth"
    )
    contract_duration_in_months: str = Field(
        ..., alias="contractDurationInMonths"
    )
    connection_type: str = Field(
        ..., alias="connectionType"
    )

    # Convert string fields to int
    @field_validator(
        "speed",
        "monthly_cost_in_cent",
        "monthly_cost_in_cent_from_25th_month",
        "contract_duration_in_months",
    )
    @classmethod
    def parse_int(cls, value: str) -> int:
        return int(value) if value else 0

    class Config:
        validate_by_name = True
        json_encoders = {
            str: lambda v: v if v else None,  # Handle empty strings
        }
    
    class Config:
        validate_by_name = True


class ByteMeQueryParams(BaseModel):
    street: str = Field(..., examples=["Musterstraße"])
    house_number: str = Field(..., examples=["5"], alias="houseNumber")
    city: str = Field(..., examples=["München"])
    plz: int = Field(..., examples=[80333])

    class Config:
        validate_by_name = True


class ByteMeProduct(BaseModel):
    product_id: str = Field(..., alias="productId")
    provider_name: str = Field(..., alias="providerName")
    speed: str = Field(..., alias="speed")
    monthly_cost_in_cent: str = Field(..., alias="monthlyCostInCent")
    after_two_years_monthly_cost: str = Field(..., alias="afterTwoYearsMonthlyCost")
    duration_in_months: str = Field(..., alias="durationInMonths")
    connection_type: str = Field(..., alias="connectionType")
    installation_service: str = Field(..., alias="installationService")
    tv: str = Field(..., alias="tv")
    limit_from: str = Field(..., alias="limitFrom")
    max_age: str = Field(..., alias="maxAge")
    voucher_type: str = Field(..., alias="voucherType")
    voucher_value: str = Field(..., alias="voucherValue")

    # Convert string fields to int
    @field_validator(
        "speed",
        "monthly_cost_in_cent",
        "after_two_years_monthly_cost",
        "duration_in_months",
        "limit_from",
        "max_age",
        "voucher_value",
    )
    @classmethod
    def parse_int(cls, value: str) -> int:
        return int(value) if value else 0

    class Config:
        validate_by_name = True
        json_encoders = {
            str: lambda v: v if v else None,  # Handle empty strings
        }


class PingPerfectHeaders(BaseModel):
    x_client_id: str = Field(..., alias="X-Client-Id")
    x_signature: str = Field(..., alias="X-Signature")
    x_timestamp: str = Field(..., alias="X-Timestamp")
    content_type: str = Field("application/json", alias="Content-Type")

    class Config:
        validate_by_name = True


class PingPerfectRequestData(BaseModel):
    city: str = Field(..., examples=["München"])
    house_number: str = Field(..., examples=["5"], alias="houseNumber")
    plz: int = Field(..., examples=[80333])
    street: str = Field(..., examples=["Musterstraße"])
    wants_fiber: bool = Field(False, alias="wantsFiber")

    class Config:
        validate_by_name = True


class PingPerfectProductInfo(BaseModel):
    speed: int = Field(..., examples=[30])
    contract_duration_in_months: int = Field(..., alias="contractDurationInMonths")
    connection_type: Literal["DSL", "CABLE", "FIBER", "MOBILE"] = Field(
        ..., examples=["DSL"]
    )
    tv: str = Field(..., examples=["PING TV"])
    limit_from: Optional[str] = Field(None, alias="limitFrom")
    max_age: Optional[str] = Field(None, alias="maxAge")

    class Config:
        validate_by_name = True


class PingPerfectPricingDetails(BaseModel):
    monthly_cost_in_cent: int = Field(..., alias="monthlyCostInCent")
    installation_service: str = Field(..., examples=["no"], alias="installationService")

    class Config:
        validate_by_name = True


class PingPerfectResponseData(BaseModel):
    provider_name: str = Field(..., alias="providerName")
    product_info: PingPerfectProductInfo = Field(..., alias="productInfo")
    pricing_details: PingPerfectPricingDetails = Field(..., alias="pricingDetails")

    class Config:
        validate_by_name = True


class VerbynDichRequestData(BaseModel):
    body: str = Field(
        ..., description="Serialized address string: 'street;houseNumber;zip;city'"
    )

    @classmethod
    def from_address(cls, address: Address) -> "VerbynDichRequestData":
        """
        Creates a VerbynDichRequestData instance from an Address object.
        The body will contain the address formatted as required by VerbynDich.
        """
        # Formatting logic moved here
        formatted_address = (
            f"{address.street};{address.house_number};{address.city};{address.zip}"
        )
        return cls(body=formatted_address)


class VerbynDichQueryParams(BaseModel):
    api_key: str = Field(..., alias="apiKey")
    page: int = Field(0)

    class Config:
        validate_by_name = True
        



class ServusSpeedRequestAddress(BaseModel):
    street: str = Field(..., examples=["Musterstraße"], alias="strasse")
    house_number: str = Field(..., examples=["5"], alias="hausnummer")
    zip: int = Field(..., examples=[80333], alias="postleitzahl")
    city: str = Field(..., examples=["München"], alias="stadt")
    country_code: str = Field(..., examples=["DE"], alias="land")

    class Config:
        validate_by_name = True


class ServusSpeedRequestData(BaseModel):
    address: ServusSpeedRequestAddress


class ServusSpeedHeaders(BaseModel):
    content_type: str = Field("application/json", alias="Content-Type")
    accept: str = Field("*/*", alias="Accept")
    accept_encoding: str = Field("gzip, deflate, br", alias="Accept-Encoding")
    connection: str = Field("keep-alive", alias="Connection")

    class Config:
        validate_by_name = True


class ServusSpeedAvailableProducts(BaseModel):
    available_products: List[str] = Field(..., alias="availableProducts")

    class Config:
        validate_by_name = True


class ServusSpeedProductInfo(BaseModel):
    speed: int = Field(..., examples=[30])
    contract_duration_in_months: int = Field(..., alias="contractDurationInMonths")
    connection_type: Literal["DSL", "Cable", "Fiber"] = Field(
        ..., examples=["DSL"], alias="connectionType"
    )
    tv: Optional[str] = Field(..., examples=["PING TV"])
    limit_from: Optional[int] = Field(None, alias="limitFrom")
    max_age: Optional[int] = Field(None, alias="maxAge")

    class Config:
        validate_by_name = True


class ServusSpeedPricingDetails(BaseModel):
    monthly_cost_in_cent: int = Field(..., alias="monthlyCostInCent")
    installation_service: bool = Field(..., alias="installationService")

    class Config:
        validate_by_name = True


class ServusSpeedProduct(BaseModel):
    provider_name: str = Field(..., alias="providerName")
    product_info: ServusSpeedProductInfo = Field(..., alias="productInfo")
    pricing_details: ServusSpeedPricingDetails = Field(..., alias="pricingDetails")
    discount: int = Field(..., description="Discount in cents")


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
    name: str

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def get_offers(self, request_data: Any) -> List[Dict[str, Any]]:
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
        return [{}]
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

    # def _create_normalized_offer(self, raw_offer: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Create a normalized offer with common fields.
    #     """
    #     normalized = self.normalize_offer(raw_offer)
    #     return {
    #         "provider": self.provider_name,
    #         "offer_id": normalized.get("offer_id"),
    #         "download_speed": normalized.get("download_speed"),
    #         "upload_speed": normalized.get("upload_speed"),
    #         "price": normalized.get("price"),
    #         "contract_length": normalized.get("contract_length"),
    #         "setup_fee": normalized.get("setup_fee"),
    #         "cancellation_fee": normalized.get("cancellation_fee"),
    #         "provider_specific": normalized.get("provider_specific", {}),
    #         "fetched_at": datetime.utcnow().isoformat(),
    #     }


# class Provider(BaseModel):
#     {ProviderEnum}: BaseProvider
