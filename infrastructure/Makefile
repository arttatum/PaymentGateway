# Default value
MERCHANT_ID ?= 0b20e14d-0122-4b60-824a-fcc4c2a3b52a
RESPONSE ?= Paid into account

.PHONY: deployable_zip
deployable_zip:
	@printf "Building deployable zip..."
	@cd ..; source make_lambda_zip.sh

.PHONY: configure_aws
configure_aws:
	@aws configure --profile local

.PHONY: localstack
localstack: configure_aws
	@printf "Setting up localstack container..."
	@docker-compose -f docker-compose-localstack.yml down
	@make deployable_zip
	@docker-compose -f docker-compose-localstack.yml up -d
	@printf "Deploying AWS components to container..."
	@terraform init
	@terraform apply --auto-approve

.PHONY: valid_payment_request
valid_payment_request: 
	@printf "\e[31;1m%s\n" "Ctrl+C to quit..."
	@printf "\e[33;1m%s\n" "Calling SubmitPaymentRequest lambda..."
	$(eval UNIX_TIME_START = $(shell date +%s))

	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://lambda_events/SubmitPaymentRequest_valid.json \
	--region eu-west-2 \
	responses/SubmitPaymentRequest.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d > /dev/null 2>&1

	@printf "\e[32;1m%s\n\n" "SubmitPaymentRequest ran to completion! A command was published to an SQS queue."
	@sleep 3
	@printf "\e[31;0m %s\n" "The ForwardPaymentRequestToAcquiringBank Lambda processes these commands as they come into SQS..." 
	@sleep 3
	@printf "\e[31;0m %s\n" "It is running in background now, on the localstack docker container..."
	@sleep 3
	@printf "\e[31;0m %s\n" "In a few moments we can view the logs from the container..."
	@sleep 3
	@printf "\e[34;1m\n\n%s\n\n" "Logs:"
	@docker logs localstack_payment_gateway --since $(UNIX_TIME_START) | grep -E 'message|sqs'
	@printf "\e[32;1m\n%s\n\n" "Response:"
	@cat responses/SubmitPaymentRequest.txt
	@printf "\e[32;3m\n\n%s\n\n" "Next, try running: 'make get_payment_request_status PAYMENT_REQUEST_ID=<the_id_above>'"
	
.PHONY: invalid_payment_request
invalid_payment_request: 
	@printf "\e[33;1m\n%s\n" "Submitting a payment request with invalid details..."
	$(eval UNIX_TIME_START = $(shell date +%s))

	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://lambda_events/SubmitPaymentRequest_invalid.json \
	--region eu-west-2 \
	responses/SubmitPaymentRequest_invalid.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d > /dev/null 2>&1
	@sleep 1
	@printf "\e[34;1m\n%s\n\n" "Logs:"
	@docker logs localstack_payment_gateway --since $(UNIX_TIME_START) | grep -E 'message|sqs'

	@printf "\e[31;1m\n\n%s\n\n" "Response:"
	@cat responses/SubmitPaymentRequest_invalid.txt | python -m json.tool


.PHONY: get_payment_request_status
get_payment_request_status:
	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name GetPaymentStatus \
	--profile local \
	--payload "{\"pathParameters\": {\"merchant_id\": \"$(MERCHANT_ID)\", \"payment_request_id\": \"$(PAYMENT_REQUEST_ID)\"}}" \
	--region eu-west-2 \
	responses/GetPaymentStatus.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d
	@printf "\e[32;1m\n\n%s\n" "Retrieved status of Payment request!"
	@printf "\e[34;1m%s\n" "Response:"
	@cat responses/GetPaymentStatus.txt | python -m json.tool
	@printf "\e[32;3m\n\n%s\n\n" "Next, try running: 'make provide_payment_request_update PAYMENT_REQUEST_ID=<the_id_above>'"


