# Default values
MERCHANT_ID ?= 0b20e14d-0122-4b60-824a-fcc4c2a3b52a
RESPONSE ?= Paid into account

# prtinf formatting
RESET_FORMAT := "\e[0m%s\n"
LINE_BREAK := "\e\n\e[0m%s\n"
GREEN_BOLD := "\e[32;1m%s\n"
GREEN_ITALIC := "\e[32;3m%s\n"
AMBER_BOLD := "\e[33;1m%s\n"
RED_BOLD := "\e[31;1m%s\n"
LIST_ITEM := "\e[0m\t%s\n"

.PHONY: deployable_zip
deployable_zip: ## Bundle python code and dependencies into a zip file. ## Usage: make deployable_zip
	@printf "Building deployable zip..."
	@cd ..; source make_lambda_zip.sh

.PHONY: configure_aws
configure_aws:
	@aws configure --profile local

.PHONY: localstack
localstack:  ## Spin up localstack (AWS emulator) in a docker container. Deploy infra and code to it. ## Usage: make localstack
	make configure_aws
	@printf "Setting up localstack container..."
	@docker-compose -f docker-compose-localstack.yml down
	@make deployable_zip
	@docker-compose -f docker-compose-localstack.yml up -d
	@printf "Deploying AWS components to container..."
	@terraform init
	@terraform apply --auto-approve

.PHONY: valid_payment_request
valid_payment_request: ## Call POST /payments endpoint with valid Payment Request details. Uses details from .json file. ## Usage: make valid_payment_request
	@printf $(RED_BOLD) "Ctrl+C to quit..."
	@printf $(AMBER_BOLD) "Calling SubmitPaymentRequest lambda..."
	$(eval UNIX_TIME_START = $(shell date +%s))

	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://lambda_events/SubmitPaymentRequest_valid.json \
	--region eu-west-2 \
	responses/SubmitPaymentRequest.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d > /dev/null 2>&1

	@printf $(GREEN_BOLD) "SubmitPaymentRequest ran to completion! A command was published to an SQS queue."
	@sleep 3
	@printf $(LIST_ITEM) "The ForwardPaymentRequestToAcquiringBank Lambda processes these commands as they come into SQS..." 
	@sleep 3
	@printf $(LIST_ITEM) "It is running in background now, on the localstack docker container..."
	@sleep 3
	@printf $(LIST_ITEM) "In a few moments we can view the logs from the container..."
	@sleep 3
	@printf $(RESET_FORMAT) "Logs:"
	@docker logs localstack_payment_gateway --since $(UNIX_TIME_START) | grep -E 'message|sqs' | cut -d " " -f 2- | awk '{if ($$0 ~ "\"message\"") {printf "> %s\n", $$0} else {printf "- {\"message\": \"%s\"}\n", $$0 }}'	
	@printf $(LINE_BREAK) ""
	@printf $(GREEN_BOLD) "Response:"
	@cat responses/SubmitPaymentRequest.txt | python -m json.tool
	@printf $(LINE_BREAK) ""
	@printf $(GREEN_ITALIC) "Next, try running: 'make get_payment_request_status PAYMENT_REQUEST_ID=<the_id_above>'"

.PHONY: invalid_payment_request
invalid_payment_request: ## Call POST /payments endpoint with invalid Payment Request details. Uses details from .json file. ## Usage: make invalid_payment_request
	@printf $(RED_BOLD) "Ctrl+C to quit..."
	@printf $(AMBER_BOLD) "Submitting a payment request with invalid details..."
	$(eval UNIX_TIME_START = $(shell date +%s))

	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://lambda_events/SubmitPaymentRequest_invalid.json \
	--region eu-west-2 \
	responses/SubmitPaymentRequest_invalid.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d > /dev/null 2>&1
	@sleep 1
	@printf $(RESET_FORMAT) "Logs:"
	@docker logs localstack_payment_gateway --since $(UNIX_TIME_START) | grep -E 'message|sqs'
	@printf $(LINE_BREAK) ""

	@printf $(RED_BOLD) "Response:"
	@cat responses/SubmitPaymentRequest_invalid.txt | python -m json.tool


.PHONY: get_payment_request_status
get_payment_request_status: ## Call GET /status endpoint as a Merchant. ## Usage: make get_payment_request_status PAYMENT_REQUEST_ID=...(required) MERCHANT_ID=...(optional)
	@printf $(RED_BOLD) "Ctrl+C to quit..."
	@printf $(AMBER_BOLD) "Getting status of Payment Request..."
	@printf $(RESET_FORMAT) ""
	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name GetPaymentRequestStatus \
	--profile local \
	--payload "{\"pathParameters\": {\"merchant_id\": \"$(MERCHANT_ID)\", \"payment_request_id\": \"$(PAYMENT_REQUEST_ID)\"}}" \
	--region eu-west-2 \
	responses/GetPaymentRequestStatus.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d
	@printf $(LINE_BREAK) ""
	@printf $(GREEN_BOLD) "Response:"
	@cat responses/GetPaymentRequestStatus.txt | python -m json.tool
	@printf $(LINE_BREAK) ""

	@printf $(GREEN_ITALIC) "Next, try running: 'make provide_payment_request_update PAYMENT_REQUEST_ID=<the_id_above>'"


