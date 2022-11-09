#!/bin/bash

# Creates deployable zip that contains PaymentGateway lambda code and it's dependencies

# Notes: 
#
#   Lambda runs on Amazon Linux 2 operating system. To ensure dependencies 
#   can run on that platform, the manylinux2014_x86_64 platform tag is specified.
#
#   The lambda runtime provided by AWS includes several packages, so they do not need 
#   to be included in the deployed bundle, but they are required to run the code locally.

#   For simplicity, I have not added a flag to determine where the zip will be deployed, 
#   dev dependencies are still included in the build. It would be a simple extension to 
#   include this logic.

[[ -f ./requirements-lambda.txt ]] && pip install \
    --requirement ./requirements-lambda.txt \
    --platform manylinux2014_x86_64 \
    --target=./dependencies \
    --implementation cp \
    --python 3.9 \
    --only-binary=:all: \

[[ -f ./requirements-dev.txt ]] && pip install \
--requirement ./requirements-dev.txt \
--platform manylinux2014_x86_64 \
--target=./dependencies \
--implementation cp \
--python 3.9 \
--only-binary=:all: \

ZIP_NAME="payment_gateway_lambdas.zip"

# Add installed dependencies to deployment zip
(cd dependencies && zip "../$ZIP_NAME" -r * -x '*__pycache__/*')

# Add source code to deployment zip
(cd src && zip "../$ZIP_NAME" -r . -x '*__pycache__/*')
