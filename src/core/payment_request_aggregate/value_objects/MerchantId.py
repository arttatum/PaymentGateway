from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.guard_clauses.uuid_guard import is_valid_uuid
from shared_kernel.ValueObject import ValueObject


class MerchantId(ValueObject):
    def __init__(self, merchant_id: str):
        if not is_valid_uuid(merchant_id):
            raise DomainException("Merchant ID must be a UUID-4.")

        self.value = merchant_id
