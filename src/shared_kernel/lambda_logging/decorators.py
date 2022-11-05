import functools

from shared_kernel.lambda_logging.set_up_logger import configure_context_logger, get_logger


def return_500_for_unhandled_errors(func):
    """
    Logs unhandled exceptions for the decorated function.
    Only suitable for lambdas connected to API Gateway via a Proxy Lambda Integration
    Returns 500 status code with body "Internal Server Error"
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = get_logger()
            logger.error("An unexpected error occurred.")
            # Exceptions can contain PII, so we must not log them without further inspection in Production.
            logger.debug(f"Exception: {e}")
            return {"statusCode": 500, "body": "Internal Server Error"}

    return wrapper


def configure_lambda_logger(func):
    """A decorator for lambda handlers that configures a logger with contextual information."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        context = args[1]
        function_name = context.function_name
        aws_request_id = context.aws_request_id

        configure_context_logger(function_name, aws_request_id)

        logger = get_logger()
        logger.info(f"Started execution of {function_name} lambda.")
        try:
            function_return_value = func(*args, **kwargs)
            return function_return_value
        finally:
            logger.info(f"Finished execution of {function_name} lambda.")

    return wrapper
