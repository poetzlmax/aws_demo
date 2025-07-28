# AWS & OpenAI Name Extractor API

A serverless AWS API that extracts person names from text using OpenAI GPT-4.

## 🚀 **DEPLOYED & LIVE** ✅

**API Endpoint:** `https://ewt4ntj2r6.execute-api.eu-west-1.amazonaws.com/v1/extract`  
**Status:** Production Ready  
**Stack:** simple-name-extractor (eu-west-1)  
**Deployed:** July 28, 2025

## Architecture

- **AWS Lambda**: Python 3.12 runtime for text processing
- **API Gateway**: RESTful API endpoint with CORS support  
- **OpenAI GPT-4**: Intelligent name extraction from natural language
- **CloudFormation**: Infrastructure as Code for reproducible deployments

## API Endpoint

```
POST https://ewt4ntj2r6.execute-api.eu-west-1.amazonaws.com/v1/extract
```

### Request Format
```json
{
  "text": "Your text containing names here"
}
```

### Response Format
```json
{
  "names": ["John Doe", "Jane Smith"],
  "original_text": "Your text containing names here",
  "count": 2
}
```

## Quick Test

```bash
curl -X POST https://ewt4ntj2r6.execute-api.eu-west-1.amazonaws.com/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello John Smith and Mary Johnson"}'
```

**Expected Response:**
```json
{"names": ["John Smith", "Mary Johnson"], "original_text": "Hello John Smith and Mary Johnson", "count": 2}
```

## Project Structure

```
├── src/                    # Lambda function source code
│   └── lambda_function.py  # Main handler
├── infrastructure/         # AWS infrastructure
│   └── cloudformation.yml  # CloudFormation template
├── tests/                  # Test scripts
│   ├── api_test.py        # API functionality tests
│   └── load_test.py       # Performance tests
├── scripts/               # Deployment scripts
│   ├── deploy.sh          # Deploy infrastructure and code
│   └── test.sh           # Run all tests
└── README.md              # This file
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- OpenAI API key
- Python 3.x for local testing

## Deployment

1. **Deploy Infrastructure:**
   ```bash
   ./scripts/deploy.sh
   ```

2. **Run Tests:**
   ```bash
   ./scripts/test.sh
   ```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (configured via CloudFormation parameter)

## Error Handling

The API handles various error scenarios:
- Missing text input (400)
- OpenAI API errors (500)
- Network timeouts (500)
- Invalid JSON format (400)

## Performance

- Cold start: ~2-3 seconds
- Warm requests: ~1-2 seconds
- Timeout: 60 seconds
- Memory: 128 MB

## Cost Estimation

- Lambda: ~$0.000001 per request
- API Gateway: ~$0.0000035 per request  
- OpenAI API: ~$0.0015 per request (GPT-4)

**Total: ~$0.0015 per request**

## Deployment Status ✅

**Current Deployment:**
- **Stack Name:** simple-name-extractor
- **Region:** eu-west-1 (Ireland)  
- **Status:** CREATE_COMPLETE
- **Lambda Function:** SimpleNameExtractor
- **Deployed:** July 28, 2025 07:34 UTC

**Resources Created:**
- AWS Lambda Function (Python 3.12)
- API Gateway REST API
- IAM Execution Role
- CloudFormation Stack

## Monitoring

View logs in CloudWatch:
```bash
aws logs tail /aws/lambda/SimpleNameExtractor --follow --region eu-west-1
```

## Security

- API is publicly accessible (no authentication required)
- CORS enabled for web integration
- OpenAI API key stored as environment variable

## Support

For issues or questions, check the CloudWatch logs or test with the provided test scripts.