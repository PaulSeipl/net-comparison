from enum import Enum
from pydantic import BaseModel, Field

class Address(BaseModel):
    street: str = Field(..., example=" Musterstraße")
    house_number: str = Field(..., example="5")
    zip: int = Field(..., example="80333")
    city: str = Field(..., example="München")
    country_code: str = Field(..., example="DE")

class WebWunderConnectionTypes(str, Enum):
    DSL = 'DSL'
    CABLE = 'CABLE'
    FIBER = 'FIBER'
    MOBILE = 'MOBILE' 
    
class WebWunderRequestData(BaseModel):
    installation: bool = Field(..., example=True)
    connection_type: WebWunderConnectionTypes = Field(..., example=WebWunderConnectionTypes.DSL)
    address: Address
    
class ApiRequestHeaders(BaseModel):
    content_type: str = Field('text/xml; charset=utf-8', alias='Content-Type')
    x_api_key: str = Field(..., alias='X-Api-Key')

    class Config:
        validate_by_name = True
        
class ByteMeQueryParams(BaseModel):
    street: str = Field(..., example="Musterstraße")
    house_number: str = Field(..., example="5", alias="houseNumber")
    city: str = Field(..., example="München")
    plz: int = Field(..., example=80333)
    
    class Config:
        validate_by_name = True
    
    

class ProviderEnum(str, Enum):
    WEBWUNDER = 'WebWunder'
    BYTEME = 'ByteMe'
    PINGPERFECT = 'Ping Perfect'
    VERBYNDICH = 'VerbynDich'
    SERVUSSPEED = 'Servus Speed'
    
class Provider(BaseModel):
    name: ProviderEnum
    
