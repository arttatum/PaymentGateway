import os

import boto3

from application.mapping.mapper import Mapper
from application.mapping.payment_request_mapper import PaymentRequestMapper
from application.repositories.exceptions.NotFound import NotFound
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from shared_kernel.lambda_logging import get_logger


class PaymentRequestsRepository:
    def __init__(self):
        payment_requests_table_name = os.environ["PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME"]
        self.logger = get_logger()
        self.payment_requests_table = boto3.resource("dynamodb").Table(payment_requests_table_name)

    def upsert(self, payment_request: PaymentRequest) -> None:
        """Insert or overwrite.

        Why?
        Simple way to achieve idempotency.

        Args:
            PaymentRequest (PaymentRequest): PaymentRequest to insert or overwrite in dynamodb.

        Raises:
            TypeError: if provided object is not of type PaymentRequest
            Exception: unexpected exception is logged and bubbled upwards
        """
        if type(payment_request) != PaymentRequest:
            self.logger.error(
                f"The argument passed to upsert() must be a {PaymentRequest}, not {type(payment_request)}."
            )
            raise TypeError()

        try:
            self.payment_requests_table.put_item(Item=Mapper.object_to_dict(payment_request))
            self.logger.debug("Saved PaymentRequest in database.")
        except Exception as e:
            self.logger.error(f"Failed to save PaymentRequest in database: {e.__class__.__name__}")
            self.logger.debug(f"Exception: {e}")
            raise e

    def get_by_aggregate_root_id(self, payment_request_id: str) -> PaymentRequest:
        try:
            payment_request_item = self.payment_requests_table.get_item(
                Key={
                    "id": payment_request_id,
                }
            )["Item"]
            self.logger.debug("Retrieved PaymentRequest from database.")
        except KeyError:
            # "Item" attribute is not present if no record was discovered in dynamodb.
            # Hence Key Error => NotFound
            message = "Failed to get PaymentRequest from dynamo: the PaymentRequest was not found."
            self.logger.error(message)
            raise NotFound()
        except Exception as e:
            self.logger.error(f"Failed to get PaymentRequest from database: {e.__class__.__name__}")
            self.logger.debug(f"Exception: {e}")
            raise e

        return PaymentRequestMapper.from_json(payment_request_item)
