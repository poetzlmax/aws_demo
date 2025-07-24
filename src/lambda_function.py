import json
import os
import urllib.request
import urllib.parse

def lambda_handler(event, context):
    """
    Simple API to extract names from text using OpenAI
    """
    try:
        print(f"Event: {event}")
        
        # Parse request body
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Get text to analyze
        text = body.get('text', '').strip()
        if not text:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'No text provided',
                    'usage': 'POST {"text": "Your text here"}'
                })
            }
        
        # Get OpenAI API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'OpenAI API key not configured'})
            }
        
        # Prepare OpenAI request
        openai_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "Extract all person names from the given text. Return only a JSON array of names, nothing else. If no names found, return empty array []."
                },
                {
                    "role": "user", 
                    "content": text
                }
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        # Call OpenAI API
        print(f"Making OpenAI API call...")
        req = urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            data=json.dumps(openai_data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                print(f"OpenAI API response status: {response.status}")
                if response.status == 200:
                    openai_response = json.loads(response.read().decode('utf-8'))
                    extracted_content = openai_response['choices'][0]['message']['content'].strip()
                    
                    try:
                        # Try to parse as JSON
                        names = json.loads(extracted_content)
                    except:
                        # Fallback: treat as plain text and split
                        names = [name.strip() for name in extracted_content.split(',') if name.strip()]
                    
                    print(f"Extracted names: {names}")
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Access-Control-Allow-Origin': '*',
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps({
                            'names': names,
                            'original_text': text[:200] + '...' if len(text) > 200 else text,
                            'count': len(names)
                        })
                    }
                else:
                    error_data = response.read().decode('utf-8')
                    print(f"OpenAI API error: {response.status}, {error_data}")
                    return {
                        'statusCode': 500,
                        'headers': {
                            'Access-Control-Allow-Origin': '*',
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps({
                            'error': f'OpenAI API error: {response.status}',
                            'details': error_data
                        })
                    }
        except urllib.error.URLError as e:
            print(f"URL Error: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': f'Network error: {str(e)}'
                })
            }
        except Exception as e:
            print(f"OpenAI request error: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': f'OpenAI request failed: {str(e)}'
                })
            }
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }
