from decimal import Decimal

from core.payment_request_aggregate.value_objects.Currency import Currency
from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.ValueObject import ValueObject


class MonetaryAmount(ValueObject):
    def __init__(self, amount, currency):
        # Note, I am aware this initialisation will not collect all errors, should currency and amount be invalid.
        # A similar pattern as is used in the command initialisation could support this.

        try:
            amount = Decimal(amount)
        except Exception:
            raise DomainException("Amount could not be parsed to a decimal type.")

        self.currency = Currency(currency)

        if amount <= 0:
            raise DomainException("Payment amount must be greater than 0.")

        self.amount = amount
