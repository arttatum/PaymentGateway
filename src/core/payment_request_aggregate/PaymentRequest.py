import uuid

from shared_kernel.guard_clauses.uuid_guard import is_valid_uuid


class PaymentRequest:
    """
    Aggregate for Payment
    """

    def __init__(self, merchant_id):
        if not is_valid_uuid(merchant_id):
            raise ValueError("Merchant ID is not a uuid.")

        # card number, expiry date etc TODO

        self.id = str(uuid.uuid4())
        self.merchant_id = merchant_id
        self.is_sent_to_acquiring_bank = False

    def mark_as_forwarded_to_acquiring_bank(self):
        self.is_sent_to_acquiring_bank = True

    def process_acquiring_bank_response(self):
        pass
