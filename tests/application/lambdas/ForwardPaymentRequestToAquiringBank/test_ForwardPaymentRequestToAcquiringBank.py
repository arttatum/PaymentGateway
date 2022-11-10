import json
import uuid
from unittest.mock import patch

import pytest

from application.lambdas.ForwardPaymentRequestToAcquiringBank.lambda_function import (
    lambda_handler,
)
from application.services.PaymentRequestService import PaymentRequestService


@patch.object(PaymentRequestService, "forward_payment_request_to_acquiring_bank")
def test_lambda_parses_event_and_calls_forward_payment_request_to_acquiring_bank_service_method(
    mock_forward_to_bank_service_method, make_lambda_context_object
):
    payment_request_id = str(uuid.uuid4())
    merchant_id = str(uuid.uuid4())
    sqs_lambda_event = {
        "Records": [
            {
                "body": json.dumps(
                    {"payment_request_id": payment_request_id, "merchant_id": merchant_id}
                )
            }
        ]
    }

    lambda_handler(
        sqs_lambda_event, make_lambda_context_object("ForwardPaymentRequestToAcquiringBank")
    )

    mock_forward_to_bank_service_method.assert_called_once()


@pytest.mark.parametrize(
    "body_with_missing_key",
    [
        {"merchant_id": str(uuid.uuid4())},
        {"payment_request_id": str(uuid.uuid4())},
        {},
        {"hello": "world"},
    ],
)
def test_lambda_does_not_handle_key_error_so_message_would_be_DLQd(
    body_with_missing_key, make_lambda_context_object
):
    unprocessable_sqs_lambda_event = {"Records": [{"body": json.dumps(body_with_missing_key)}]}
    with pytest.raises(KeyError):
        lambda_handler(
            unprocessable_sqs_lambda_event,
            make_lambda_context_object("ForwardPaymentRequestToAcquiringBank"),
        )
