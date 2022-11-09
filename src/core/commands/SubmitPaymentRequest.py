from shared_kernel.Command import Command


class SubmitPaymentRequest(Command):
    """
    Command sent by Merchant when making a Payment Request.
    """

    def __init__(self, merchant_id, card_number, expiry_date, amount, currency, cvv):
        self.merchant_id = merchant_id
        self.card_number = card_number
        self.expiry_date = expiry_date
        self.amount = amount
        self.currency = currency
        self.cvv = cvv
