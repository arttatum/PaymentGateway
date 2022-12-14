import json

from application.services.PaymentRequestService import PaymentRequestService
from core.commands.ProcessAcquiringBankResponse import ProcessAcquiringBankResponse
from shared_kernel.lambda_logging.decorators import (
    configure_lambda_logger,
    return_400_for_domain_exceptions,
    return_500_for_unhandled_exceptions,
)
from shared_kernel.lambda_logging.set_up_logger import add_context, get_logger


@configure_lambda_logger
@return_500_for_unhandled_exceptions
@return_400_for_domain_exceptions
def lambda_handler(event, context):
    logger = get_logger()

    # Some services stringify JSON (escaping quotes), others don't. Try to handle both scenarios,
    # since this Lambda is triggered via CLI, but would be called by an application load balancer
    # if development continued in AWS

    if type(event["body"]) == str:
        payload = json.loads(event["body"])
    else:
        payload = event["body"]

    try:
        payment_request_id = payload["payment_request_id"]
        add_context(logger, "payment_request_id", payment_request_id)

        # Not strictly required, but helpful for observability and simpler
        # backwards compatibility if merchant_id were to become part of
        # the composite primary key for a PaymentRequest
        merchant_id = payload["merchant_id"]
        add_context(logger, "merchant_id", merchant_id)

        response = payload["response"]
    except KeyError as ke:
        message = f"Bad request, required field: {ke} missing."
        logger.info(message)
        logger.debug(payload)
        return {"statusCode": 400, "body": message}

    command = ProcessAcquiringBankResponse(payment_request_id, response)

    service = PaymentRequestService()
    service.process_acquiring_bank_response(command)

    return {"statusCode": 200, "body": "Success"}
