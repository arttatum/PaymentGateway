import os

import boto3


class AWSClient:
    @staticmethod
    def get_dynamodb_resource():
        if os.environ.get("LOCALSTACK_HOSTNAME"):
            return boto3.resource(
                "dynamodb", endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:4566"
            )
        else:
            return boto3.resource("dynamodb")

    @staticmethod
    def get_sqs_resource():
        if os.environ.get("LOCALSTACK_HOSTNAME"):
            return boto3.resource(
                "sqs", endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:4566"
            )
        else:
            return boto3.resource("sqs")

    @staticmethod
    def get_secretsmanager_client():
        if os.environ.get("LOCALSTACK_HOSTNAME"):
            return boto3.client(
                service_name="secretsmanager",
                region_name="eu-west-2",
                endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:4566",
            )
        else:
            return boto3.client(service_name="secretsmanager", region_name="eu-west-2")
