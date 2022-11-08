import uuid
from unittest.mock import patch

import requests
from requests import Response

from application.services.PaymentRequestService import PaymentRequestService
from core.commands.ForwardPaymentRequestToAcquiringBank import (
    ForwardPaymentRequestToAcquiringBank,
)
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest


def test_submit_payment_request_adds_payment_request_to_dynamodb_and_sends_command_message_to_sqs(
    payment_requests_table, payment_requests_to_forward_queue
):
    # Given
    service = PaymentRequestService()
    merchant_id = str(uuid.uuid4())
    command = SubmitPaymentRequest(
        merchant_id, "1234123412341234", "01-24", "15.75", "POUNDS", "321"
    )

    # When
    payment_request_id = service.submit_payment_request(command)

    # Then
    payment_request_db_object = payment_requests_table.get_item(Key={"id": payment_request_id})

    assert payment_request_db_object["Item"]["id"] == payment_request_id
    assert payment_request_db_object["Item"]["merchant_id"]["value"] == merchant_id
    assert payment_request_db_object["Item"]["is_sent_to_acquiring_bank"] is False

    messages_on_queue = payment_requests_to_forward_queue.receive_messages()

    assert len(messages_on_queue) == 1


@patch.object(requests, "post")
def test_forward_payment_request_to_acquiring_bank_calls_AcquiringBankClient_and_updates_payment_reqeuest_aggregate(
    mock_post,
    payment_requests_table,
    api_key_secret_in_secretsmanager,
    payment_requests_to_forward_queue,
):
    # Given
    post_response = Response()
    post_response.status_code = 204
    mock_post.return_value = post_response

    service = PaymentRequestService()
    merchant_id = str(uuid.uuid4())
    command = SubmitPaymentRequest(
        merchant_id, "1234123412341234", "01-24", "15.75", "POUNDS", "321"
    )
    payment_request_id = service.submit_payment_request(command)

    # When
    service.forward_payment_request_to_aquiring_bank(
        ForwardPaymentRequestToAcquiringBank(payment_request_id, merchant_id)
    )

    # Then
    mock_post.assert_called_once()
    payment_request_db_object = payment_requests_table.get_item(Key={"id": payment_request_id})
    assert payment_request_db_object["Item"]["id"] == payment_request_id
    assert payment_request_db_object["Item"]["merchant_id"]["value"] == merchant_id
    assert payment_request_db_object["Item"]["is_sent_to_acquiring_bank"] is True
