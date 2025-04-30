from enum import Enum
from pydantic import BaseModel, Field

class Address(BaseModel):
    street: str
    house_number: str
    city: str
    zip: int
    country_code: str

class WebWunderConnectionTypes(str, Enum):
    DSL = 'DSL'
    CABLE = 'CABLE'
    FIBER = 'FIBER'
    MOBILE = 'MOBILE' 
    
class WebWunderRequestData(BaseModel):
    installation: bool
    connection_type: WebWunderConnectionTypes
    address: Address
    
class WebWunderHeaders(BaseModel):
    content_type: str = Field('text/xml; charset=utf-8', alias='Content-Type')
    x_api_key: str = Field(..., alias='X-Api-Key')

    class Config:
        allow_population_by_field_name = True
    
    

class ProviderEnum(str, Enum):
    WEBWUNDER = 'WebWunder'
    BYTEME = 'ByteMe'
    PINGPERFECT = 'Ping Perfect'
    VERBYNDICH = 'VerbynDich'
    SERVUSSPEED = 'Servus Speed'
    
class Provider(BaseModel):
    name: ProviderEnum
    
