from app.schemas import (
    ProviderEnum,
    NetworkRequestData,
    ByteMeQueryParams,
    ApiRequestHeaders,
    BaseProvider
)
from pydantic import PrivateAttr
from app.config import get_settings
from typing import Dict, List, Any
import requests
import logging
import csv


class ByteMe(BaseProvider):
    name: str = ProviderEnum.BYTEME.value
    _logger: logging.Logger = PrivateAttr()
    
    def __init__(self, logger: logging.Logger, **data):
        super().__init__(**data)
        self._logger = logger

    def provider_name(self) -> str:
        return self.name

    async def get_offers(
        self, request_data: NetworkRequestData
    ) -> List[Dict[str, Any]]:
        settings = get_settings()

        headers = ApiRequestHeaders(
            content_type="text/xml; charset=utf-8", x_api_key=settings.BYTEME_API_KEY
        ).model_dump(by_alias=True)
        print(headers)

        address = request_data.address

        query_params = ByteMeQueryParams(
            street=address.street,
            house_number=address.house_number,
            city=address.city,
            plz=address.zip,
        ).model_dump(by_alias=True)

        try:
            response = requests.get(
                settings.BYTEME_BASE_URL,
                headers=headers,
                params=query_params,  # Add query parameters here
            )
        except Exception as e:
            self._logger.exception("Error while making request to ByteMe API", exc_info=e)

        print(response)

        if response.status_code == 200:
            pass
        elif response.status_code == 500:
            pass

        # products = self.parse_xml_response(response.text)
        
        products = self.normalize_offer(response.text)

        return products

    def normalize_offer(self, raw_offer: str) -> List[Dict[str, Any]]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        raw_products = self.parse_csv_response(raw_offer)
        products = self.remove_duplicates_from_dict_list(raw_products)
        return products
    
    def parse_csv_response(self, csv_data: str) -> List[Dict[str, Any]]:
        """
        Parse the CSV response and convert it into a list of dictionaries.
        """     
        return [product for product in csv.DictReader(csv_data.splitlines())]
    
    def remove_duplicates_from_dict_list(self, dict_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicates from a list of dictionaries
        """
        return [dict(unique) for unique in {tuple(d.items()) for d in dict_list}]
        


