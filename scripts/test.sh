#!/bin/bash
# Run all tests for Name Extractor API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        error "Python 3 not found. Please install Python 3."
        exit 1
    fi
}

# Install Python dependencies if needed
install_dependencies() {
    log "Checking Python dependencies..."
    
    # Check if requests is available, install if not
    if ! python3 -c "import requests" &> /dev/null; then
        log "Installing requests library..."
        pip3 install requests --user || {
            warn "Could not install requests. Using urllib instead."
            USE_URLLIB=true
        }
    fi
}

# Run API functionality tests
run_api_tests() {
    log "Running API functionality tests..."
    echo "=" * 50
    
    if [ "$USE_URLLIB" = true ]; then
        # Use simple urllib test if requests not available
        python3 -c "
import urllib.request
import json
import sys

def test_api():
    try:
        data = {'text': 'Test John Smith'}
        req = urllib.request.Request(
            'https://cplwnagvi0.execute-api.eu-west-1.amazonaws.com/v1/extract',
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print('✅ API Test passed')
            print(f'Response: {json.dumps(result, indent=2)}')
            return True
    except Exception as e:
        print(f'❌ API Test failed: {e}')
        return False

if not test_api():
    sys.exit(1)
"
    else
        python3 tests/api_test.py
    fi
}

# Run load tests
run_load_tests() {
    log "Running load tests..."
    echo "=" * 50
    python3 tests/load_test.py
}

# Quick smoke test
run_smoke_test() {
    log "Running smoke test..."
    
    ENDPOINT="https://cplwnagvi0.execute-api.eu-west-1.amazonaws.com/v1/extract"
    
    RESPONSE=$(curl -s -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d '{"text": "Quick test with John Doe"}' \
        --max-time 30)
    
    if echo "$RESPONSE" | grep -q "John Doe"; then
        success "Smoke test passed"
        echo "Response: $RESPONSE"
    else
        error "Smoke test failed"
        echo "Response: $RESPONSE"
        exit 1
    fi
}

# Main test execution
main() {
    echo "🧪 Name Extractor API Test Suite"
    echo "================================"
    
    check_python
    install_dependencies
    
    echo ""
    run_smoke_test
    echo ""
    
    if [ "$1" = "--full" ]; then
        run_api_tests
        echo ""
        run_load_tests
    else
        log "Running basic tests only. Use --full for comprehensive tests."
        run_api_tests
    fi
    
    echo ""
    success "All tests completed! 🎉"
}

# Handle errors
trap 'error "Tests failed"; exit 1' ERR

# Run main function
main "$@"
