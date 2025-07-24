#!/bin/bash
set -e

STACK_NAME="openai-image-extraction-stack"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
TIMESTAMP=$(date +%s)
DEPLOYMENT_BUCKET="openai-deployment-${ACCOUNT_ID}-${REGION}-${TIMESTAMP}"

# Create deployment bucket if it doesn't exist
aws s3 mb s3://$DEPLOYMENT_BUCKET 2>/dev/null || echo "Bucket already exists"

# prepare lambda packages
cd lambda
/home/azureuser/.local/bin/pip install -r requirements.txt -t ./package
zip -r ../lambda-code.zip lambda_function.py package > /dev/null
zip -r ../api-code.zip api_handler.py package > /dev/null
cd ..

# Upload lambda packages to deployment bucket
aws s3 cp lambda-code.zip s3://$DEPLOYMENT_BUCKET/lambda-code.zip
aws s3 cp api-code.zip s3://$DEPLOYMENT_BUCKET/api-code.zip

# deploy stack
aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --template-file cloudformation-template.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides OpenAIAPIKey=${OPENAI_KEY} DeploymentBucketName=${DEPLOYMENT_BUCKET}

INPUT_BUCKET="openai-image-input-${ACCOUNT_ID}-${REGION}"

echo "Deployment abgeschlossen."
echo ""
echo "🔒 SECURITY NOTICE: All S3 buckets are now PRIVATE and cost-protected:"
echo "   - Input bucket: Auto-deletes files after 1 day"
echo "   - Output bucket: Auto-deletes results after 7 days"
echo "   - Web bucket: Auto-deletes files after 7 days"
echo ""
echo "✅ No public access = No risk of unexpected charges from malicious uploads"
echo "✅ Use the API endpoints to interact with the service securely"
