import os
from unittest.mock import ANY, patch

import pytest
import requests
from requests import Response

from application.clients.AcquiringBankClient import AcquiringBankClient
from application.mapping.mapper import Mapper


def test_if_ACQUIRING_BANK_API_KEY_SECRET_NAME_is_not_set_client_raises_KeyError(
    api_key_secret_in_secretsmanager,
):
    del os.environ["ACQUIRING_BANK_API_KEY_SECRET_NAME"]
    with pytest.raises(KeyError):
        AcquiringBankClient()


def test_if_ACQUIRING_BANK_POST_PAYMENT_REQUEST_URL_is_not_set_client_raises_KeyError(
    api_key_secret_in_secretsmanager,
):
    del os.environ["ACQUIRING_BANK_POST_PAYMENT_REQUEST_URL"]
    with pytest.raises(KeyError):
        AcquiringBankClient()


@patch.object(requests, "post")
def test_post_payment_request_does_not_call_over_http_when_in_localstack(
    mock_post_payment_request, payment_request, localstack_environment_variable
):
    # Given
    acquiring_bank_client = AcquiringBankClient()
    # When
    acquiring_bank_client.post_payment_request(payment_request)

    mock_post_payment_request.assert_not_called()


@patch.object(requests, "post")
def test_post_payment_request_happy_path(
    mock_post, payment_request, api_key_secret_in_secretsmanager
):
    # Given
    post_response = Response()
    post_response.status_code = 204
    mock_post.return_value = post_response
    acquiring_bank_client = AcquiringBankClient()
    # When
    acquiring_bank_client.post_payment_request(payment_request)

    mock_post.assert_called_once()
    mock_post.assert_called_with(
        ANY,
        timeout=30,
        json=Mapper.object_to_json_string(payment_request),
        headers={"x-api-key": ANY},
    )


@pytest.mark.parametrize("failure_code", [400, 404, 403, 500, 502])
@patch.object(requests, "post")
def test_post_payment_request_non_2xx_response(
    mock_post, failure_code, payment_request, api_key_secret_in_secretsmanager
):
    # Given
    post_response = Response()
    post_response.status_code = failure_code
    mock_post.return_value = post_response
    acquiring_bank_client = AcquiringBankClient()

    # When, then raises
    with pytest.raises(Exception):
        acquiring_bank_client.post_payment_request(payment_request)
