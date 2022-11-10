import json
import uuid
from unittest.mock import patch

import pytest

from application.lambdas.ProcessAcquiringBankResponse.lambda_function import (
    lambda_handler,
)
from application.services.PaymentRequestService import PaymentRequestService
from core.payment_request_aggregate.value_objects.AcquiringBankResponse import (
    AcquiringBankResponse,
)
from shared_kernel.exceptions.DomainException import DomainException


@patch.object(PaymentRequestService, "process_acquiring_bank_response")
def test_ProcessAcquiringBankResponse_returns_200_if_successful(
    mock_process_bank_response, make_lambda_context_object
):
    event = {
        "body": json.dumps(
            {
                "payment_request_id": str(uuid.uuid4()),
                "merchant_id": str(uuid.uuid4()),
                "response": AcquiringBankResponse.INSUFFICIENT_CREDIT,
            }
        )
    }
    response = lambda_handler(event, make_lambda_context_object("ProcessAcquiringBankResponse"))
    assert response["statusCode"] == 200
    assert response["body"] == "Success"


@patch.object(PaymentRequestService, "process_acquiring_bank_response")
def test_ProcessAcquiringBankResponse_returns_400_if_merchant_id_field_missing(
    mock_process_bank_response, make_lambda_context_object
):
    event = {
        "body": json.dumps(
            {
                "payment_request_id": str(uuid.uuid4()),
                "response": AcquiringBankResponse.INSUFFICIENT_CREDIT,
            }
        )
    }
    response = lambda_handler(event, make_lambda_context_object("ProcessAcquiringBankResponse"))
    assert response["statusCode"] == 400
    assert response["body"] == "Bad request, required field: 'merchant_id' missing."


@patch.object(PaymentRequestService, "process_acquiring_bank_response")
def test_ProcessAcquiringBankResponse_returns_400_if_payment_request_id_field_missing(
    mock_process_bank_response, make_lambda_context_object
):
    event = {
        "body": json.dumps(
            {
                "merchant_id": str(uuid.uuid4()),
                "response": AcquiringBankResponse.INSUFFICIENT_CREDIT,
            }
        )
    }
    response = lambda_handler(event, make_lambda_context_object("ProcessAcquiringBankResponse"))
    assert response["statusCode"] == 400
    assert response["body"] == "Bad request, required field: 'payment_request_id' missing."


@patch.object(PaymentRequestService, "process_acquiring_bank_response")
def test_ProcessAcquiringBankResponse_returns_400_if_response_field_missing(
    mock_process_bank_response, make_lambda_context_object
):
    event = {
        "body": json.dumps(
            {
                "payment_request_id": str(uuid.uuid4()),
                "merchant_id": str(uuid.uuid4()),
            }
        )
    }
    response = lambda_handler(event, make_lambda_context_object("ProcessAcquiringBankResponse"))
    assert response["statusCode"] == 400
    assert response["body"] == "Bad request, required field: 'response' missing."


@patch.object(PaymentRequestService, "process_acquiring_bank_response")
def test_ProcessAcquiringBankResponse_returns_500_if_lambda_event_does_not_have_body(
    mock_process_bank_response, make_lambda_context_object
):
    event = {}
    response = lambda_handler(event, make_lambda_context_object("ProcessAcquiringBankResponse"))
    assert response["statusCode"] == 500
    assert response["body"] == "Internal Server Error"


@pytest.mark.parametrize("is_stringified_json", [True, False])
@patch.object(PaymentRequestService, "process_acquiring_bank_response")
def test_ProcessAcquiringBankResponse_returns_400_if_service_raises_domain_exception(
    mock_process_bank_response, is_stringified_json, make_lambda_context_object
):
    mock_process_bank_response.side_effect = DomainException("An invariant was violated.")
    event = {
        "body": {
            "payment_request_id": str(uuid.uuid4()),
            "merchant_id": str(uuid.uuid4()),
            "response": AcquiringBankResponse.INSUFFICIENT_CREDIT,
        }
    }
    if is_stringified_json:
        event["body"] = json.dumps(event["body"])

    response = lambda_handler(event, make_lambda_context_object("ProcessAcquiringBankResponse"))
    assert response["statusCode"] == 400
    assert response["body"] == ["An invariant was violated."]
