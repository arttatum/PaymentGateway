import uuid

import pytest

from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from core.payment_request_aggregate.value_objects.AcquiringBankResponse import (
    AcquiringBankResponse,
)
from core.payment_request_aggregate.value_objects.Currency import Currency
from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.guard_clauses.uuid_guard import is_valid_uuid


def test_init_PaymentRequest_with_valid_arguments_creates_expected_object():
    merchant_id = str(uuid.uuid4())
    card_number = "12345671234567"
    expiry_date = "08-32"
    amount = 1192.34
    currency = "POUNDS"
    cvv = "999"

    submit_command = SubmitPaymentRequest(
        merchant_id, card_number, expiry_date, amount, currency, cvv
    )

    payment_request = PaymentRequest(submit_command)
    assert is_valid_uuid(payment_request.id)
    assert payment_request.merchant_id.value == merchant_id
    assert payment_request.card_number.value == "12345671234567"
    assert payment_request.expiry_date.month == "08"
    assert payment_request.expiry_date.year == "32"
    assert payment_request.amount.currency.value == Currency.POUNDS
    assert payment_request.amount.amount == 1192.34
    assert not payment_request.is_sent_to_acquiring_bank
    assert payment_request.acquiring_bank_response is None


def test_init_PaymentRequest_with_several_invalid_arguments_raises_domain_exception_with_list_of_errors():
    merchant_id = "not a uuid"
    card_number = "1234567"
    expiry_date = "008-12"
    amount = "-12.34"
    currency = "POUNDS"
    cvv = "9999"

    submit_command = SubmitPaymentRequest(
        merchant_id, card_number, expiry_date, amount, currency, cvv
    )

    with pytest.raises(DomainException) as e:
        PaymentRequest(submit_command)

    assert "Merchant ID must be a UUID-4." in e.value.messages
    assert (
        "Credit card number must be numeric, and between 8 and 19 digits long." in e.value.messages
    )
    assert "Expiry date must be in format: MM-YY" in e.value.messages
    assert "Payment amount must be greater than 0." in e.value.messages
    assert "CVV must be of length three, not 4" in e.value.messages


@pytest.mark.parametrize(
    "valid_response_message_from_bank",
    [
        AcquiringBankResponse.PAID,
        AcquiringBankResponse.PROCESSING,
        AcquiringBankResponse.FRAUD_DETECTED,
        AcquiringBankResponse.INSUFFICIENT_CREDIT,
    ],
)
def test_mark_as_forwarded_to_acquiring_bank_updates_is_sent_to_bank_flag(
    valid_response_message_from_bank,
):
    merchant_id = str(uuid.uuid4())
    card_number = "12345671234567"
    expiry_date = "08-32"
    amount = 1192.34
    currency = "POUNDS"
    cvv = "999"

    submit_command = SubmitPaymentRequest(
        merchant_id, card_number, expiry_date, amount, currency, cvv
    )

    payment_request = PaymentRequest(submit_command)
    payment_request.mark_as_forwarded_to_acquiring_bank()

    response_from_bank = AcquiringBankResponse(valid_response_message_from_bank)
    payment_request.process_acquiring_bank_response(response_from_bank)

    assert payment_request.acquiring_bank_response.value == valid_response_message_from_bank
