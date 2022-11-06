from shared_kernel.lambda_logging.decorators import configure_lambda_logger
from shared_kernel.lambda_logging.set_up_logger import get_logger


@configure_lambda_logger
def good_mock_lambda(event, context):
    logger = get_logger()
    logger.info("This record will have aws_request_id and function name attributes")
    logger.info("So will this!")
    return {"statusCode": 202, "body": "Accepted"}


class AWSLambdaContext:
    def __init__(self, function_name, aws_request_id):
        self.function_name = function_name
        self.aws_request_id = aws_request_id


def test_configure_lambda_logger_wraps_lambda_execution_with_started_and_finished_messages(capsys):
    function_name = "a_great_name"
    context = AWSLambdaContext(function_name, "12345")

    good_mock_lambda(None, context)

    logs_from_lambda = capsys.readouterr().err

    assert f"Started execution of {function_name} lambda." in logs_from_lambda
    assert f"Finished execution of {function_name} lambda." in logs_from_lambda
