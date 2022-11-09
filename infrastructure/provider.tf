provider "aws" {
  access_key                  = "test"
  secret_key                  = "test"
  region                      = "eu-west-2"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    lambda         = "http://localhost:4566"
    dynamodb       = "http://localhost:4566"
    sqs            = "http://localhost:4566"
    secretsmanager = "http://localhost:4566"
  }
}
