from enum import Enum
from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from abc import ABC, abstractmethod


class BaseModel(BaseModel):
    """
    Base model for all schemas.
    """

    model_config = ConfigDict(
        validate_by_name=True,
        json_encoders={
            str: lambda v: v if v else None,  # Handle empty strings
        },
        from_attributes=True,
    )


class ProviderEnum(str, Enum):
    WEBWUNDER = "WebWunder"
    BYTEME = "ByteMe"
    PINGPERFECT = "Ping Perfect"
    VERBYNDICH = "VerbynDich"
    SERVUSSPEED = "Servus Speed"


class ConnectionTypeEnum(str, Enum):
    DSL = "DSL"
    CABLE = "Cable"
    FIBER = "Fiber"
    MOBILE = "Mobile"

class PriceDetails(BaseModel):
    monthly_cost: int
    monthly_cost_with_discount: int | None = None
    monthly_savings: int | None = None
    monthly_cost_after_promotion: int | None = None
    total_savings: int | None = None
    setup_fee: int | None = None
    discount_percentage: int | None = None  # Percentage discount

class NormalizedOffer(BaseModel):
    # Core Identification
    provider: ProviderEnum
    offer_id: str  # self generate if not available
    name: str

    # Technical Details
    speed: int
    connection_type: ConnectionTypeEnum

    # Pricing Information (all in cents)
    price_details: PriceDetails

    # Contract Terms
    contract_duration: int  # in months
    
    installation_service: bool | None

    # Age & Eligibility Restrictions
    max_age: int | None = None

    # Additional Services & Features
    tv_service: str | None = None
    promotion_length: int | None = None  # Length of promotion in months
    data_limit: int | None = None  # Data limit in GB, if applicable

    # Metadata
    fetched_at: str  # ISO timestamp

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        if isinstance(v, str):
            # Convert string to enum if needed
            return ProviderEnum(v)
        return v

    @field_validator("connection_type")
    @classmethod
    def validate_connection_type(cls, v):
        if isinstance(v, str):
            return ConnectionTypeEnum(v)
        return v

    @property
    def provider_name(self) -> str:
        """Get the string value of the provider enum"""
        return self.provider.value


class Address(BaseModel):
    street: str = Field(..., examples=["Musterstraße"])
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
    address: Address


class WebWunderRequestHeaders(BaseModel):
    content_type: str = Field("text/xml; charset=utf-8", alias="Content-Type")
    x_api_key: str = Field(..., alias="X-Api-Key")


class WebWunderFetchReturn(BaseModel):
    installation_service: bool
    connection_type: str
    response_text: str


class WebWunderProduct(BaseModel):
    product_id: str = Field(..., alias="productId")
    provider_name: str = Field(..., alias="providerName")
    speed: int
    monthly_cost_in_cent: int = Field(..., alias="monthlyCostInCent")
    monthly_cost_in_cent_from_25th_month: int = Field(
        ..., alias="monthlyCostInCentFrom25thMonth"
    )
    contract_duration_in_months: int = Field(..., alias="contractDurationInMonths")
    connection_type: str = Field(..., alias="connectionType")

    # Percentage voucher fields
    voucher_percentage: int | None = Field(None, alias="voucherPercentage")
    max_discount_in_cent: int | None = Field(None, alias="maxDiscountInCent")

    # Absolute voucher fields
    discount_in_cent: int | None = Field(None, alias="discountInCent")
    min_order_value_in_cent: int | None = Field(None, alias="minOrderValueInCent")


class ByteMeQueryParams(BaseModel):
    street: str = Field(..., examples=["Musterstraße"])
    house_number: str = Field(..., examples=["5"], alias="houseNumber")
    city: str = Field(..., examples=["München"])
    plz: int = Field(..., examples=[80333])


class ByteMeProduct(BaseModel):
    product_id: str = Field(..., alias="productId")
    provider_name: str = Field(..., alias="providerName")
    speed: int = Field(..., alias="speed")
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

    # Convert boolean string fields to bool
    @field_validator("installation_service")
    @classmethod
    def parse_bool(cls, value: str) -> bool:
        return value.lower() == "true"


