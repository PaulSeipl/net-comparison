from pydantic import PrivateAttr
from app.schemas import (
    PingPerfectRequestData,
    PingPerfectHeaders,
    ProviderEnum,
    NetworkRequestData,
    BaseProvider,
)
from app.config import get_settings
from typing import Dict, List, Any
import requests
import logging
import time
import json
import hmac
import hashlib


class PingPerfect(BaseProvider):
    name: str = ProviderEnum.PINGPERFECT.value
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

        current_timestamp = int(time.time())

        payload = self.get_payload(request_data=request_data)
        payload_dict = payload.model_dump(by_alias=True)
        payload_as_json = json.dumps(
            payload_dict, ensure_ascii=False, separators=(",", ":")
        )
        payload_hashed = self.get_hashed_payload(
            payload_as_json, current_timestamp, settings.PINGPERFECT_SIGNATURE_SECRET
        )

        headers = self.get_headers(
            payload_hashed=payload_hashed,
            client_id=settings.PINGPERFECT_CLIENT_ID,
            current_timestamp=current_timestamp,
        ).model_dump(by_alias=True)

        try:
            response = requests.post(
                settings.PINGPERFECT_URL,
                headers=headers,
                data=payload_as_json,
            )
        except Exception as e:
            self._logger.exception(
                "Error while making request to Ping Perfect API", exc_info=e
            )
            print(f"Exception: {e}")

        if response.status_code == 200:
            pass
        elif response.status_code == 500:
            pass

        # products = self.parse_xml_response(response.text)

        # products = self.normalize_offer(response.text)

        return response.json()

    def normalize_offer(self, raw_offer: str) -> List[Dict[str, Any]]:
        """
        Normalize the provider-specific offer format into a common format.
        """
        raw_products = self.parse_csv_response(raw_offer)
        products = self.remove_duplicates_from_dict_list(raw_products)
        return products

    def get_payload(self, request_data: NetworkRequestData) -> PingPerfectRequestData:
        """
        Create the payload for the API request.
        """
        payload = PingPerfectRequestData(
            city=request_data.address.city,
            house_number=request_data.address.house_number,
            plz=request_data.address.zip,
            street=request_data.address.street,
            wants_fiber=request_data.connection_type == "fiber",
        )

        return payload

    def get_headers(
        self, payload_hashed: str, client_id: str, current_timestamp: int
    ) -> PingPerfectHeaders:
        """
        Create the headers for the API request.
        """
        headers = PingPerfectHeaders(
            x_client_id=client_id,
            x_signature=payload_hashed,
            x_timestamp=str(current_timestamp),
            content_type="application/json",
        )

        return headers

    def get_hashed_payload(
        self, payload_as_json: str, current_timestamp: int, secret: str
    ) -> str:
        """
        Hash the payload using HMAC with SHA256.
        """
        json_and_timestamp = f"{current_timestamp}:{payload_as_json}"

        hashed_payload = hmac.new(
            key=secret.encode(),
            msg=json_and_timestamp.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hashed_payload
