from base import BaseProvider
from ..schemas import (
    ProviderEnum,
    WebWunderRequestData,
    WebWunderConnectionTypes,
    WebWunderHeaders,
)
from ..config import get_settings
from typing import Dict, List, Any, Optional
import requests
import xml.etree.ElementTree as ET


class WebWunder(BaseProvider):
    def __init__(self, db):
        super().__init__(db)
        self.name = ProviderEnum.WEBWUNDER.value

    def provider_name(self) -> str:
        return self.name

    async def get_offers(
        self, request_data: WebWunderRequestData
    ) -> List[Dict[str, Any]]:
        settings = get_settings()
        payload = self.create_soap_payload(request_data)

        headers = WebWunderHeaders(x_api_key=settings.WEBWUNDER_API_KEY).model_dump(by_alias=True)

        response = requests.post(
            settings.WEBWUNDER_BASE_URL,
            data=payload,
            headers=headers,
        )
        
        print(response)
        

    @staticmethod
    def create_soap_payload(request_data: WebWunderRequestData) -> str:
        address = request_data.address
        return f"""<?xml version="1.0" encoding="UTF-8"?>
                            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                                            xmlns:gs="http://webwunder.gendev7.check24.fun/offerservice">
                            <soapenv:Header/>
                                <soapenv:Body>
                                    <gs:legacyGetInternetOffers>
                                        <gs:input>
                                            <gs:installation>{request_data.installation}</gs:installation>
                                            <gs:connectionEnum>{request_data.connection_type.value}</gs:connectionEnum>
                                            <gs:address>
                                                <gs:street>{address.street}</gs:street>
                                                <gs:houseNumber>{address.house_number}</gs:houseNumber>
                                                <gs:city>{address.city}</gs:city>
                                                <gs:plz>{address.zip}</gs:plz>
                                                <gs:countryCode>{address.country_code}</gs:countryCode>
                                            </gs:address>
                                        </gs:input>
                                    </gs:legacyGetInternetOffers>
                                </soapenv:Body>
                            </soapenv:Envelope>"""
                            
                            
    def parse_xml_response(response: str) -> dict:
        # Parse the XML
        root = ET.fromstring(response)

        # Define namespaces
        namespaces = {
            'SOAP-ENV': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns2': 'http://webwunder.gendev7.check24.fun/offerservice'
        }

        # Find all product entries
        products = root.findall('.//ns2:products', namespaces)

        # Extract data
        product_list = []
        for product in products:
            product_data = {
                'productId': product.find('ns2:productId', namespaces).text,
                'providerName': product.find('ns2:providerName', namespaces).text,
                'speed': product.find('.//ns2:speed', namespaces).text,
                'monthlyCostInCent': product.find('.//ns2:monthlyCostInCent', namespaces).text,
                'monthlyCostInCentFrom25thMonth': product.find('.//ns2:monthlyCostInCentFrom25thMonth', namespaces).text,
                'contractDurationInMonths': product.find('.//ns2:contractDurationInMonths', namespaces).text,
                'connectionType': product.find('.//ns2:connectionType', namespaces).text
            }
            product_list.append(product_data)

        # Print extracted data
        for p in product_list:
            print(p)
