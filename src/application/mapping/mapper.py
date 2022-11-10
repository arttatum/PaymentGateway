import json

from shared_kernel.lambda_logging.set_up_logger import get_logger


class Mapper:
    """
    Provides a simple mechanism to map json / dicts into nested python objects.
    """

    def __init__(self) -> None:
        self.attribute_mappers = {}
        self.target_type = None
        self.is_list_mapper = False
        self.logger = get_logger()

    @classmethod
    def for_type(cls, target_type: type):
        """Configure mapper for the specified target type.

        Args:
            target_type (type): The type to map to.

        Raises:
            TypeError: If target_type is not a type

        Returns:
            Mapper: The configured Mapper

        Usage:
            book_mapper = Mapper().for_type(Book)
        """
        if not isinstance(target_type, type):
            raise TypeError("The target_type argument must be a type (class).")

        mapper = cls()
        mapper.target_type = target_type
        return mapper

    @classmethod
    def for_list_of(cls, target_type: type):
        """Configure mapper for a list of the specified target type.

        Args:
            target_type (type): The type to map each item in a list to.

        Returns:
            Mapper: The configured Mapper

        Usage:
            book_mapper = Mapper().for_type(Book).with_attribute_mappings(
                chapters=Mapper().for_list_of(Chapter)
            )
        """
        mapper = cls.for_type(target_type)
        mapper.is_list_mapper = True
        return mapper

    def with_attribute_mappings(self, **kwargs):
        """Configure Mappers for attributes of the target_type.
        Argument name: attribute name
        Argument value: Mapper for that attribute

        Raises:
            ValueError: If method is called without any arguments
            TypeError: If value provided for any argument is not a Mapper

        Returns:
            Mapper: The configured Mapper

        Usage:
            book_mapper = Mapper().for_type(Book).with_attribute_mappings(
                author=Mapper().for_type(Author)
                chapters=Mapper().for_list_of(Chapter)
            )
        """
        if len(kwargs) < 1:
            raise ValueError("No attribute mappings were provided.")

        for attribute_name, attribute_mapper in kwargs.items():
            if not isinstance(attribute_mapper, Mapper):
                raise TypeError(
                    f"Required instance of Mapper, received {attribute_mapper.__name__}"
                )
            self.attribute_mappers[attribute_name] = attribute_mapper
        return self

    def from_json(self, json) -> object:
        """Given a dict / json, return an object of type: target_type

        Notably, this maps child attributes to the types declared
        the using .with_child_attributes(...) method

        Args:
            json (dict): json/dict to map.

        Raises:
            ValueError: If input is not a dict

        Returns:
            target_type: An instance of the target_type
        """
        self.logger.debug(f"Mapping JSON to object of type: {self.target_type}")
        self.logger.debug(f"JSON to map: {json}")
        if type(json) is not dict:
            error_message = "Expected a dict as input."
            self.logger.info(error_message)
            raise TypeError(error_message)

        instance = object.__new__(self.target_type)

        for attribute_name, value in json.items():
            if not self._has_attribute_mapper(attribute_name) or value is None:
                setattr(instance, attribute_name, value)
                continue

            attribute_mapper = self.attribute_mappers[attribute_name]

            if attribute_mapper.is_list_mapper:
                if type(value) is not list:
                    error_message = f"The mapper was configured to process a list, but a {type(value)} was received."
                    self.logger.info(error_message)
                    raise ValueError(error_message)
                self._map_to_list(instance, attribute_name, value, attribute_mapper)
                continue

            if type(value) is not dict:
                setattr(instance, attribute_name, attribute_mapper.target_type(value))
                continue

            setattr(instance, attribute_name, attribute_mapper.from_json(value))
            continue

        return instance

    def _has_attribute_mapper(self, property):
        return self.attribute_mappers.get(property) is not None

    def _map_to_list(self, instance, attribute_name, value, attribute_mapper):
        setattr(instance, attribute_name, list(self._map_iterable(attribute_mapper, value)))

    def _map_iterable(self, child_mapper, value):
        for item in value:
            yield child_mapper.from_json(item)

    @staticmethod
    def object_to_dict(obj: object) -> dict:
        """Given an object, returns it's dict (json) representation.
        Useful when trying to persist aggregate roots to json based data stores (dynamodb).

        Args:
            obj (object): The object to map

        Returns:
            dict: the dictionary representation of the object
        """
        return json.loads(Mapper.object_to_json_string(obj))

    @staticmethod
    def object_to_json_string(obj: object) -> str:
        """Given an object, returns it's string representation.

        Args:
            obj (object): the object

        Returns:
            str: the string representation
        """
        return json.dumps(obj, default=lambda o: getattr(o, "__dict__", str(o)))
