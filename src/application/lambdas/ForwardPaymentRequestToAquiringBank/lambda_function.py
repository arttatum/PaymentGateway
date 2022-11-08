import json

from application.services.PaymentRequestService import PaymentRequestService
from core.commands.ForwardPaymentRequestToAcquiringBank import (
    ForwardPaymentRequestToAcquiringBank,
)
from shared_kernel.lambda_logging.decorators import configure_lambda_logger
from shared_kernel.lambda_logging.set_up_logger import add_context, get_logger


@configure_lambda_logger
def lambda_handler(event, context):
    """Triggered via SQS Event Source Mapping

    Pulls single message off queue (could be modified to process
    batches by looping over Records).

    Message follows ForwardPaymentRequestToAcquiringBank schema.
    Versioning should be introduced for this command schema to simplify
    backward compatibility.

    Exceptions are deliberately not handled, so messages are DLQ'd if they are not processed.

    Args:
        event (dict): provided by SQS
        context (object): provided by AWS
    """
    logger = get_logger()

    message_body = json.loads(event["Records"][0]["body"])
    logger.info("Parsed message from SQS.")

    command_from_queue = ForwardPaymentRequestToAcquiringBank.from_json(message_body)
    add_context(logger, "merchant_id", command_from_queue.merchant_id)
    logger.info("Formed ForwardPaymentRequestToAcquiringBank command.")

    service = PaymentRequestService()
    service.forward_payment_request_to_aquiring_bank(command_from_queue)
    logger.info("Forwarded to aquiring bank.")
