from core.commands.ForwardPaymentRequestToAcquiringBank import (
    ForwardPaymentRequestToAcquiringBank,
)
from core.commands.InitiatePaymentRequest import InitiatePaymentRequest
from core.commands.ProcessAquiringBankResponse import ProcessAquiringBankResponse


class PaymentRequestService:
    def initiate_payment_request(self, command: InitiatePaymentRequest):
        # create PaymentRequest
        # save it
        # publish command to queue
        pass

    def forward_payment_request_to_aquiring_bank(self, command: ForwardPaymentRequestToAcquiringBank):
        # get payment request aggregate root
        # transform to payload expected by aquiring bank
        # send over http
        # call method on payment request: mark_as_forwarded_to_acquiring_bank
        # update payment request aggregate root
        pass

    def process_aquiring_bank_response(self, command: ProcessAquiringBankResponse):
        # get payment request aggregate root
        # call method on object: process_aquiring_bank_response
        # update payment request aggregate root
        pass
