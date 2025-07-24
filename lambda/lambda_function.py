import boto3
import openai
import os
import json
import base64

secrets_client = boto3.client('secretsmanager')
s3 = boto3.client('s3')

def get_openai_key(secret_name):
    secret_response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = secret_response['SecretString']
    return secret

openai.api_key = get_openai_key(os.environ['OPENAI_SECRET_NAME'])

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    response = s3.get_object(Bucket=bucket, Key=key)
    image_data = response['Body'].read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    openai_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extrahiere alle relevanten Informationen aus diesem Bild."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }
        ],
        max_tokens=500
    )

    extracted_info = openai_response.choices[0].message.content

    output_bucket = os.environ['OUTPUT_BUCKET']
    output_key = key.rsplit('.', 1)[0] + '.json'

    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=json.dumps({"extracted_info": extracted_info}),
        ContentType='application/json'
    )

    return {'statusCode': 200}
