import pytest

from shared_kernel.exceptions.DomainException import DomainException
from core.payment_request_aggregate.value_objects.Currency import Currency

def test_unsupported_currency_raises_domain_exception():
    invalid_currency = "YEN"
    with pytest.raises(DomainException) as e:
        Currency(invalid_currency)

    assert "Currency type: YEN is not supported." in e.value.messages[0]
    