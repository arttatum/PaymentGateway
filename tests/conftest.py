import os

import boto3
import pytest
from moto import mock_dynamodb

from application.mapping.mapper import Mapper


@pytest.fixture(autouse=True, scope="function")
def moto_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME = "payment_requests"


@pytest.fixture(autouse=True, scope="function")
def payment_requests_table_name_env_variable():
    os.environ["PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME"] = PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME


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


def property_values_are_equal(some_object, another_object):
    some_object = Mapper.object_to_dict(some_object)
    another_object = Mapper.object_to_dict(another_object)

    for property, value in some_object.items():
        if another_object[property] != value:
            return False
    return True
