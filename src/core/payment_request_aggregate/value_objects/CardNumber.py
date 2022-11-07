from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.ValueObject import ValueObject


class CardNumber(ValueObject):
    """Further validation and cross checking could be encapsulated in this class.

    Checksum computation, deducing the type, etc.
    """

    def __init__(self, card_number: str):
        length = len(card_number)
        if not card_number.isnumeric() or length < 8 or length > 19:
            raise DomainException(
                "Credit card number must be numeric, and between 8 and 19 digits long."
            )
        self.value = card_number

    def to_masked_card_number(self):
        return "*" * (len(self.value) - 4) + self.value[-4:]
