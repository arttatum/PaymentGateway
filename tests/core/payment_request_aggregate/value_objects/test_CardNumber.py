from shared_kernel.exceptions.DomainException import DomainException
from core.payment_request_aggregate.value_objects.CardNumber import CardNumber
import pytest

@pytest.mark.parametrize("invalid_card_number",
[
    "a1231231123",
    "1234567",
    "12345678912345678912342"
])
def test_card_number_must_be_numeric_and_correct_length(invalid_card_number):
    with pytest.raises(DomainException) as e:
        CardNumber(invalid_card_number)

    assert "Credit card number must be numeric, and between 8 and 19 digits long." in e.value.messages[0]

@pytest.mark.parametrize(("card_number", "masked_card_number"),
[
    ("123123123", "*****3123"),
    ("123123123123", "********3123")
])
def test_to_masked_card_number_hides_all_digits_except_last_four(card_number, masked_card_number):
    card_number_value_object = CardNumber(card_number)
    assert card_number_value_object.to_masked_card_number() == masked_card_number
