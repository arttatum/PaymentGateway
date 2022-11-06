from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.ValueObject import ValueObject


class CVV(ValueObject):
    def __init__(self, cvv):
        if len(cvv) != 3:
            raise DomainException(f"CVV must be of length three, not {len(cvv)}")

        if type(cvv) != str or not cvv.isnumeric():
            raise DomainException("CVV must be a numeric string.")

        self.value = cvv
