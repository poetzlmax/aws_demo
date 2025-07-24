#!/usr/bin/env python3
"""
Generate secure pre-signed URLs for bucket access
"""
import boto3
import argparse
from datetime import datetime, timedelta

def generate_upload_url(bucket_name, object_key, expiry_hours=1):
    """Generate a pre-signed URL for uploading to S3"""
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiry_hours * 3600  # Convert hours to seconds
        )
        return response
    except Exception as e:
        print(f"Error generating upload URL: {e}")
        return None

def generate_download_url(bucket_name, object_key, expiry_hours=1):
    """Generate a pre-signed URL for downloading from S3"""
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiry_hours * 3600
        )
        return response
    except Exception as e:
        print(f"Error generating download URL: {e}")
        return None

def list_bucket_contents(bucket_name):
    """List contents of a bucket"""
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        else:
            return []
    except Exception as e:
        print(f"Error listing bucket contents: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Generate secure S3 access URLs')
    parser.add_argument('--action', choices=['upload', 'download', 'list'], required=True,
                      help='Action to perform')
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    parser.add_argument('--file', help='File name/key (required for upload/download)')
    parser.add_argument('--hours', type=int, default=1, help='Expiry time in hours (default: 1)')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        print(f"\n📁 Contents of bucket '{args.bucket}':")
        files = list_bucket_contents(args.bucket)
        if files:
            for file in files:
                print(f"  - {file}")
        else:
            print("  (bucket is empty)")
    
    elif args.action == 'upload':
        if not args.file:
            print("Error: --file is required for upload")
            return
        
        url = generate_upload_url(args.bucket, args.file, args.hours)
        if url:
            expiry = datetime.now() + timedelta(hours=args.hours)
            print(f"\n🔗 Upload URL for '{args.file}':")
            print(f"URL: {url}")
            print(f"⏰ Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n📤 Usage:")
            print(f"curl -X PUT '{url}' --upload-file /path/to/your/{args.file}")
    
    elif args.action == 'download':
        if not args.file:
            print("Error: --file is required for download")
            return
        
        url = generate_download_url(args.bucket, args.file, args.hours)
        if url:
            expiry = datetime.now() + timedelta(hours=args.hours)
            print(f"\n🔗 Download URL for '{args.file}':")
            print(f"URL: {url}")
            print(f"⏰ Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n📥 Usage:")
            print(f"curl '{url}' -o {args.file}")

if __name__ == "__main__":
    main()
