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
	cd ..; . $(activate_venv); \
	aws --endpoint-url=http://localhost:4566 \
	lambda invoke --function-name SubmitPaymentRequest \
	--profile local \
	--payload file://infrastructure/lambda_events/SubmitPaymentRequest_valid.json \
	--region eu-west-2 \
	infrastructure/responses/SubmitPaymentRequest.response.log  \
	--log-type Tail --query 'LogResult' --output text |  base64 -d > /dev/null 2>&1
	
	make follow_localstack_logs
	
.PHONY: follow_localstack_logs
follow_localstack_logs:
	docker logs --follow localstack_payment_gateway --since 20s | grep \"message\"

.PHONY: get_number_of_dead_letters
get_number_of_dead_letters:
	echo "Number of Dead Letters..."
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
	@echo "☠☠☠ The Payment Request was invalid ☠☠☠"
	cat responses/SubmitPaymentRequest_invalid.response.log

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
