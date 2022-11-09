from application.dtos.GetPaymentStatusDTO import GetPaymentStatusDTO
from application.repositories.exceptions.NotFound import NotFound
from application.repositories.PaymentRequestsRepository import PaymentRequestsRepository
from shared_kernel.guard_clauses.uuid_guard import is_valid_uuid
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
    """Gets status of a payment request.

    Assumption has been made that whatever status is provided to the Payment
    Gateway by the Acquiring Bank, can safely be shown to Merchants as-is.

    User research and legal aspects should be examined further to inform this
    decision.

    NB: Read stack is thinner than Writer stack by design. The write stack
    is optimised for correctness, while the read stack is optimised for speed.

    If called for, another repository could be created that was specifically built
    for speed. It could cut out the steps where json is mapped to python objects, then
    back to json, for instance.

    Args:
        event (dict): API Gateway Proxy Lambda Integration event
        context (object): AWS provided obejct

    Returns:
        _type_: HTTP Response
    """
    logger = get_logger()

    try:
        payload = event["pathParameters"]

        merchant_id = payload["merchant_id"]
        add_context(logger, "merchant_id", merchant_id)

        payment_request_id = payload["payment_request_id"]
        add_context(logger, "payment_request_id", payment_request_id)

    except KeyError as ke:
        logger.error(f"API Gateway event did not contain expected field: {ke}")
        return {"statusCode": 500, "body": "Internal Server Error"}

    is_payment_request_id_uuid = is_valid_uuid(payment_request_id)
    is_merchant_id_uuid = is_valid_uuid(merchant_id)

    if not is_payment_request_id_uuid and not is_merchant_id_uuid:
        message = "payment_request_id and merchant_id are not valid uuids."
        logger.info(message)
        return {"statusCode": 400, "body": message}

    if not is_payment_request_id_uuid:
        message = "payment_request_id is not a valid uuid"
        logger.info(message)
        return {"statusCode": 400, "body": message}

    if not is_merchant_id_uuid:
        message = "merchant_id is not a valid uuid"
        logger.info(message)
        return {"statusCode": 400, "body": message}

    repo = PaymentRequestsRepository()

    try:
        payment_request = repo.get_by_aggregate_root_id(payment_request_id)
    except NotFound:
        return {"statusCode": 404, "body": "Not Found"}

    if payment_request.merchant_id.value != merchant_id:
        logger.critical(
            f"The merchant with ID: {merchant_id} tried to get the status of a payment"
            f" for another merchant, whose ID is: {payment_request.merchant_id.value}!"
        )
        return {"statusCode": 404, "body": "Not Found"}

    if not payment_request.is_sent_to_acquiring_bank:
        return {
            "statusCode": 200,
            "body": GetPaymentStatusDTO(payment_request, "Processing - In Payment Gateway").json,
        }

    if payment_request.acquiring_bank_response is None:
        return {
            "statusCode": 200,
            "body": GetPaymentStatusDTO(
                payment_request, "Processing - Awaiting response from acquiring bank"
            ).json,
        }

    return {
        "statusCode": 200,
        "body": GetPaymentStatusDTO(
            payment_request, payment_request.acquiring_bank_response.value
        ).json,
    }
