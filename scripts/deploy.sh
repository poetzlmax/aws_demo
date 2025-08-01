#!/bin/bash

# AWS Lambda Name Extractor Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AWS Name Extractor Deployment Script${NC}"
echo "=============================================="

# Check AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure'${NC}"
    exit 1
fi

# Get AWS account and region
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_DEFAULT_REGION:-eu-west-1}

echo -e "${YELLOW}📋 Deployment Details:${NC}"
echo "Account: $AWS_ACCOUNT"
echo "Region: $AWS_REGION"
echo "Stack: simple-name-extractor"

# Check if OpenAI API key is provided
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY environment variable not set${NC}"
    echo "Please set it with: export OPENAI_API_KEY=your_key_here"
    exit 1
fi

echo -e "${GREEN}✓ OpenAI API key found${NC}"

# Step 1: Deploy/Update CloudFormation stack
echo -e "${YELLOW}📦 Step 1: Deploying CloudFormation stack...${NC}"

aws cloudformation deploy \
    --template-file infrastructure/cloudformation.yml \
    --stack-name simple-name-extractor \
    --parameter-overrides OpenAIAPIKey=$OPENAI_API_KEY \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ CloudFormation stack deployed successfully${NC}"
else
    echo -e "${RED}❌ CloudFormation deployment failed${NC}"
    exit 1
fi

# Step 2: Package and deploy Lambda function
echo -e "${YELLOW}📦 Step 2: Packaging Lambda function...${NC}"

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
cp src/lambda_function.py $TEMP_DIR/

# Create deployment package
cd $TEMP_DIR
zip -r lambda-deployment.zip .
cd - > /dev/null

echo -e "${YELLOW}🚀 Step 3: Updating Lambda function code...${NC}"

# Update Lambda function code
aws lambda update-function-code \
    --function-name SimpleNameExtractor \
    --zip-file fileb://$TEMP_DIR/lambda-deployment.zip \
    --region $AWS_REGION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Lambda function updated successfully${NC}"
else
    echo -e "${RED}❌ Lambda function update failed${NC}"
    exit 1
fi

# Clean up
rm -rf $TEMP_DIR

# Step 4: Get API endpoint
echo -e "${YELLOW}🔍 Step 4: Getting API endpoint...${NC}"

API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name simple-name-extractor \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
    --output text)

# Step 5: Test the deployment
echo -e "${YELLOW}🧪 Step 5: Testing deployment...${NC}"

TEST_RESPONSE=$(curl -s -X POST $API_ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello John Smith and Mary Johnson"}')

echo "API Response: $TEST_RESPONSE"

if echo $TEST_RESPONSE | grep -q "names"; then
    echo -e "${GREEN}✅ Deployment test successful!${NC}"
else
    echo -e "${RED}❌ Deployment test failed${NC}"
    echo "Response: $TEST_RESPONSE"
fi

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=============================================="
echo -e "${YELLOW}API Endpoint:${NC} $API_ENDPOINT"
echo -e "${YELLOW}Test Command:${NC}"
echo "curl -X POST $API_ENDPOINT \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"text\": \"Hello John Smith and Mary Johnson\"}'"
echo ""
echo -e "${YELLOW}Monitor logs:${NC}"
echo "aws logs tail /aws/lambda/SimpleNameExtractor --follow --region $AWS_REGION"
