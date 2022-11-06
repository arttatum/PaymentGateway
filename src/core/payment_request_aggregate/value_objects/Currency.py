from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.ValueObject import ValueObject


class Currency(ValueObject):
    _supported_currencies = ["POUNDS", "EUROS", "DOLLARS"]

    def __init__(self, currency: str):
        if currency not in Currency._supported_currencies:
            raise DomainException(f"Currency type: {currency} is not supported.")

        self.value = currency