class PingPerfectHeaders(BaseModel):
    x_client_id: str = Field(..., alias="X-Client-Id")
    x_signature: str = Field(..., alias="X-Signature")
    x_timestamp: str = Field(..., alias="X-Timestamp")
    content_type: str = Field("application/json", alias="Content-Type")


class PingPerfectRequestData(BaseModel):
    city: str = Field(..., examples=["München"])
    house_number: str = Field(..., examples=["5"], alias="houseNumber")
    plz: int = Field(..., examples=[80333])
    street: str = Field(..., examples=["Musterstraße"])
    wants_fiber: bool = Field(False, alias="wantsFiber")


class PingPerfectProductInfo(BaseModel):
    speed: int = Field(..., examples=[30])
    contract_duration_in_months: int = Field(..., alias="contractDurationInMonths")
    connection_type: Literal["DSL", "CABLE", "FIBER", "MOBILE"] = Field(
        ..., examples=["DSL"]
    )
    tv: str = Field(..., examples=["PING TV"])
    limit_from: str | None = Field(None, alias="limitFrom")
    max_age: str | None = Field(None, alias="maxAge")


class PingPerfectPricingDetails(BaseModel):
    monthly_cost_in_cent: int = Field(..., alias="monthlyCostInCent")
    installation_service: str = Field(..., examples=["no"], alias="installationService")


class PingPerfectResponseData(BaseModel):
    provider_name: str = Field(..., alias="providerName")
    product_info: PingPerfectProductInfo = Field(..., alias="productInfo")
    pricing_details: PingPerfectPricingDetails = Field(..., alias="pricingDetails")


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


class ServusSpeedRequestAddress(BaseModel):
    street: str = Field(..., examples=["Musterstraße"], alias="strasse")
    house_number: str = Field(..., examples=["5"], alias="hausnummer")
    zip: int = Field(..., examples=[80333], alias="postleitzahl")
    city: str = Field(..., examples=["München"], alias="stadt")
    country_code: str = Field(..., examples=["DE"], alias="land")


class ServusSpeedRequestData(BaseModel):
    address: ServusSpeedRequestAddress


class ServusSpeedHeaders(BaseModel):
    content_type: str = Field("application/json", alias="Content-Type")
    accept: str = Field("*/*", alias="Accept")
    accept_encoding: str = Field("gzip, deflate, br", alias="Accept-Encoding")
    connection: str = Field("keep-alive", alias="Connection")


class ServusSpeedAvailableProducts(BaseModel):
    available_products: List[str] = Field(..., alias="availableProducts")


class ServusSpeedProductInfo(BaseModel):
    speed: int = Field(..., examples=[30])
    contract_duration_in_months: int = Field(..., alias="contractDurationInMonths")
    connection_type: Literal["DSL", "Cable", "Fiber"] = Field(
        ..., examples=["DSL"], alias="connectionType"
    )
    tv: str | None = Field(..., examples=["PING TV"])
    limit_from: int | None = Field(None, alias="limitFrom")
    max_age: int | None = Field(None, alias="maxAge")


class ServusSpeedPricingDetails(BaseModel):
    monthly_cost_in_cent: int = Field(..., alias="monthlyCostInCent")
    installation_service: bool = Field(..., alias="installationService")


class ServusSpeedProduct(BaseModel):
    provider_name: str = Field(..., alias="providerName")
    product_info: ServusSpeedProductInfo = Field(..., alias="productInfo")
    pricing_details: ServusSpeedPricingDetails = Field(..., alias="pricingDetails")
    discount: int = Field(..., description="Discount in cents")


class BaseProvider(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Make circuit_breaker a class attribute so it can be used as a decorator
    # circuit_breaker = circuit_breaker
    #    db: str
    name: str

    @property
    @abstractmethod
    def name(self) -> str:
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
