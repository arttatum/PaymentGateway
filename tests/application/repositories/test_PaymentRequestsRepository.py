import os
import uuid

import pytest
from moto import mock_dynamodb

from application.repositories.exceptions.NotFound import NotFound
from application.repositories.PaymentRequestsRepository import PaymentRequestsRepository
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from tests.conftest import property_values_are_equal

# TODO: Mock out dymabo's put_item() and get_item() methods to simulate failed connection to dynamodb.

# Using moto provides virtual dynamodb, which allows us to test behaviours in a more realistic fashion,
# but it is not suitable for simulating random errors.


def test_PaymentRequestRepository_raises_KeyError_if_table_name_env_variable_is_not_set(payment_requests_table):
    del os.environ["PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME"]
    with pytest.raises(KeyError):
        PaymentRequestsRepository()


def test_PaymentRequestRepository_upsert_inserts_item_in_db(payment_requests_table):
    # Given
    repo = PaymentRequestsRepository()

    merchant_id = str(uuid.uuid4())

    initiated_payment_request = PaymentRequest(merchant_id)

    id = initiated_payment_request.id

    # When
    repo.upsert(initiated_payment_request)

    # Then
    clearance_db_object = payment_requests_table.get_item(Key={"id": id})

    assert clearance_db_object["Item"]["id"] == id
    assert clearance_db_object["Item"]["merchant_id"] == merchant_id
    assert clearance_db_object["Item"]["is_sent_to_acquiring_bank"] is False


def test_PaymentRequestRepository_upsert_updates_item_in_db(payment_requests_table):
    # Given
    repo = PaymentRequestsRepository()

    merchant_id = str(uuid.uuid4())

    payment_request_to_forward = PaymentRequest(merchant_id)

    id = payment_request_to_forward.id

    repo.upsert(payment_request_to_forward)

    payment_request_to_forward.mark_as_forwarded_to_acquiring_bank()

    # When
    repo.upsert(payment_request_to_forward)

    # Then
    clearance_db_object = payment_requests_table.get_item(Key={"id": id})

    assert clearance_db_object["Item"]["id"] == id
    assert clearance_db_object["Item"]["merchant_id"] == merchant_id
    assert clearance_db_object["Item"]["is_sent_to_acquiring_bank"] is True


@pytest.mark.parametrize("not_a_payment_request", [123, "abc", {"do": "re"}, ("me",)])
def test_PaymentRequestRepository_upsert_updates_item_in_db(payment_requests_table, not_a_payment_request):
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


def test_PaymentRequestRepository_get_by_aggregate_root_id_returns_what_was_saved(payment_requests_table):
    # Given
    repo = PaymentRequestsRepository()

    merchant_id = str(uuid.uuid4())

    payment_request_to_save = PaymentRequest(merchant_id)

    id = payment_request_to_save.id

    repo.upsert(payment_request_to_save)

    # When
    payment_request_from_repo = repo.get_by_aggregate_root_id(id)

    # Then
    assert property_values_are_equal(payment_request_from_repo, payment_request_to_save)
    assert type(payment_request_to_save) == type(payment_request_from_repo)
