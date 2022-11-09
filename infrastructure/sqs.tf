
resource "aws_sqs_queue" "forward_payment_request_to_acquiring_bank" {
  name                       = "forward-payment-request-to-acquiring-bank"
  sqs_managed_sse_enabled    = true
  message_retention_seconds  = 1209600
  visibility_timeout_seconds = 30
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.forward_payment_request_to_acquiring_bank_dlq.arn
    maxReceiveCount     = 1
  })
}

resource "aws_sqs_queue" "forward_payment_request_to_acquiring_bank_dlq" {
  name                    = "forward-payment-request-to-acquiring-bank-dlq"
  sqs_managed_sse_enabled = true
}
