import uuid

import pytest

from application.lambdas.GetPaymentRequestStatus.lambda_function import lambda_handler
from application.repositories.PaymentRequestsRepository import PaymentRequestsRepository
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from core.payment_request_aggregate.value_objects.AcquiringBankResponse import (
    AcquiringBankResponse,
)


def test_GetPaymentRequestStatus_returns_200_if_PaymentRequest_is_not_sent_to_acquiring_bank(
    make_lambda_context_object, make_api_gateway_event_get_payment_request_status, payment_requests_table
):
    # Given
    merchant_id = str(uuid.uuid4())
    card_number = "12345671234567"
    expiry_date = "08-32"
    amount = 1192.34
    currency = "POUNDS"
    cvv = "999"

    submit_command = SubmitPaymentRequest(
        merchant_id, card_number, expiry_date, amount, currency, cvv
    )

    payment_request = PaymentRequest(submit_command)

    payment_requests_repo = PaymentRequestsRepository()
    payment_requests_repo.upsert(payment_request)

    get_payment_request_status_event = make_api_gateway_event_get_payment_request_status(
        {"payment_request_id": payment_request.id, "merchant_id": payment_request.merchant_id.value}
    )

    context = make_lambda_context_object("GetPaymentRequestStatus")

    # When
    response = lambda_handler(get_payment_request_status_event, context)

    # Then
    assert response["statusCode"] == 200
    assert response["body"]["status"] == "Processing - In Payment Gateway"
    assert response["body"]["payment_details"] == {
        "id": payment_request.id,
        "card_number": "**********4567",
        "cvv": cvv,
        "expiry_date": "08-32",
        "amount": 1192.34,
        "currency": "POUNDS",
    }


def test_GetPaymentRequestStatus_returns_200_if_PaymentRequest_is_sent_to_acquiring_bank_and_response_not_received(
    make_lambda_context_object,
    make_api_gateway_event_get_payment_request_status,
    payment_requests_table,
    payment_request: PaymentRequest,
):
    # Given
    payment_requests_repo = PaymentRequestsRepository()
    payment_request.mark_as_forwarded_to_acquiring_bank()

    payment_requests_repo.upsert(payment_request)

    get_payment_request_status_event = make_api_gateway_event_get_payment_request_status(
        {"payment_request_id": payment_request.id, "merchant_id": payment_request.merchant_id.value}
    )

    context = make_lambda_context_object("GetPaymentRequestStatus")

    # When
    response = lambda_handler(get_payment_request_status_event, context)

    # Then
    assert response["statusCode"] == 200
    assert response["body"]["status"] == "Processing - Awaiting response from acquiring bank"


@pytest.mark.parametrize("valid_response_from_bank", AcquiringBankResponse._valid_statuses)
def test_GetPaymentRequestStatus_returns_200_if_PaymentRequest_is_sent_to_acquiring_bank_and_response_received(
    make_lambda_context_object,
    make_api_gateway_event_get_payment_request_status,
    payment_requests_table,
    payment_request,
    valid_response_from_bank,
):

    # Given
    payment_requests_repo = PaymentRequestsRepository()
    payment_request.mark_as_forwarded_to_acquiring_bank()
    payment_request.process_acquiring_bank_response(AcquiringBankResponse(valid_response_from_bank))
    payment_requests_repo.upsert(payment_request)

    get_payment_request_status_event = make_api_gateway_event_get_payment_request_status(
        {"payment_request_id": payment_request.id, "merchant_id": payment_request.merchant_id.value}
    )

    context = make_lambda_context_object("GetPaymentRequestStatus")

    # When
    response = lambda_handler(get_payment_request_status_event, context)

    # Then
    assert response["statusCode"] == 200
    assert response["body"]["status"] == valid_response_from_bank


def test_GetPaymentRequestStatus_returns_404_if_PaymentRequest_not_found(
    make_lambda_context_object,
    make_api_gateway_event_get_payment_request_status,
    payment_requests_table,
    payment_request,
):
    get_payment_request_status_event = make_api_gateway_event_get_payment_request_status(
        {"payment_request_id": payment_request.id, "merchant_id": payment_request.merchant_id.value}
    )
    context = make_lambda_context_object("GetPaymentRequestStatus")

    # When
    response = lambda_handler(get_payment_request_status_event, context)

    # Then
    assert response["statusCode"] == 404
    assert response["body"] == "Not Found"


def test_GetPaymentRequestStatus_returns_404_if_PaymentRequest_belongs_to_a_different_merchant(
    make_lambda_context_object,
    make_api_gateway_event_get_payment_request_status,
    payment_requests_table,
    payment_request,
):
    # Given
    a_different_merchants_id = str(uuid.uuid4())
    payment_requests_repo = PaymentRequestsRepository()
    payment_request.mark_as_forwarded_to_acquiring_bank()
    payment_request.process_acquiring_bank_response(
        AcquiringBankResponse(AcquiringBankResponse.PAID)
    )
    payment_requests_repo.upsert(payment_request)

    get_payment_request_status_event = make_api_gateway_event_get_payment_request_status(
        {"payment_request_id": payment_request.id, "merchant_id": a_different_merchants_id}
    )

    context = make_lambda_context_object("GetPaymentRequestStatus")

    # When
    response = lambda_handler(get_payment_request_status_event, context)

    # Then
    assert response["statusCode"] == 404
    assert response["body"] == "Not Found"


def test_GetPaymentRequestStatus_returns_500_if_API_gateway_event_has_incorrect_structure(
    make_lambda_context_object,
    make_api_gateway_event_get_payment_request_status,
    payment_requests_table,
    payment_request,
):
    # Given
    payment_requests_repo = PaymentRequestsRepository()
    payment_requests_repo.upsert(payment_request)

    get_payment_request_status_event = make_api_gateway_event_get_payment_request_status(
        {"payment_request_id": payment_request.id}
    )

    context = make_lambda_context_object("GetPaymentRequestStatus")

    # When
    response = lambda_handler(get_payment_request_status_event, context)

    # Then
    assert response["statusCode"] == 500
    assert response["body"] == "Internal Server Error"


@pytest.mark.parametrize(
    ("payment_request_id", "merchant_id"),
    [
        (str(uuid.uuid4()), "not_an_id"),
        ("not_an_id", str(uuid.uuid4())),
        ("not_an_id", "also_not_an_id"),
    ],
)
def test_GetPaymentRequestStatus_returns_400_if_invalid_IDs_provided(
    make_lambda_context_object,
    make_api_gateway_event_get_payment_request_status,
    payment_requests_table,
    payment_request,
    payment_request_id,
    merchant_id,
):
    # Given
    payment_requests_repo = PaymentRequestsRepository()
    payment_requests_repo.upsert(payment_request)

    get_payment_request_status_event = make_api_gateway_event_get_payment_request_status(
        {"payment_request_id": payment_request_id, "merchant_id": merchant_id}
    )

    context = make_lambda_context_object("GetPaymentRequestStatus")

    # When
    response = lambda_handler(get_payment_request_status_event, context)

    # Then
    assert response["statusCode"] == 400
    assert "is not valid uuid", "are not valid uuids" in response["body"]
