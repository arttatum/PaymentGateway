resource "aws_lambda_event_source_mapping" "trigger_ForwardPaymentRequestToAquiringBank_from_command_queue" {
  event_source_arn = aws_sqs_queue.forward_payment_request_to_acquiring_bank.arn
  function_name    = aws_lambda_function.ForwardPaymentRequestToAquiringBank.arn
  batch_size       = 1
}
