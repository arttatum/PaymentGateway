import os

import boto3

from application.mapping.mapper import Mapper
from application.repositories.PaymentRequestsRepository import PaymentRequestsRepository
from core.commands.ForwardPaymentRequestToAcquiringBank import (
    ForwardPaymentRequestToAcquiringBank,
)
from core.commands.ProcessAquiringBankResponse import ProcessAquiringBankResponse
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from shared_kernel.lambda_logging.set_up_logger import get_logger


class PaymentRequestService:
    def __init__(self):
        self.payment_requests_repo = PaymentRequestsRepository()
        self.logger = get_logger()

    def submit_payment_request(self, command: SubmitPaymentRequest):
        payment_request = PaymentRequest(command)
        self.logger.info("Created new Payment Request.")

        self.payment_requests_repo.upsert(payment_request)
        self.logger.info("Inserted to Dynamo.")

        forward_payment_request_command = ForwardPaymentRequestToAcquiringBank(
            payment_request.id, payment_request.merchant_id
        )
        self.send_forward_to_acquiring_bank_command_to_queue(forward_payment_request_command)
        self.logger.info("Published ForwardPaymentRequestToAcquiringBank command to queue.")

        return payment_request.id

    def forward_payment_request_to_aquiring_bank(self, command: ForwardPaymentRequestToAcquiringBank):
        # get payment request aggregate root
        # transform to payload expected by aquiring bank
        # send over http
        # call method on payment request: mark_as_forwarded_to_acquiring_bank
        # update payment request aggregate root
        pass

    def process_aquiring_bank_response(self, command: ProcessAquiringBankResponse):
        # get payment request aggregate root
        # call method on object: process_aquiring_bank_response
        # update payment request aggregate root
        pass

    def send_forward_to_acquiring_bank_command_to_queue(self, command: ForwardPaymentRequestToAcquiringBank):
        """TECH DEBT: this mechanism could be refactored behind an abstraction as required.

        Args:
            command (ForwardPaymentRequestToAcquiringBank): Command to add to the queue
        """
        queue_name = os.environ["PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME"]
        sqs_resource = boto3.resource("sqs")
        payments_to_forward_queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
        payments_to_forward_queue.send_message(MessageBody=Mapper.object_to_string(command))
