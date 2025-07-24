import boto3
import os
import json
import base64
import uuid

s3 = boto3.client('s3')
INPUT_BUCKET = os.environ['INPUT_BUCKET']
OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']

def lambda_handler(event, context):
    route = event.get('rawPath', '')
    method = event.get('requestContext', {}).get('http', {}).get('method', '')

    if method == 'POST' and route == '/upload':
        body = json.loads(event.get('body', '{}'))
        filename = body.get('filename', 'upload')
        file_data = base64.b64decode(body.get('file', ''))
        key = f"{uuid.uuid4()}-{filename}"
        s3.put_object(Bucket=INPUT_BUCKET, Key=key, Body=file_data)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'key': key})
        }
    elif method == 'GET' and route.startswith('/result/'):
        key = route[len('/result/'):]
        try:
            response = s3.get_object(Bucket=OUTPUT_BUCKET, Key=f"{key}.json")
            content = response['Body'].read().decode('utf-8')
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': content
            }
        except s3.exceptions.NoSuchKey:
            return {'statusCode': 404, 'body': 'Not ready'}

    return {'statusCode': 404, 'body': 'Not found'}
