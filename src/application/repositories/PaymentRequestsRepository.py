import os

from application.clients.AWSClient import AWSClient
from application.mapping.mapper import Mapper
from application.mapping.payment_request_mapper import PaymentRequestMapper
from application.repositories.exceptions.NotFound import NotFound
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from shared_kernel.lambda_logging import get_logger


class PaymentRequestsRepository:
    def __init__(self):
        self.payment_requests_table_name = os.environ["PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME"]
        self.logger = get_logger()
        self.payment_requests_table = AWSClient.get_dynamodb_resource().Table(
            self.payment_requests_table_name
        )

    def upsert(self, payment_request: PaymentRequest) -> None:
        """Inserts or overwrites.

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
            self.logger.info(
                f"Created or updated PaymentRequest in the {self.payment_requests_table_name} table."
            )
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
            self.logger.info(
                f"Retrieved PaymentRequest from {self.payment_requests_table_name} table."
            )
        except KeyError:
            # "Item" attribute is not present if no record was discovered in dynamodb.
            # Hence Key Error => NotFound
            message = f"PaymentRequest not found in {self.payment_requests_table_name} table."
            self.logger.error(message)
            raise NotFound()
        except Exception as e:
            self.logger.error(f"Failed to get PaymentRequest from {e.__class__.__name__} table.")
            self.logger.debug(f"Exception: {e}")
            raise e

        return PaymentRequestMapper.from_json(payment_request_item)
