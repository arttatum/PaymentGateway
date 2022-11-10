SHELL := /bin/bash
activate_venv=.venv/bin/activate

.venv:
	cd ..; if command -v pyenv; then pyenv install --skip-existing; fi
	cd ..; python3 -m venv .venv
	cd ..; . $(activate_venv); pip3 install -r requirements-dev.txt
	cd ..; . $(activate_venv); pip3 install -r requirements-lambda.txt
	
.PHONY: deployable_zip
deployable_zip:
	cd .. && source make_lambda_zip.sh

.PHONY: configure_aws
configure_aws: .venv
	cd ..; . $(activate_venv); aws configure --profile local

.PHONY: localstack
localstack: configure_aws
	docker-compose -f docker-compose-localstack.yml down
	make deployable_zip
	docker-compose -f docker-compose-localstack.yml up -d
	terraform init
	terraform apply --auto-approve

.PHONY: valid_payment_request
valid_payment_request: 
	@printf "\e[31;1m%s\n" "Ctrl+C to quit..."
	@printf "\e[33;1m%s\n" "Calling SubmitPaymentRequest lambda..."

	@cd ..; . $(activate_venv); \
	aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://infrastructure/lambda_events/SubmitPaymentRequest_valid.json \
	--region eu-west-2 \
	infrastructure/responses/SubmitPaymentRequest.response.log  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d > /dev/null 2>&1

	@printf "\e[32;1m%s\n\n" "SubmitPaymentRequest ran to completion! A command was published to an SQS queue."
	@sleep 3
	@printf "\e[31;0m %s\n" "The ForwardPaymentRequestToAcquiringBank Lambda processes these commands as they come into SQS..." 
	@sleep 3
	@printf "\e[31;0m %s\n" "It is running in background now, on the localstack docker container.."
	@sleep 3
	@printf "\e[31;0m %s\n" "In a few moments we can view the logs from the container..."
	@sleep 3
	@printf "\e[34;1m%s\n" ""
	@docker logs localstack_payment_gateway --since 120s | sed -n '/\"message\"/p'
	@sleep 0.5
	@printf "\e[32;1m\n%s\n\n" "A new PaymentRequest was added to the system!"
	@printf "\e[31;0m%s\n\n" "The SubmitPaymentRequest Lambda returned it's ID to the caller:"
	@cat responses/SubmitPaymentRequest.response.log
	@printf "\e[32;3m\n\n%s\n\n" "Next, try running: 'make get_payment_request_status PAYMENT_REQUEST_ID=<the_id_above>'"
	

.PHONY: get_number_of_dead_letters
get_number_of_dead_letters:
	printf "\nNumber of Dead Letters..."
	@aws --endpoint-url=http://localhost:4566 \
	sqs get-queue-attributes --queue-url https://sqs.eu-west-2.amazonaws.com/000000000000/forward-payment-request-to-acquiring-bank-dlq \
	--attribute-names ApproximateNumberOfMessages


.PHONY: invalid_payment_request
invalid_payment_request: 
	cd ..; . $(activate_venv); \
	aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://infrastructure/lambda_events/SubmitPaymentRequest_invalid.json \
	--region eu-west-2 \
	infrastructure/responses/SubmitPaymentRequest_invalid.response.log  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d
	@printf "\n\n☠☠☠ The Payment Request was invalid ☠☠☠\n\n"
	cat responses/SubmitPaymentRequest_invalid.response.log

MERCHANT_ID ?= 0b20e14d-0122-4b60-824a-fcc4c2a3b52a

.PHONY: get_payment_request_status
get_payment_request_status:
	@cd ..; . $(activate_venv); \
	aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name GetPaymentStatus \
	--profile local \
	--payload "{\"pathParameters\": {\"merchant_id\": \"$(MERCHANT_ID)\", \"payment_request_id\": \"$(PAYMENT_REQUEST_ID)\"}}" \
	--region eu-west-2 \
	infrastructure/responses/GetPaymentStatus.response.log  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d
	@printf "\e[32;1m\n\n%s\n" "Retrieved status of Payment request!"
	@printf "\e[31;0m\n%s\n\n" "Response:"
	@cat responses/GetPaymentStatus.response.log | python -m json.tool
	@printf "\e[32;3m\n\n%s\n\n" "Next, try running: 'make provide_payment_request_update PAYMENT_REQUEST_ID=<the_id_above>'"


.PHONY: dump_dynamo
dump_dynamo:
	cd ..; . $(activate_venv); \
	aws --endpoint-url=http://localhost:4566 dynamodb scan \
	--profile local \
	--table-name="payment_requests"

query_dynamo:
	cd ..; . $(activate_venv); \
	aws --endpoint-url=http://localhost:4566 dynamodb query \
	--profile local \
	--table-name "payment_requests" \
	--key-condition-expression "id = :id" \
	--expression-attribute-values "{\":id\": {\"S\": \"$(ID)\"}}"
