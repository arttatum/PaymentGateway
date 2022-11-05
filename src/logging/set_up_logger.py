import logging
from logging import LoggerAdapter
import os

from pythonjsonlogger import jsonlogger

logger_with_adapter = None


def _get_environment_variable_log_level():
    environment_variable_log_level = os.getenv("LOG_LEVEL", "INFO")

    # This method returns a number when given the name, and a name when given a number
    log_level_number = logging.getLevelName(environment_variable_log_level)

    # Default to INFO if invalid log level is specified in environment variable 
    if log_level_number == "Level %s":
        return logging.INFO

    return log_level_number


def configure_context_logger(
    *args, **kwargs
):
    logger = logging.getLogger()

    # Remove AWS configured log handler, or loggers configured for previous runs of the lambda
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    logHandler = logging.StreamHandler()
    logger.addHandler(logHandler)
    logger.setLevel(_get_environment_variable_log_level())

    formatter = jsonlogger.JsonFormatter(fmt="%(levelname)s %(message)s", timestamp=True)

    logHandler.setFormatter(formatter)
    logger.propagate = False

    adapter_data = {}

    for argument_name, argument_value in kwargs.items():
        adapter_data[argument_name] = argument_value

    global logger_with_adapter
    logger_with_adapter = logging.LoggerAdapter(
        logger,
        adapter_data,
    )


def add_context(logger: LoggerAdapter, key: str, value: object):
    """Adds contextual information to all subsequent logs.

    Args:
        logger (LoggerAdapter): the logger
        key (str): name of attribute to display in log records
        value (object / any): value of attribute to display in log records
    """
    logger.extra[key] = value


def get_logger():
    """Gets the singleton instance of the logger.

    Returns:
        Logger: a logger
    """
    global logger_with_adapter
    if logger_with_adapter is None:
        configure_context_logger()
    return logger_with_adapter
