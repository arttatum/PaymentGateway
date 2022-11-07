import uuid

from application.services.PaymentRequestService import PaymentRequestService
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
