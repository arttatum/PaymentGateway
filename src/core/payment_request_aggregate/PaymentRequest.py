from core.commands.SubmitPaymentRequest import SubmitPaymentRequest
from core.payment_request_aggregate.value_objects.AcquiringBankResponse import (
    AcquiringBankResponse,
)
from core.payment_request_aggregate.value_objects.CardNumber import CardNumber
from core.payment_request_aggregate.value_objects.CVV import CVV
from core.payment_request_aggregate.value_objects.ExpiryDate import ExpiryDate
from core.payment_request_aggregate.value_objects.MerchantId import MerchantId
from core.payment_request_aggregate.value_objects.MonetaryAmount import MonetaryAmount
from shared_kernel.AggregateRoot import AggregateRoot
from shared_kernel.exceptions.DomainException import DomainException


class PaymentRequest(AggregateRoot):
    """
    Aggregate for Payment
    """

    def __init__(self, submit_payment_request: SubmitPaymentRequest):
        super().__init__()
        try:
            self.merchant_id = MerchantId(submit_payment_request.merchant_id)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.card_number = CardNumber(submit_payment_request.card_number)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.expiry_date = ExpiryDate(submit_payment_request.expiry_date)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.cvv = CVV(submit_payment_request.cvv)
        except DomainException as e:
            self.add_domain_exception(e)

        try:
            self.amount = MonetaryAmount(
                submit_payment_request.amount, submit_payment_request.currency
            )
        except DomainException as e:
            self.add_domain_exception(e)

        self.is_sent_to_acquiring_bank = False
        self.acquiring_bank_response = None

        if self.domain_exceptions_raised():
            self.raise_domain_exceptions()

    def mark_as_forwarded_to_acquiring_bank(self):
        self.is_sent_to_acquiring_bank = True

    def process_acquiring_bank_response(self, response: AcquiringBankResponse):
        """Processes response from acquiring bank.

        Assumption has been made thatthe bank provides a
        string containing the status in a request body, and
        we simply need to store that string as the new status
        of the PaymentRequest.

        Args:
            response (str): Response recieved by AcquiringBank
        """

        self.acquiring_bank_response = response
