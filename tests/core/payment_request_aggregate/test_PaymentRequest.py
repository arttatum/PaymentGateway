import pytest

from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.PaymentRequest import PaymentRequest
from shared_kernel.exceptions.DomainException import DomainException


def test_init_PaymentRequest_with_several_invalid_arguments_raises_domain_exception_with_list_of_errors():
    merchant_id = "not a uuid"
    card_number = "1234567"
    expiry_date = "008-12"
    amount = "-12.34"
    currency = "POUNDS"
    cvv = "9999"

    submit_command = SubmitPaymentRequest(merchant_id, card_number, expiry_date, amount, currency, cvv)

    with pytest.raises(DomainException) as e:
        PaymentRequest(submit_command)

    assert "Merchant ID must be a UUID-4." in e.value.messages
    assert "Credit card number must be numeric, and between 8 and 19 digits long." in e.value.messages
    assert "Expiry date must be in format: MM-YY" in e.value.messages
    assert "Payment amount must be greater than 0." in e.value.messages
    assert "CVV must be of length three, not 4" in e.value.messages
