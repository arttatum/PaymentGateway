import os
import uuid
from unittest.mock import patch

import boto3
import pytest

from application.repositories.exceptions.NotFound import NotFound
from application.repositories.PaymentRequestsRepository import PaymentRequestsRepository
from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from core.payment_request_aggregate.value_objects.CardNumber import CardNumber
from core.payment_request_aggregate.value_objects.CVV import CVV
from tests.conftest import property_values_are_equal


def test_PaymentRequestRepository_raises_KeyError_if_table_name_env_variable_is_not_set(
    payment_requests_table,
):
    del os.environ["PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME"]
    with pytest.raises(KeyError):
        PaymentRequestsRepository()


def test_PaymentRequestRepository_upsert_inserts_item_in_db(payment_requests_table):
    # Given
    repo = PaymentRequestsRepository()

    merchant_id = str(uuid.uuid4())

    submit_payment_request = SubmitPaymentRequest(
        merchant_id, "1234123412341234", "01-24", "15.75", "POUNDS", "321"
    )

    submitted_payment_request = PaymentRequest(submit_payment_request)

    id = submitted_payment_request.id

    # When
    repo.upsert(submitted_payment_request)

    # Then
    payment_request_db_object = payment_requests_table.get_item(Key={"id": id})

    assert payment_request_db_object["Item"]["id"] == id
    assert payment_request_db_object["Item"]["merchant_id"]["value"] == merchant_id
    assert payment_request_db_object["Item"]["is_sent_to_acquiring_bank"] is False


def test_PaymentRequestRepository_upsert_updates_item_in_db(payment_requests_table):
    # Given
    repo = PaymentRequestsRepository()

    merchant_id = str(uuid.uuid4())

    submit_payment_request = SubmitPaymentRequest(
        merchant_id, "1234123412341234", "01-24", "15.75", "POUNDS", "321"
    )

    payment_request_to_forward = PaymentRequest(submit_payment_request)

    id = payment_request_to_forward.id

    repo.upsert(payment_request_to_forward)

    payment_request_to_forward.mark_as_forwarded_to_acquiring_bank()

    # When
    repo.upsert(payment_request_to_forward)

    # Then
    payment_request_db_object = payment_requests_table.get_item(Key={"id": id})

    assert payment_request_db_object["Item"]["id"] == id
    assert payment_request_db_object["Item"]["merchant_id"]["value"] == merchant_id
    assert payment_request_db_object["Item"]["is_sent_to_acquiring_bank"] is True


@pytest.mark.parametrize("not_a_payment_request", [123, "abc", {"do": "re"}, ("me",)])
def test_PaymentRequestRepository_upsert_raises_TypeError_if_passed_something_other_than_PaymentRequest_object(
    payment_requests_table, not_a_payment_request
):
    # Given
    repo = PaymentRequestsRepository()

    # When
    with pytest.raises(TypeError):
        repo.upsert(not_a_payment_request)


def test_PaymentRequestRepository_get_by_aggregate_root_id_raises_NotFound_when_item_does_not_exist(
    payment_requests_table,
):
    # Given
    repo = PaymentRequestsRepository()

    # When
    with pytest.raises(NotFound):
        repo.get_by_aggregate_root_id(str(uuid.uuid4()))


def test_PaymentRequestRepository_get_by_aggregate_root_id_returns_what_was_saved(
    payment_requests_table,
):
    # Given
    repo = PaymentRequestsRepository()

    merchant_id = str(uuid.uuid4())

    submit_payment_request = SubmitPaymentRequest(
        merchant_id, "1234123412341234", "01-24", "15.75", "POUNDS", "321"
    )

    payment_request_to_save = PaymentRequest(submit_payment_request)

    id = payment_request_to_save.id

    repo.upsert(payment_request_to_save)

    # When
    payment_request_from_repo = repo.get_by_aggregate_root_id(id)

    # Then
    assert property_values_are_equal(payment_request_from_repo, payment_request_to_save)
    assert type(payment_request_from_repo) == PaymentRequest
    assert type(payment_request_from_repo.card_number) == CardNumber
    assert type(payment_request_from_repo.cvv) == CVV


class BrokenDynamoDBResource:
    def Table(self, *args, **kwargs):
        return BrokenDynamoDBTable()


class BrokenDynamoDBTable:
    def get_item(self, *args, **kwargs):
        raise Exception("Get Item raised an Exception")

    def put_item(self, *args, **kwargs):
        raise Exception("Put Item raised an Exception")


@patch.object(boto3, "resource")
def test_PaymentRequestRepository_upsert_bubbles_exceptions_from_boto(mock_boto3, payment_request):
    # Given
    mock_boto3.return_value = BrokenDynamoDBResource()

    repo = PaymentRequestsRepository()

    with pytest.raises(Exception) as e:
        repo.upsert(payment_request)

    assert "Put Item raised an Exception" in str(e.value)


@patch.object(boto3, "resource")
def test_PaymentRequestRepository_get_by_aggregate_root_id_bubbles_exceptions_from_boto(
    mock_boto3, payment_request
):
    # Given
    mock_boto3.return_value = BrokenDynamoDBResource()

    repo = PaymentRequestsRepository()

    with pytest.raises(Exception) as e:
        repo.get_by_aggregate_root_id(payment_request.id)

    assert "Get Item raised an Exception" in str(e.value)
