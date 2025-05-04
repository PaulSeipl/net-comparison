from app.api.base import BaseProvider
from app.schemas import (
    ProviderEnum,
    WebWunderRequestData,
    WebWunderConnectionTypes,
    ApiRequestHeaders,
)
from app.config import get_settings
from typing import Dict, List, Any, Optional
import requests
import xml.etree.ElementTree as ET
import logging


class WebWunder(BaseProvider):
    def __init__(self, db):
        super().__init__()
        self.name = ProviderEnum.WEBWUNDER.value
        self.logger = logging.Logger(self.name)

    def provider_name(self) -> str:
        return self.name

    async def get_offers(
        self, request_data: WebWunderRequestData
    ) -> List[Dict[str, Any]]:
        settings = get_settings()
        payload = self.create_soap_payload(request_data)

        headers = ApiRequestHeaders(x_api_key=settings.WEBWUNDER_API_KEY).model_dump(by_alias=True)
        print(headers)
        try:
            response = requests.post(
                settings.WEBWUNDER_BASE_URL,
                data=payload,
                headers=headers,
            )
        except Exception as e:
            self.logger(e)
        
        print(response)
        
        if response.status_code == 200:
            pass
        elif response.status_code == 500:
            pass
        
        return self.normalize_offer(response.text)
    

    def normalize_offer(self, raw_offer: str) -> List[Dict[str, Any]]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        products = self.parse_xml_response(raw_offer)
        
        return products
        

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
                            
                            
    def parse_xml_response(self, response: str) -> List[Dict]:
        # Parse the XML
        print(response)
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

        return product_list
