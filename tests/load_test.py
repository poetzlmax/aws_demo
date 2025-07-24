#!/usr/bin/env python3
"""
Load Test for Name Extractor API
Tests performance under concurrent load
"""

import concurrent.futures
import time
import json
import urllib.request
import urllib.parse
from typing import List, Dict

# API Configuration
API_ENDPOINT = "https://cplwnagvi0.execute-api.eu-west-1.amazonaws.com/v1/extract"
CONCURRENT_REQUESTS = 5
TOTAL_REQUESTS = 20

def make_request(text: str) -> Dict:
    """Make a single API request"""
    data = {"text": text}
    req = urllib.request.Request(
        API_ENDPOINT,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            duration = time.time() - start_time
            result = json.loads(response.read().decode('utf-8'))
            return {
                'success': True,
                'duration': duration,
                'status_code': response.status,
                'response': result
            }
    except Exception as e:
        duration = time.time() - start_time
        return {
            'success': False,
            'duration': duration,
            'error': str(e)
        }

def run_load_test():
    """Run concurrent load test"""
    print("🚀 Starting Load Test")
    print(f"Endpoint: {API_ENDPOINT}")
    print(f"Concurrent requests: {CONCURRENT_REQUESTS}")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print("-" * 50)
    
    test_texts = [
        "John Smith and Mary Johnson work together",
        "Dr. Peter Weber and Prof. Sarah Miller",
        "Anna Schmidt ist eine Entwicklerin",
        "Mike Brown, Lisa Wilson, and David Anderson",
        "No names in this text at all"
    ]
    
    # Prepare requests
    requests_data = []
    for i in range(TOTAL_REQUESTS):
        text = test_texts[i % len(test_texts)]
        requests_data.append(text)
    
    # Execute concurrent requests
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        future_to_text = {
            executor.submit(make_request, text): text 
            for text in requests_data
        }
        
        for future in concurrent.futures.as_completed(future_to_text):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✅ Request completed in {result['duration']:.2f}s")
            else:
                print(f"❌ Request failed: {result['error']}")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]
    
    if successful_requests:
        durations = [r['duration'] for r in successful_requests]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
    else:
        avg_duration = min_duration = max_duration = 0
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 LOAD TEST RESULTS")
    print("=" * 50)
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Successful requests: {len(successful_requests)}")
    print(f"Failed requests: {len(failed_requests)}")
    print(f"Success rate: {len(successful_requests)/TOTAL_REQUESTS*100:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Requests per second: {TOTAL_REQUESTS/total_time:.2f}")
    print(f"Average response time: {avg_duration:.2f}s")
    print(f"Min response time: {min_duration:.2f}s")
    print(f"Max response time: {max_duration:.2f}s")
    
    if failed_requests:
        print(f"\n❌ Failed request errors:")
        for req in failed_requests[:5]:  # Show first 5 errors
            print(f"  - {req['error']}")

if __name__ == "__main__":
    run_load_test()
