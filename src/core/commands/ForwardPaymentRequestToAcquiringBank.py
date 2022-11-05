class ForwardPaymentRequestToAcquiringBank:
    """
    Command that is made after successfully handling a InitiatePaymentRequest command.
    Decouples initiation from forwarding of Payment Requests, increasing availability of the PaymentRequest gateway.
    """

    pass
