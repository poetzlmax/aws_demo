#!/usr/bin/env python3
"""
API Functionality Tests for Name Extractor API
Tests various scenarios and validates responses
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

# API Configuration
API_ENDPOINT = "https://mch0iwssbk.execute-api.eu-west-1.amazonaws.com/v1/extract"
TIMEOUT = 30

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log(message: str, color: str = Colors.BLUE) -> None:
    """Log message with color"""
    print(f"{color}[TEST]{Colors.END} {message}")

def test_api_call(test_name: str, payload: Dict[str, Any], expected_status: int = 200) -> bool:
    """Make API call and validate response"""
    log(f"Running: {test_name}")
    
    try:
        start_time = time.time()
        response = requests.post(
            API_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=TIMEOUT
        )
        duration = time.time() - start_time
        
        # Check status code
        if response.status_code != expected_status:
            log(f"❌ FAIL: Expected {expected_status}, got {response.status_code}", Colors.RED)
            log(f"Response: {response.text}", Colors.RED)
            return False
        
        # Parse JSON response
        try:
            result = response.json()
        except json.JSONDecodeError:
            log(f"❌ FAIL: Invalid JSON response", Colors.RED)
            return False
        
        log(f"✅ PASS: {test_name} ({duration:.2f}s)", Colors.GREEN)
        log(f"Response: {json.dumps(result, indent=2)}", Colors.YELLOW)
        return True
        
    except requests.exceptions.Timeout:
        log(f"❌ FAIL: Request timeout ({TIMEOUT}s)", Colors.RED)
        return False
    except requests.exceptions.RequestException as e:
        log(f"❌ FAIL: Request error: {e}", Colors.RED)
        return False

def main():
    """Run all API tests"""
    log("Starting Name Extractor API Tests", Colors.BLUE)
    log(f"Endpoint: {API_ENDPOINT}", Colors.BLUE)
    
    tests_passed = 0
    total_tests = 0
    
    # Test cases
    test_cases = [
        {
            "name": "Basic name extraction",
            "payload": {"text": "Hello John Smith and Mary Johnson"},
            "expected_status": 200
        },
        {
            "name": "German names",
            "payload": {"text": "Hallo Max Mustermann, ich bin Anna Schmidt"},
            "expected_status": 200
        },
        {
            "name": "Multiple names with titles",
            "payload": {"text": "Dr. Peter Weber arbeitet mit Prof. Sarah Miller zusammen"},
            "expected_status": 200
        },
        {
            "name": "No names in text",
            "payload": {"text": "This is just a regular sentence without any names"},
            "expected_status": 200
        },
        {
            "name": "Empty text",
            "payload": {"text": ""},
            "expected_status": 400
        },
        {
            "name": "Missing text field",
            "payload": {},
            "expected_status": 400
        },
        {
            "name": "Long text with names",
            "payload": {"text": "In this long paragraph we have John Smith working at the company. Sarah Johnson is the manager and Mike Brown is the developer. They all work together on the project with Lisa Wilson and David Anderson from the other team."},
            "expected_status": 200
        }
    ]
    
    # Run tests
    for test_case in test_cases:
        total_tests += 1
        if test_api_call(
            test_case["name"], 
            test_case["payload"], 
            test_case["expected_status"]
        ):
            tests_passed += 1
        print("-" * 60)
    
    # Summary
    log(f"Tests completed: {tests_passed}/{total_tests} passed", Colors.BLUE)
    
    if tests_passed == total_tests:
        log("🎉 All tests passed!", Colors.GREEN)
        sys.exit(0)
    else:
        log(f"❌ {total_tests - tests_passed} tests failed", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
