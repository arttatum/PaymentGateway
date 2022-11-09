from datetime import datetime

from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.ValueObject import ValueObject


class ExpiryDate(ValueObject):
    """A simil

    Args:
        ValueObject (_type_): _description_
    """

    def __init__(self, expiry_date):
        if (
            len(expiry_date) != 5
            or expiry_date[2] != "-"
            or not expiry_date[0:2].isnumeric()
            or not expiry_date[3:].isnumeric()
        ):
            raise DomainException("Expiry date must be in format: MM-YY")

        if int(expiry_date[0:2]) < 1 or int(expiry_date[0:2]) > 12:
            raise DomainException("Month must be between 01 and 12")

        self.month = expiry_date[0:2]
        self.year = expiry_date[3:5]

    def is_in_past(self):
        today = datetime.now()

        if int(f"20{self.year}") < today.year:
            return True
        elif int(f"20{self.year}") == today.year and int(self.month) < today.month:
            return True
        else:
            return False

    def __str__(self):
        return f"{self.month}-{self.year}"
