from shared_kernel.Command import Command


class ProcessAcquiringBankResponse(Command):
    """
    Command sent by Acquiring Bank when they
    have an update regarding a Payment Request
    """

    def __init__(self, payment_request_id: str, response: str):
        self.payment_request_id = payment_request_id
        self.response = response
