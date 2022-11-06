import pytest

from core.payment_request_aggregate.value_objects.MonetaryAmount import MonetaryAmount
from shared_kernel.exceptions.DomainException import DomainException


def test_negative_amount_results_in_domain_exception():
    amount = -12
    currency = "POUNDS"

    with pytest.raises(DomainException) as e:
        MonetaryAmount(amount, currency)

    assert "Payment amount must be greater than 0." in e.value.messages[0]
