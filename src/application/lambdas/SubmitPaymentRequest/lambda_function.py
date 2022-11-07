import json

from application.services.PaymentRequestService import PaymentRequestService
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from shared_kernel.lambda_logging.decorators import (
    configure_lambda_logger,
    return_400_for_domain_exceptions,
    return_500_for_unhandled_exceptions,
)
from shared_kernel.lambda_logging.set_up_logger import add_context, get_logger


@return_500_for_unhandled_exceptions
@return_400_for_domain_exceptions
@configure_lambda_logger
def lambda_handler(event, context):
    """Triggered via API Gateway integration.

    Transforms event into SubmitPaymentRequest command and passes to PayementRequestService

    Args:
        event (dict): provided by API Gateway
        context (object): provided by AWS
    """
    logger = get_logger()
    path_parameters = event["pathParameters"]
    merchant_id = path_parameters["merchant_id"]

    add_context(logger, "merchant_id", merchant_id)

    payload = json.loads(event["body"])

    try:
        (card_number, expiry_date, amount, currency, cvv) = _get_fields_from_payload(payload)
    except KeyError as ke:
        return {"statusCode": 400, "body": f"Missing required field: {ke}"}

    command = SubmitPaymentRequest(merchant_id, card_number, expiry_date, amount, currency, cvv)

    service = PaymentRequestService()

    payment_request_id = service.submit_payment_request(command)

    return {"statusCode": 201, "body": payment_request_id}


def _get_fields_from_payload(payload: dict):
    return (
        payload["card_number"],
        payload["expiry_date"],
        payload["amount"],
        payload["currency"],
        payload["cvv"],
    )
