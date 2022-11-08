import os

import boto3
import requests

from application.mapping.payment_request_mapper import Mapper
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from shared_kernel.lambda_logging import get_logger


class AcquiringBankClient:
    """
    Assumption: API Key (also, potentially network level controls)
    will be used to authenticate our system to call Bank's APIs
    """

    def __init__(self):
        self.logger = get_logger()
        self.api_key = self._get_api_key()
        self.api_post_payment_request_url = os.environ["ACQUIRING_BANK_POST_PAYMENT_REQUEST_URL"]

    def post_payment_request(self, payment_request: PaymentRequest):
        response = requests.post(
            self.api_post_payment_request_url,
            timeout=30,
            headers={
                "x-api-key": self.api_key,
            },
            json=Mapper.object_to_json_string(payment_request),
        )

        self.logger.info(f"Status code response from bank: {response.status_code}")

        # Any 4xx or 5xx status will cause exception to be raised
        response.raise_for_status()

    def _get_api_key(self):
        try:
            api_key_secret_name = os.environ["ACQUIRING_BANK_API_KEY_SECRET_NAME"]
            client = boto3.client(service_name="secretsmanager", region_name="eu-west-2")
            get_secret_response = client.get_secret_value(SecretId=api_key_secret_name)
            return get_secret_response["SecretString"]
        except Exception as e:
            self.logger.error("Failed to get API key.")
            raise e
