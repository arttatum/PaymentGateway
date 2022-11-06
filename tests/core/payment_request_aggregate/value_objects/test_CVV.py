from shared_kernel.exceptions.DomainException import DomainException
from core.payment_request_aggregate.value_objects.CVV import CVV
import pytest
def test_CVV_must_be_of_length_three():
    invalid_cvv = "3928"
    with pytest.raises(DomainException) as e:
        CVV(invalid_cvv)

    assert "CVV must be of length three" in e.value.messages[0]


def test_CVV_must_be_a_numeric_string():
    invalid_cvv = "A28"
    with pytest.raises(DomainException) as e:
        CVV(invalid_cvv)

    assert "CVV must be a numeric string." in e.value.messages[0]
    