from shared_kernel.lambda_logging.decorators import return_500_for_unhandled_errors


@return_500_for_unhandled_errors
def bad_mock_lambda(event, context):
    raise Exception()


def test_return_500_for_unhandled_errors_works():
    response_from_lambda_that_raised_exception = bad_mock_lambda()

    assert response_from_lambda_that_raised_exception["statusCode"] == 500
    assert response_from_lambda_that_raised_exception["body"] == "Internal Server Error"
