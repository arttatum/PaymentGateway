import os

from application.clients.AcquiringBankClient import AcquiringBankClient
from application.clients.AWSClient import AWSClient
from application.mapping.mapper import Mapper
from application.repositories.PaymentRequestsRepository import PaymentRequestsRepository
from core.commands.ForwardPaymentRequestToAcquiringBank import (
    ForwardPaymentRequestToAcquiringBank,
)
from core.commands.ProcessAcquiringBankResponse import ProcessAcquiringBankResponse
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from core.payment_request_aggregate.value_objects.AcquiringBankResponse import (
    AcquiringBankResponse,
)
from shared_kernel.lambda_logging.set_up_logger import get_logger


class PaymentRequestService:
    def __init__(self) -> None:
        self.payment_requests_repo = PaymentRequestsRepository()
        self.logger = get_logger()

    def submit_payment_request(self, command: SubmitPaymentRequest) -> str:
        """Submit a PaymentRequest.

        Creates the PaymentRequest aggregate, where validation of inputs parameters occurs.
        Adds the item to Dynamo, and if successful sends a command to SQS that instructs
        the system that this request must be forwarded to the Acquiring Bank.

        Optimisations that can exist here to improve transactionality and performance include
        the Transactional Outbox Pattern.
        https://learn.microsoft.com/en-us/azure/architecture/best-practices/transactional-outbox-cosmos

        Args:
            command (SubmitPaymentRequest): _

        Returns:
            str: the new PaymentRequest's ID.
        """
        self.logger.info("Creating new Payment Request.")
        payment_request = PaymentRequest(command)

        self.payment_requests_repo.upsert(payment_request)

        forward_payment_request_command = ForwardPaymentRequestToAcquiringBank(
            payment_request.id, payment_request.merchant_id.value
        )
        self._send_forward_to_acquiring_bank_command_to_queue(forward_payment_request_command)
        self.logger.info("Published ForwardPaymentRequestToAcquiringBank command to SQS.")

        return payment_request.id

    def process_acquiring_bank_response(self, command: ProcessAcquiringBankResponse) -> None:
        payment_request = self.payment_requests_repo.get_by_aggregate_root_id(
            command.payment_request_id
        )
        response = AcquiringBankResponse(command.response)
        payment_request.process_acquiring_bank_response(response)
        self.payment_requests_repo.upsert(payment_request)

    def forward_payment_request_to_acquiring_bank(
        self, command: ForwardPaymentRequestToAcquiringBank
    ) -> None:
        """Forwards PaymentRequest to the Acquiring Bank, if it has not already done so.

        A note on idempotency:
        There exists an edge case where duplicate messages are processed in very quick succession,
        such that the the aggregate has not yet been updated in dynamo. This may result in duplciates
        being sent to the Acquiring Bank.

        Better strategies exist to enforce idempotency, such as storing hashes of messages, or pushing
        that responsibiltiy to SQS itself.

        Args:
            command (ForwardPaymentRequestToAcquiringBank): Command containing relevant information
        """
        # get payment request aggregate root
        payment_request = self.payment_requests_repo.get_by_aggregate_root_id(
            command.payment_request_id
        )

        # For (poor man's) idempotency... and reporting of status via merchant's GET endpoint
        if payment_request.is_sent_to_acquiring_bank:
            self.logger.info("PaymentRequest already forwarded to Acquiring Bank.")
            return

        # If transformation to schema required by Acquiring Bank were
        # required, this would be the place to do it.

        acquiring_bank_client = AcquiringBankClient()
        acquiring_bank_client.post_payment_request(payment_request)

        payment_request.mark_as_forwarded_to_acquiring_bank()
        self.payment_requests_repo.upsert(payment_request)

    def _send_forward_to_acquiring_bank_command_to_queue(
        self, command: ForwardPaymentRequestToAcquiringBank
    ) -> None:
        """Publishes the ForwardPaymentRequestToAcquiringBank command to teh
        PAYMENT_REQUESTS_TO_FORWARD SQS queue.

        TECH DEBT: The mechanism to send commands to SQS queues
        could be refactored behind an abstraction as required.

        Args:
            command (ForwardPaymentRequestToAcquiringBank): Command to add to the queue
        """
        queue_name = os.environ["PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME"]
        sqs_resource = AWSClient.get_sqs_resource()
        payments_to_forward_queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
        payments_to_forward_queue.send_message(MessageBody=Mapper.object_to_json_string(command))
