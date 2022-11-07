import uuid

from application.lambdas.SubmitPaymentRequest.lambda_function import lambda_handler


def test_SubmitPaymentRequest_creates_item_in_database_and_publishes_message_to_queue(
    make_api_gateway_event, make_lambda_context_object, payment_requests_table, payment_requests_to_forward_queue
):
    # Given
    merchant_id = str(uuid.uuid4())
    event = make_api_gateway_event(path_parameters={"merchant_id": merchant_id})
    context = make_lambda_context_object("SubmitPaymentRequest")

    # When
    response = lambda_handler(event, context)

    # Then
    assert response["statusCode"] == 201
    payment_request_item = payment_requests_table.get_item(
        Key={
            "id": response["body"],
        }
    )["Item"]
    assert payment_request_item["merchant_id"]["value"] == merchant_id

    messages_on_queue = payment_requests_to_forward_queue.receive_messages()
    assert len(messages_on_queue) == 1
