# Localstack

Since deploying this solution in AWS properly is beyond the scope of this project, localstack is used to provide a local emulation of AWS.

## Setup

### Pre-requisites
Ensure you have the following tools available:

- terraform
- docker-compose
- docker / colima (Daemon must be running to host container)


### Deploy infrastructure to localstack container

Ensure that colima or docker are running.

Run `make localstack` from the infrastructure directory.

You will be prompted to enter some AWS credentials. Provide the following values:

    ```
    AWS Access Key ID: test
    AWS Secret Access Key: test
    Region: eu-west-2
    Output: json
    ```

Following this:
- The deployable zip containing the lambda code + dependencies will be generated.
- The container running localstack will be started.
- Terraform will deploy the infrastructure to this container.

## Triggering the endpoints

To trigger the Lambdas (that would be integrated with load balancers or API GW), you can use localstack 
and the aws cli. The Makefile in the infrastructure folder provides pre-configured commands to make this
simple.

Responses for endpoints that Lambdas that return a value can be found in the /responses folder.

### Submit a valid PaymentRequest as a Merchant

To view this in action, run `make valid_payment_request`

This will generate a new PaymentRequest. The ID can be found in the SubmitPaymentRequest.txt file.

### Submit an invalid PaymentRequest as a Merchant

To view this in action, run `make invalid_payment_request`

### Get status of a PaymentRequest as a Merchant

To view this in action, run `make get_payment_request_status PAYMENT_REQUEST_ID=<required_value> MERCHANT_ID=<default_provided> `

### Provide a status update as the acquiring bank

To view this in action, run `make provide_payment_request_update PAYMENT_REQUEST_ID=<required_value> MERCHANT_ID=<default_provided> RESPONSE=<default_provided>`

Valid statuses are: 
- Processing
- Paid into account
- Payment could not be reconciled - insufficient credit
- Payment could not be reconciled - fraud detected

### Simulate broken message consumer to demonstrate DLQ-ing

Run `make break_forward_payment_request`

### Read contents of DynamoDB

#### Dump

To dump the entire local dynamodb table into a terminal, run: `make dump_dynamo`

#### Query

To query for a specific PaymentRequest, run: `make query_dynamo ID=<payment_request_id>`