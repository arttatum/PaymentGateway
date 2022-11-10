import os
from unittest.mock import patch

import boto3

from application.clients.AWSClient import AWSClient


@patch.object(boto3, "resource")
def test_AWSClient_get_dynamodb_resource_adds_endpoint_url_when_in_localstack(
    mock_boto3_resource_method, localstack_environment_variable
):
    AWSClient.get_dynamodb_resource()
    mock_boto3_resource_method.assert_called_with(
        "dynamodb", endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:4566"
    )

    del os.environ["LOCALSTACK_HOSTNAME"]
    AWSClient.get_dynamodb_resource()
    mock_boto3_resource_method.assert_called_with("dynamodb")


@patch.object(boto3, "resource")
def test_AWSClient_get_sqs_resource_adds_endpoint_url_when_in_localstack(
    mock_boto3_resource_method, localstack_environment_variable
):
    AWSClient.get_sqs_resource()
    mock_boto3_resource_method.assert_called_with(
        "sqs", endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:4566"
    )

    del os.environ["LOCALSTACK_HOSTNAME"]
    AWSClient.get_sqs_resource()
    mock_boto3_resource_method.assert_called_with("sqs")


@patch.object(boto3, "client")
def test_AWSClient_get_secretsmanager_client_adds_endpoint_url_when_in_localstack(
    mock_boto3_resource_method, localstack_environment_variable
):
    AWSClient.get_secretsmanager_client()
    mock_boto3_resource_method.assert_called_with(
        service_name="secretsmanager",
        region_name="eu-west-2",
        endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:4566",
    )

    del os.environ["LOCALSTACK_HOSTNAME"]
    AWSClient.get_secretsmanager_client()
    mock_boto3_resource_method.assert_called_with(
        service_name="secretsmanager", region_name="eu-west-2"
    )
