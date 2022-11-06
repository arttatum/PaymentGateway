from shared_kernel.exceptions.DomainException import DomainException
from shared_kernel.lambda_logging.decorators import (
    return_400_for_domain_exceptions,
    return_500_for_unhandled_exceptions,
)


@return_500_for_unhandled_exceptions
def exception_mock_lambda(event, context):
    raise Exception()


@return_400_for_domain_exceptions
def domain_exception_mock_lambda(event, context):
    raise DomainException("The price cannot be negative.")


def test_return_500_for_unhandled_exceptions_works():
    response_from_lambda_that_raised_exception = exception_mock_lambda(None, None)

    assert response_from_lambda_that_raised_exception["statusCode"] == 500
    assert response_from_lambda_that_raised_exception["body"] == "Internal Server Error"


def test_return_400_for_domain_exceptions_works():
    response_from_lambda_that_raised_domain_exception = domain_exception_mock_lambda(None, None)

    assert response_from_lambda_that_raised_domain_exception["statusCode"] == 400
    assert response_from_lambda_that_raised_domain_exception["body"] == "The price cannot be negative."