.PHONY: provide_payment_request_update
provide_payment_request_update: ## Simulate the Acquiring Bank sending a response to a Payment Request. ## Usage: make provide_payment_request_update PAYMENT_REQUEST_ID=...(required) MERCHANT_ID=...(optional) RESPONSE=...(optional)
	@printf $(RED_BOLD) "Ctrl+C to quit..."
	@printf $(AMBER_BOLD) "Calling ProcessAcquiringBankResponse lambda..."
	@printf $(RESET_FORMAT) ""
	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name ProcessAcquiringBankResponse \
	--profile local \
	--payload  "{\"body\": {\"merchant_id\": \"$(MERCHANT_ID)\", \"payment_request_id\": \"$(PAYMENT_REQUEST_ID)\", \"response\": \"$(RESPONSE)\"}}" \
	--region eu-west-2 \
	responses/ProcessAcquiringBankResponse.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d

	@printf $(LINE_BREAK) ""
	@printf $(GREEN_BOLD) "Response:"
	@cat responses/ProcessAcquiringBankResponse.txt | python -m json.tool
	@printf $(LINE_BREAK) ""

	@printf $(RESET_FORMAT) "Valid responses from the acquiring bank are:" 
	@printf $(LIST_ITEM) "- Processing" 
	@printf $(LIST_ITEM) "- Paid into account" 
	@printf $(LIST_ITEM) "- Payment could not be reconciled - insufficient credit" 
	@printf $(LIST_ITEM) "- Payment could not be reconciled - fraud detected" 
	@printf $(LINE_BREAK) ""

	@printf $(GREEN_ITALIC) "Try setting a response yourself like so 'make provide_payment_request_update RESPONSE=...'"
	@printf "Or try running 'make get_payment_request_status' again...."


.PHONY: dump_dynamo
dump_dynamo: ## Display entire contents of local DynamoDB. ## Usage: make dump_dynamo
	@aws --endpoint-url=http://localhost:4566 dynamodb scan \
	--profile local \
	--table-name="payment_requests"

query_dynamo: ## Get DynamoDB entry by ID. ## Usage: make query_dynamo PAYMENT_REQUEST_ID=...(required)
	@aws --endpoint-url=http://localhost:4566 dynamodb query \
	--profile local \
	--table-name "payment_requests" \
	--key-condition-expression "id = :id" \
	--expression-attribute-values "{\":id\": {\"S\": \"$(PAYMENT_REQUEST_ID)\"}}"

.PHONY: demo_dlq
demo_dlq: ## Break ForwardPaymentRequestToAcquiringBank lambda config. Watch the message get DLQ'd. ## Usage: make break_forward_payment_request
	@printf $(RED_BOLD) "Breaking the ForwardPaymentRequestToAcquiringBank lambda configuration!"
	$(eval UNIX_TIME_START = $(shell date +%s))
	@aws --endpoint-url=http://localhost:4566 \
	lambda update-function-configuration --function-name ForwardPaymentRequestToAcquiringBank \
	--profile local \
	--region eu-west-2 \
	--handler "not_a_real_method" > /dev/null 2>&1
	
	@printf $(AMBER_BOLD) "Calling SubmitPaymentRequest lambda..."
	@printf $(LINE_BREAK) ""

	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://lambda_events/SubmitPaymentRequest_valid.json \
	--region eu-west-2 \
	responses/SubmitPaymentRequest.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d
	@printf $(LINE_BREAK) ""

	@printf $(GREEN_BOLD) "SubmitPaymentRequest ran to completion! A command was published to an SQS queue."
	@printf $(RESET_FORMAT) ""
	@printf $(LIST_ITEM) "In the background, the ForwardPaymentRequestToAcquiringBank is failing, due to a (deliberate) configuration issue" 
	@sleep 3
	@printf $(LIST_ITEM) "The message it fails to process will be added to the DLQ."
	@sleep 3
	@printf $(LIST_ITEM) "In a few moments we will parse the logs to show this journey..."
	@sleep 1
	@printf $(RESET_FORMAT) "Logs:"
	@docker logs localstack_payment_gateway --since $(UNIX_TIME_START) | grep -E sqs\|failed  | cut -d " " -f 2- | awk '{ printf "- {\"message\": \"%s\"}\n", $$0 }'	
	@printf $(LINE_BREAK) ""

	@printf $(AMBER_BOLD) "Querying DLQ for messages..."
	@aws --endpoint-url=http://localhost:4566 \
	sqs get-queue-attributes --queue-url https://sqs.eu-west-2.amazonaws.com/000000000000/forward-payment-request-to-acquiring-bank-dlq \
	--attribute-names ApproximateNumberOfMessages
	@printf $(LINE_BREAK) ""

	@printf $(GREEN_ITALIC) "These messages could be automatically replayed, sent through a reconciliation process, and/or trigger alerts for developers or other systems to respond to..."

	@aws --endpoint-url=http://localhost:4566 \
	lambda update-function-configuration --function-name ForwardPaymentRequestToAcquiringBank \
	--profile local \
	--region eu-west-2 \
	--handler "application.lambdas.ForwardPaymentRequestToAcquiringBank.lambda_function.lambda_handler" > /dev/null 2>&1

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = "##"}; {printf "\n\033[0;34m%-32s \033[0;32m%s\n %-34s\033[3;36m%s\n", $$1, $$2,"", $$3}'
