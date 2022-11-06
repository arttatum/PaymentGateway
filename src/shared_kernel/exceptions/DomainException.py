class DomainException(Exception):
    def __init__(self, message: str = None):
        self.messages = []
        if message:
             self.messages.append(message)

    @classmethod
    def from_multiple_messages(cls, messages: list[str]):
        instance = cls()
        for message in messages:
            instance.messages.append(message)
        return instance
