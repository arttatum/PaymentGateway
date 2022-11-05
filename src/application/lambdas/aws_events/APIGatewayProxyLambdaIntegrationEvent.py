import json


class APIGatewayEvent:
    """
    Summary: Class to parse API Gateway Proxy Lambda Integration event
    """

    @classmethod
    def from_dict(cls, event: dict):
        """Given an event that is a dict, convert it to an object to clean lambda

        Args:
            event (dict): _description_

        Returns:
            _type_: _description_
        """
        instance = cls()

        for key, value in event.items():
            if key == "body":
                # Convert body from stringified json (with escape characters) into dict type
                value = json.loads(value)

            setattr(instance, key, value)

        return instance
