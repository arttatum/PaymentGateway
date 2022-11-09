import uuid, pytest
from unittest.mock import patch

import requests
from requests import Response
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from application.services.PaymentRequestService import PaymentRequestService
from core.commands.ForwardPaymentRequestToAcquiringBank import (
    ForwardPaymentRequestToAcquiringBank,
)
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.commands.ProcessAquiringBankResponse import ProcessAquiringBankResponse
from core.payment_request_aggregate.value_objects.AcquiringBankResponse import AcquiringBankResponse
from application.repositories.exceptions.NotFound import NotFound
from application.mapping.mapper import Mapper
from shared_kernel.exceptions.DomainException import DomainException

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


@patch.object(requests, "post")
def test_forward_payment_request_to_acquiring_bank_is_mostly_idempotent(
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

    service.forward_payment_request_to_aquiring_bank(
        ForwardPaymentRequestToAcquiringBank(payment_request_id, merchant_id)
    )

    # Then
    mock_post.assert_called_once()


def test_process_aquiring_bank_response_raises_NotFound_if_PaymentRequest_does_not_exist(payment_requests_table):
    command = ProcessAquiringBankResponse(str(uuid.uuid4()), AcquiringBankResponse.PAID)
    service = PaymentRequestService()
    with pytest.raises(NotFound):
        service.process_aquiring_bank_response(command)

def test_process_aquiring_bank_response_raises_DomainException_if_response_string_not_valid(payment_requests_table):
    
    command = ProcessAquiringBankResponse(str(uuid.uuid4()), AcquiringBankResponse.PAID)
    service = PaymentRequestService()
    with pytest.raises(NotFound):
        service.process_aquiring_bank_response(command)


def test_process_acquiring_bank_response_updates_PaymentRequest(payment_requests_table):
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
    payment_request.mark_as_forwarded_to_acquiring_bank()

    payment_requests_table.put_item(Item=Mapper.object_to_dict(payment_request))

    process_bank_response_command = ProcessAquiringBankResponse(payment_request.id, AcquiringBankResponse.PAID)
    service = PaymentRequestService()

    # When
    service.process_aquiring_bank_response(process_bank_response_command)

    # Then 
    payment_request_db_object = payment_requests_table.get_item(Key={"id": payment_request.id})

    assert payment_request_db_object["Item"]["id"] == payment_request.id
    assert payment_request_db_object["Item"]["merchant_id"]["value"] == merchant_id
    assert payment_request_db_object["Item"]["acquiring_bank_response"]["value"] == AcquiringBankResponse.PAID
