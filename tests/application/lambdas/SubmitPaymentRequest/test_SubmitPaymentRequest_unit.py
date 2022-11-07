import uuid
from unittest.mock import patch

from application.lambdas.SubmitPaymentRequest.lambda_function import lambda_handler
from application.services.PaymentRequestService import PaymentRequestService
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.guard_clauses.uuid_guard import is_valid_uuid


@patch.object(PaymentRequestService, "submit_payment_request")
def test_SubmitPaymentRequest_returns_500_if_event_is_invalid(
    mock_service_submit_payment_request, make_api_gateway_event, make_lambda_context_object
):
    event = make_api_gateway_event()
    context = make_lambda_context_object("SubmitPaymentRequest")

    del event["pathParameters"]

    response = lambda_handler(event, context)
    assert response["statusCode"] == 500
    assert response["body"] == "Internal Server Error"

    mock_service_submit_payment_request.assert_not_called()


@patch.object(PaymentRequestService, "submit_payment_request")
@patch.object(SubmitPaymentRequest, "__init__")
def test_SubmitPaymentRequest_returns_400_if_initialisation_of_command_raises_domain_exception(
    mock_command_init, mock_service_submit_payment_request, make_api_gateway_event, make_lambda_context_object
):
    mock_command_init.side_effect = DomainException("Price cannot be negative.")

    event = make_api_gateway_event()
    context = make_lambda_context_object("SubmitPaymentRequest")

    response = lambda_handler(event, context)

    assert response["statusCode"] == 400
    assert response["body"] == ["Price cannot be negative."]

    mock_command_init.assert_called_once()
    mock_service_submit_payment_request.assert_not_called()


@patch.object(PaymentRequestService, "submit_payment_request")
@patch.object(SubmitPaymentRequest, "__init__")
def test_SubmitPaymentRequest_returns_201_and_new_payment_request_id_if_successful(
    mock_command_init, mock_service_submit_payment_request, make_api_gateway_event, make_lambda_context_object
):
    # Given
    new_payment_request_id = str(uuid.uuid4())
    mock_command_init.return_value = None
    mock_service_submit_payment_request.return_value = new_payment_request_id
    event = make_api_gateway_event()
    context = make_lambda_context_object("SubmitPaymentRequest")

    # When
    response = lambda_handler(event, context)

    # Then
    assert response["statusCode"] == 201
    assert response["body"] == new_payment_request_id
    mock_service_submit_payment_request.assert_called_once()
    mock_command_init.assert_called_once()
