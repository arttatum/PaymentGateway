import json
import os
import uuid

import boto3
import pytest
from moto import mock_dynamodb, mock_secretsmanager, mock_sqs

from application.mapping.mapper import Mapper
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.PaymentRequest import PaymentRequest

PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME = "payment_requests"
PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME = "payment_requests_to_forward"
ACQUIRING_BANK_API_KEY_SECRET_NAME = "api_key_secret_id"
ACQUIRING_BANK_POST_PAYMENT_REQUEST_URL = "acquiringbank.api.com/payments/requests"


@pytest.fixture(autouse=True, scope="function")
def moto_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"
    os.environ["PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME"] = PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME
    os.environ["PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME"] = PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME
    os.environ["ACQUIRING_BANK_API_KEY_SECRET_NAME"] = ACQUIRING_BANK_API_KEY_SECRET_NAME
    os.environ["ACQUIRING_BANK_POST_PAYMENT_REQUEST_URL"] = ACQUIRING_BANK_POST_PAYMENT_REQUEST_URL


@pytest.fixture(scope="function")
def dynamodb():
    with mock_dynamodb():
        yield boto3.resource("dynamodb")


@pytest.fixture(scope="function")
def payment_requests_table(dynamodb):
    dynamodb.create_table(
        TableName=PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    yield dynamodb.Table(PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME)


@pytest.fixture(scope="function")
def secretsmanager():
    with mock_secretsmanager():
        yield boto3.client("secretsmanager")


@pytest.fixture(scope="function")
def api_key_secret_in_secretsmanager(secretsmanager):
    secretsmanager.create_secret(
        Name=ACQUIRING_BANK_API_KEY_SECRET_NAME, SecretString="178s3290vds"
    )


@pytest.fixture(scope="function")
def sqs():
    with mock_sqs():
        yield boto3.resource("sqs")


@pytest.fixture(scope="function")
def payment_requests_to_forward_queue(sqs):
    sqs.create_queue(QueueName=PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME)
    yield sqs.get_queue_by_name(QueueName=PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME)


def property_values_are_equal(some_object, another_object):
    some_object = Mapper.object_to_dict(some_object)
    another_object = Mapper.object_to_dict(another_object)

    for property, value in some_object.items():
        if another_object[property] != value:
            return False
    return True


@pytest.fixture(scope="session")
def make_api_gateway_event() -> dict:
    default_post_payment_request_body = {
        "card_number": "123456123456",
        "cvv": "374",
        "expiry_date": "12-26",
        "amount": 99.99,
        "currency": "POUNDS",
    }

    def build_api_gateway_event(
        payload: dict = default_post_payment_request_body,
        path_parameters: dict = {"merchant_id": str(uuid.uuid4())},
    ):
        return {
            "resource": "",
            "path": "",
            "pathParameters": path_parameters,
            "httpMethod": "",
            "headers": {},
            "requestContext": {"resourcePath": "", "httpMethod": ""},
            "body": json.dumps(payload),
        }

    return build_api_gateway_event


@pytest.fixture(scope="session")
def make_lambda_context_object():
    class AWSLambdaContext:
        def __init__(self, function_name, aws_request_id):
            self.function_name = function_name
            self.aws_request_id = aws_request_id

    def build_lambda_context_object(function_name, aws_request_id="182731916"):
        return AWSLambdaContext(function_name, aws_request_id)

    return build_lambda_context_object


@pytest.fixture(scope="session")
def payment_request():
    return PaymentRequest(
        SubmitPaymentRequest(str(uuid.uuid4()), "1234123412341234", "11-32", 12.94, "POUNDS", "019")
    )