.PHONY: provide_payment_request_update
provide_payment_request_update:
	@printf "\e[33;1m%s\n" "Calling ProcessAcquiringBankResponse lambda..."
	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name ProcessAcquiringBankResponse \
	--profile local \
	--payload  "{\"body\": {\"merchant_id\": \"$(MERCHANT_ID)\", \"payment_request_id\": \"$(PAYMENT_REQUEST_ID)\", \"response\": \"$(RESPONSE)\"}}" \
	--region eu-west-2 \
	responses/ProcessAcquiringBankResponse.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d

	@printf "\e[32;1m\n\n%s\n\n" "ProcessAcquiringBankResponse finished!"
	@printf "\e[34;1m%s\n" "Response:"
	@cat responses/ProcessAcquiringBankResponse.txt | python -m json.tool
	@printf "\e[32;3m\n%s\n" "Valid responses from the acquiring bank are:" "- Processing" "- Paid into account" "- Payment could not be reconciled - insufficient credit" "- Payment could not be reconciled - fraud detected" 
	@printf "\e[32;3m\n%s\n\n" "Try setting a response yourself like so 'make provide_payment_request_update RESPONSE=an_invalid_response'"
	@printf "\e[32;3m\n%s\n\n" "Or try running 'make get_payment_request_status' again...."


.PHONY: dump_dynamo
dump_dynamo:
	@aws --endpoint-url=http://localhost:4566 dynamodb scan \
	--profile local \
	--table-name="payment_requests"

query_dynamo:
	@aws --endpoint-url=http://localhost:4566 dynamodb query \
	--profile local \
	--table-name "payment_requests" \
	--key-condition-expression "id = :id" \
	--expression-attribute-values "{\":id\": {\"S\": \"$(ID)\"}}"

.PHONY: break_forward_payment_request
break_forward_payment_request:
	@printf "\e[31;1m\n%s\n" "Breaking the ForwardPaymentRequestToAquiringBank lambda configuration!"
	@aws --endpoint-url=http://localhost:4566 \
	lambda update-function-configuration --function-name ForwardPaymentRequestToAquiringBank \
	--profile local \
	--region eu-west-2 \
	--handler "not_a_real_method" > /dev/null 2>&1
	
	@printf "\e[33;1m\n%s\n" "Calling SubmitPaymentRequest lambda..."

	@aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://lambda_events/SubmitPaymentRequest_valid.json \
	--region eu-west-2 \
	responses/SubmitPaymentRequest.txt  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d

	@printf "\e[32;1m\n\n%s\n\n" "SubmitPaymentRequest ran to completion! A command was published to an SQS queue."
	@printf "\e[34;1m\n  %s\n\n" "In the background, the ForwardPaymentRequestToAquiringBank is failing, due to a (deliberate) configuration issue" 
	@sleep 3
	@printf "\e[34;1m\n  %s\n\n" "The message it fails to process will be added to the DLQ."
	@sleep 3
	@printf "\e[34;1m\n  %s\n\n" "In a few moments we will parse the logs to show this journey..."
	@sleep 3
	@docker logs localstack_payment_gateway --since 40s | sed -n '/arn:aws:sqs:eu-west-2:000000000000:forward-payment-request-to-acquiring-bank/p'

	@printf "\e[33;1m\n%s\n" "Querying DLQ for messages..."

	@aws --endpoint-url=http://localhost:4566 \
	sqs get-queue-attributes --queue-url https://sqs.eu-west-2.amazonaws.com/000000000000/forward-payment-request-to-acquiring-bank-dlq \
	--attribute-names ApproximateNumberOfMessages
	@printf "\e[32;1m\n%s\n\n" "These messages could be automatically replayed, sent through a reconciliation process, and trigger alerts to developers or other systems..."

	@printf "\e[32;1m\n%s\n\n" "Fixing the Lambda configuration for ForwardPaymentRequestToAquiringBank..."
	@aws --endpoint-url=http://localhost:4566 \
	lambda update-function-configuration --function-name ForwardPaymentRequestToAquiringBank \
	--profile local \
	--region eu-west-2 \
	--handler "application.lambdas.ForwardPaymentRequestToAquiringBank.lambda_function.lambda_handler" > /dev/null 2>&1