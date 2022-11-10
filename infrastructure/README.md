# Localstack

Since deploying this solution in AWS properly is beyond the scope of this project, localstack is used to provide a local emulation of AWS.

## Setup

## Pre-requisites
Ensure you have the following tools available:

- terraform
- docker-compose
- AWS CLI
- docker / colima (Daemon must be running to host container)
- mac or linux (makefile may not work as intended on windows)


## Deploy infrastructure to localstack container

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

# Triggering the endpoints

To trigger the Lambdas you can use localstack 
and the AWS CLI.

The Makefile in the infrastructure folder provides pre-configured commands to make this
simple. Responses returned by Lambdas can be found in the /responses folder.



## Submit a valid PaymentRequest as a Merchant

Run `make valid_payment_request`

Emulates calling the POST merchant/{merchant_id}/payments/ API, which triggers the SubmitPaymentRequest Lambda.

When provided with valid input, a 201 HTTP response and a body containing the newly created PaymentRequest ID is returned.

The logs demonstrate the command being published to SQS and the subsequent triggering of the ForwardPaymentRequestToAcquiringBank Lambda. 

The payload that API Gateway would send to the Lambda can be found in infrastructure/lambda_events/SubmitPaymentRequest_valid.json

Terminal output:

<img width="1792" alt="image" src="https://user-images.githubusercontent.com/58389740/201194703-447ff99f-4417-4b1d-bf9f-65512de46b71.png">




## Submit an invalid PaymentRequest as a Merchant

Run `make invalid_payment_request`

Emulates calling the POST merchant/{merchant_id}/payments/ API with invalid input.

A body containing the validation errors and a 400 HTTP response code are returned.

You can modify the input in infrastructure/lambda_events/SubmitPaymentRequest_invalid.json to explore the behaviour.

Terminal output:

<img width="1777" alt="image" src="https://user-images.githubusercontent.com/58389740/201195656-9978bb2e-ac45-44f8-b509-d5335f536246.png">


### Get status of a PaymentRequest as a Merchant

Run `make get_payment_request_status PAYMENT_REQUEST_ID=<required_value> MERCHANT_ID=<default_provided> `

Emulates calling the GET merchant/{merchant_id}/payment/{payment_id} API, which triggers the GetPaymentRequestStatus lambda.

Terminal output:

<img width="1792" alt="image" src="https://user-images.githubusercontent.com/58389740/201201076-99f084f2-f6a6-4368-a7d0-bab266a19bd6.png">


### Provide a status update as the acquiring bank

Run `make provide_payment_request_update PAYMENT_REQUEST_ID=<id_from_above> MERCHANT_ID=<optional> RESPONSE=<optional>`

Emulates the Acquiring Bank calling the ProcessAcquiringBankResponse Lambda. In the architecture diagrams I have provided, this is connected via a VPC Endpoint Service, NLB and ALB, though there are alternative options (e.g. Private API Gateway).

Terminal output:
<img width="1569" alt="image" src="https://user-images.githubusercontent.com/58389740/201201451-cc73a2df-5c42-4212-9f23-222f4c4656ef.png">


### Simulate broken message consumer to demonstrate DLQ-ing

Run `make break_forward_payment_request`

<img width="1740" alt="image" src="https://user-images.githubusercontent.com/58389740/201210205-cf307bc7-9af8-4539-973c-685448cb1d33.png">

### Read contents of DynamoDB

#### Dump

To dump the entire local dynamodb table into a terminal, run: `make dump_dynamo`

#### Query

To query for a specific PaymentRequest, run: `make query_dynamo ID=<payment_request_id>`
