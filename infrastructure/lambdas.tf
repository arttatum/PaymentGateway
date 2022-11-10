resource "aws_lambda_function" "ForwardPaymentRequestToAcquiringBank" {
  function_name    = "ForwardPaymentRequestToAcquiringBank"
  filename         = "../payment_gateway_lambdas.zip"
  role             = "fake_role" # localstack doesn't support IAM in community edition
  handler          = "application.lambdas.ForwardPaymentRequestToAcquiringBank.lambda_function.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("../payment_gateway_lambdas.zip")
  timeout          = 30
  environment {
    variables = {
      PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME    = aws_dynamodb_table.payment_requests.name
      QUIET_LOGS                              = "true"
    }
  }
}


resource "aws_lambda_function" "GetPaymentRequestStatus" {
  function_name    = "GetPaymentRequestStatus"
  filename         = "../payment_gateway_lambdas.zip"
  role             = "fake_role" # localstack doesn't support IAM in community edition
  handler          = "application.lambdas.GetPaymentRequestStatus.lambda_function.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("../payment_gateway_lambdas.zip")
  timeout          = 30
  environment {
    variables = {
      PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME = aws_dynamodb_table.payment_requests.name
      QUIET_LOGS                           = "true"
    }
  }
}


resource "aws_lambda_function" "ProcessAcquiringBankResponse" {
  function_name    = "ProcessAcquiringBankResponse"
  filename         = "../payment_gateway_lambdas.zip"
  role             = "fake_role" # localstack doesn't support IAM in community edition
  handler          = "application.lambdas.ProcessAcquiringBankResponse.lambda_function.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("../payment_gateway_lambdas.zip")
  timeout          = 30
  environment {
    variables = {
      PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME = aws_dynamodb_table.payment_requests.name
      QUIET_LOGS                           = "true"
    }
  }
}


resource "aws_lambda_function" "SubmitPaymentRequest" {
  function_name    = "SubmitPaymentRequest"
  filename         = "../payment_gateway_lambdas.zip"
  role             = "fake_role" # localstack doesn't support IAM in community edition
  handler          = "application.lambdas.SubmitPaymentRequest.lambda_function.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("../payment_gateway_lambdas.zip")
  timeout          = 30
  environment {
    variables = {
      PAYMENT_REQUESTS_DYNAMODB_TABLE_NAME   = aws_dynamodb_table.payment_requests.name
      PAYMENT_REQUESTS_TO_FORWARD_QUEUE_NAME = aws_sqs_queue.forward_payment_request_to_acquiring_bank.name
      QUIET_LOGS                             = "true"
    }
  }
}
