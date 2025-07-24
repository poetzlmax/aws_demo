#!/bin/bash
set -e

STACK_NAME="openai-image-extraction-stack"

# prepare lambda packages
cd lambda
pip install -r requirements.txt -t ./package
zip -r ../lambda-code.zip lambda_function.py package > /dev/null
zip -r ../api-code.zip api_handler.py package > /dev/null
cd ..

# deploy stack
aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --template-file cloudformation-template.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides OpenAIAPIKey=${OPENAI_KEY}

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
INPUT_BUCKET="openai-image-input-${ACCOUNT_ID}-${REGION}"
WEB_BUCKET=$(aws cloudformation describe-stack-resources --stack-name $STACK_NAME --logical-resource-id WebBucket --query 'StackResources[0].PhysicalResourceId' --output text)

aws s3 cp lambda-code.zip s3://$INPUT_BUCKET/lambda-code.zip
aws s3 cp api-code.zip s3://$INPUT_BUCKET/api-code.zip
aws s3 cp web/index.html s3://$WEB_BUCKET/index.html --content-type text/html

echo "Deployment abgeschlossen."
