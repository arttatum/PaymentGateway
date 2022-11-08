# Payment Gateway

A simple MVP for a payment gateway.

## Features:

- Make a Payment Request as a Merchant.

- Forward Payment Request to Acquiring Bank.

- Provide update regarding a Payment Request as an Acquiring Bank.

- Get the latest status of a Payment Request as a Merchant.


## What I have delivered today, what I would deliver given more time

The below diagrams illustrate how I would suggest deploying this solution, given more time. The designs aim to optimise for performance, security, scalability, and cost.

For expediency, I have focussed solely on the Lambdas at the core of these designs, the DynamoDB table, and the SQS queue that decouples accepting payment requests from merchants and forwarding them on to an Acquiring Bank.

To enable testing and demonstration in a local environment, without requiring provisioning and deployment to an AWS environemnt, I have opted to use localstack[https://localstack.cloud/].

### Merchant Makes Payment Request

![Merchant_MakePaymentRequest](https://user-images.githubusercontent.com/58389740/200094893-f41303fb-c995-4e4c-be10-48c27e341fb8.svg)
[Merchant_MakePaymentRequest.pdf](https://github.com/arttatum/PaymentGateway/files/9942662/Merchant_MakePaymentRequest.pdf)


### Acquiring Bank Sends Payment Request Update

![AcquiringBank_SendPaymentRequestUpdate](https://user-images.githubusercontent.com/58389740/200094906-91c4c3db-3154-486c-8c55-cbb5f62febe7.svg)
[AcquiringBank_SendPaymentRequestUpdate.pdf](https://github.com/arttatum/PaymentGateway/files/9942664/AcquiringBank_SendPaymentRequestUpdate.pdf)

### Merchant Asks For Latest Status On Payment Request

![Merchant_GetPaymentRequestStatus](https://user-images.githubusercontent.com/58389740/200094898-28f993d9-1b76-432a-9d9f-2cef245e571b.svg)
[Merchant_GetPaymentRequestStatus.pdf](https://github.com/arttatum/PaymentGateway/files/9942663/Merchant_GetPaymentRequestStatus.pdf)


## Running the tests locally

#### Pre-requesites
- pip3
- pyenv

If you do not have python 3.9.13 installed, it will be installed when you run any `make` command. 

A python virtual environment is used to manage dependencies in a consistent manner. All commands are run within an activated virtual environment automatically.

## Run the unit test suite

Enter the root directory of the repository in your terminal, then run `make unit` 

## Run the linter 

`make lint`

## Run the prettifier

`make pretty`

## Running the system using localstack

TBD

## Internal Software Design

### Domain Driven Design

Some tactical patterns of domain driven design are employed here: Aggregate / Value Object / Repository / Command / Application Service.

Due to the time constraints when building this system and the nature of Python, properly implementing these patterns was out of scope, but their spirit lives on (I hope)!


### Hexagonal Architecture / Ports and Adapters

The core of the system is expressed in infrastructure ignorant terms.

Requests are routed to Lambdas through various means (SQS, ALB, API Gateway).

Due to this strategy, adding additional Ports (API GW / Load Balancer / Manual Trigger / SQS / ...) or Adapters (to translate external events into commands for domain model) does not have an impact on the core of the system and can be more easily managed.

## Layers

### Infrastructure

AWS configuration code (terraform).

### Application

Driven by Lambda, the core compute technology used here.

Responsibilities:
- Interfaces with other AWS services (API GW, SQS, ALB, DynamoDB).
- Insulates Core of system from external concerns. 
- Translates incoming requests into Commands (or Queries).
- Delegates business logic to Core of system.

### Core

Pure expression of business logic, infrastructure ignorant.

The only aggregate modelled here is the PaymentRequest. The Merchant aggregate is referenced by it's ID.

### Shared Kernel

A slight misuse of the term, this folder contains the code that is required across all layers (Guard clauses, logging)
