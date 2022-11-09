
resource "aws_dynamodb_table" "payment_requests" {
  name           = "payment_requests"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }
}
