# PaymentGateway

A simple MVP for a payment gateway.

# Features:

- Make a Payment Request as a Merchant.

- Forward Payment Request to Acquiring Bank.

- Provide update regarding a Payment Request as an Acquiring Bank.

- Get the latest status of a Payment Request as a Merchant.


### Merchant Makes Payment Request

![Merchant_MakePaymentRequest](https://user-images.githubusercontent.com/58389740/200094893-f41303fb-c995-4e4c-be10-48c27e341fb8.svg)
[Merchant_MakePaymentRequest.pdf](https://github.com/arttatum/PaymentGateway/files/9942662/Merchant_MakePaymentRequest.pdf)


### Acquiring Bank Sends Payment Request Update

![AcquiringBank_SendPaymentRequestUpdate](https://user-images.githubusercontent.com/58389740/200094906-91c4c3db-3154-486c-8c55-cbb5f62febe7.svg)
[AcquiringBank_SendPaymentRequestUpdate.pdf](https://github.com/arttatum/PaymentGateway/files/9942664/AcquiringBank_SendPaymentRequestUpdate.pdf)

### Merchant Asks For Latest Status On Payment Request

![Merchant_GetPaymentRequestStatus](https://user-images.githubusercontent.com/58389740/200094898-28f993d9-1b76-432a-9d9f-2cef245e571b.svg)
[Merchant_GetPaymentRequestStatus.pdf](https://github.com/arttatum/PaymentGateway/files/9942663/Merchant_GetPaymentRequestStatus.pdf)


## Layers

### Infrastructure

AWS configuration code (terraform).

### Application

Driven by Lambda, the core compute technology used.

Responsibilities:
- Interfaces with other AWS services (API GW, SQS, ALB, DynamoDB).
- Translates external requests into Commands understood by the domain model.
- Delegates business logic services / aggregate roots.

### Core

Pure expression of business logic, infrastructure ignorant.

The only aggregate modelled here is the PaymentRequest. The Merchant aggregate is referenced by it's ID.

### Shared Kernel

A slight misuse of the term, this folder contains the code that is required across all layers.

For now: logging
