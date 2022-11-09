from shared_kernel.Command import Command


class ForwardPaymentRequestToAcquiringBank(Command):
    """
    Command that is made after successfully handling a SubmitPaymentRequest command.
    Decouples initiation from forwarding of Payment Requests, increasing availability of the PaymentRequest gateway.
    """

    def __init__(self, payment_request_id, merchant_id):
        self.payment_request_id = payment_request_id
        self.merchant_id = merchant_id

    @classmethod
    def from_json(cls, json):
        return cls(json["payment_request_id"], json["merchant_id"])
