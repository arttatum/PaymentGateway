from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.ValueObject import ValueObject


class AcquiringBankResponse(ValueObject):
    PROCESSING = "Processing"
    PAID = "Paid into account"
    INSUFFICIENT_CREDIT = "Payment could not be reconciled - insufficient credit"
    FRAUD_DETECTED = "Payment could not be reconciled - fraud detected"

    _valid_statuses = [PROCESSING, PAID, INSUFFICIENT_CREDIT, FRAUD_DETECTED]

    def __init__(self, response_message: str):
        if response_message not in AcquiringBankResponse._valid_statuses:
            raise DomainException(f"Response message: {response_message} is not supported.")
        self.value = response_message
