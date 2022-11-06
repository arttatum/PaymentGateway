import json
import os
import uuid

import boto3
import pytest
from moto import mock_dynamodb, mock_sqs

from application.mapping.mapper import Mapper

PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME = "payment_requests"
PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME = "payment_requests_to_forward"


@pytest.fixture(autouse=True, scope="function")
def moto_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"
    os.environ["PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME"] = PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME
    os.environ["PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME"] = PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME


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
    def build_api_gateway_event(payload: dict = {}, path_parameters: dict = {"merchant_id": str(uuid.uuid4())}):
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
