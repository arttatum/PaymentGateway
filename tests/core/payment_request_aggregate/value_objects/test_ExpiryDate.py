import pytest

from core.payment_request_aggregate.value_objects.ExpiryDate import ExpiryDate
from shared_kernel.exceptions.DomainException import DomainException


@pytest.mark.parametrize(
    "incorrect_format_expiry_date", ["008-22", "1-23", "11_23", "11-299", "00-25"]
)
def test_ExpiryDate_must_be_mm_dash_yy_format(incorrect_format_expiry_date):
    with pytest.raises(DomainException):
        ExpiryDate(incorrect_format_expiry_date)


def test_is_in_past_returns_True_for_historic_expiry_date():
    past_expiry_date = "08-20"
    expiry_date = ExpiryDate(past_expiry_date)
    assert expiry_date.is_in_past()


def test_is_in_past_returns_False_for_future_expiry_date():
    future_expiry_date = "08-35"
    expiry_date = ExpiryDate(future_expiry_date)
    assert not expiry_date.is_in_past()
