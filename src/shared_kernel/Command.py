from shared_kernel.exceptions.DomainException import DomainException


class Command:
    def __init__(self):
        self.initialisation_domain_exceptions = []

    def add_domain_exception(self, domain_exception: DomainException):
        self.initialisation_domain_exceptions.append(domain_exception)

    def domain_exceptions_raised(self) -> bool:
        return len(self.initialisation_domain_exceptions) > 0

    def raise_domain_exceptions(self):
        messages = []
        for domain_exception in self.initialisation_domain_exceptions:
            messages.append(str(domain_exception))
        raise DomainException.from_multiple_messages(messages)
