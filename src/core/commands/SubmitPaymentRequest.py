from core.payment_request_aggregate.value_objects.CardNumber import CardNumber
from core.payment_request_aggregate.value_objects.CVV import CVV
from core.payment_request_aggregate.value_objects.ExpiryDate import ExpiryDate
from core.payment_request_aggregate.value_objects.MerchantId import MerchantId
from core.payment_request_aggregate.value_objects.MonetaryAmount import MonetaryAmount
from shared_kernel.Command import Command
from shared_kernel.exceptions.DomainException import DomainException


class SubmitPaymentRequest(Command):
    """
    Command sent by Merchant when making a Payment Request.
    """

    def __init__(self, merchant_id, card_number, expiry_date, amount, currency, cvv):
        super().__init__()
        try:
            self.merchant_id = MerchantId(merchant_id)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.card_number = CardNumber(card_number)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.expiry_date = ExpiryDate(expiry_date)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.cvv = CVV(cvv)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.amount = MonetaryAmount(amount, currency)
        except DomainException as e:
            self.add_domain_exception(e)

        if self.domain_exceptions_raised():
            self.raise_domain_exceptions()
