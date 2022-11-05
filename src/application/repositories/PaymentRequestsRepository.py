import os

import boto3
from mapping.mapper import Mapper
from mapping.payment_request_mapper import PaymentRequestMapper
from repositories.exceptions.NotFound import NotFound

from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from shared_kernel.lambda_logging import get_logger


class PaymentRequestsRepository:
    def __init__(self):
        PaymentRequests_table_name = os.environ.get("PaymentRequestS_DYNAMODB_TABLE_NAME")
        self.logger = get_logger()
        self.PaymentRequests_table = boto3.resource("dynamodb").Table(PaymentRequests_table_name)

    def upsert(self, PaymentRequest: PaymentRequest) -> None:
        """Insert or overwrite.

        Why?
        Simple way to achieve idempotency.

        Args:
            PaymentRequest (PaymentRequest): PaymentRequest to insert or overwrite in dynamodb.

        Raises:
            TypeError: if provided object is not of type PaymentRequest
            Exception: unexpected exception is logged and bubbled upwards
        """
        if type(PaymentRequest) != PaymentRequest:
            error_message = f"The argument passed to upsert() must be a {PaymentRequest}, not {type(PaymentRequest)}."
            self.logger.error(error_message)
            raise TypeError()

        try:
            self.PaymentRequests_table.put_item(Item=Mapper.object_to_dict(PaymentRequest))
            self.logger.debug("Created PaymentRequest in database.")
        except Exception as e:
            self.logger.error(f"Failed to create PaymentRequest in database, due to exception: {e.__class__.__name__}")
            self.logger.debug(f"Exception: {e}")
            raise e

    def get_by_aggregate_root_id(self, PaymentRequest_request_id, merchant_id) -> PaymentRequest:
        try:
            PaymentRequest_item = self.PaymentRequests.get_item(
                Key={
                    "PaymentRequest_request_id": PaymentRequest_request_id,
                    "merchant_id": merchant_id,
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

        return PaymentRequestMapper.from_json(PaymentRequest_item)
