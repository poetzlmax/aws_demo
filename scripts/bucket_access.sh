#!/bin/bash
# Secure S3 Access Helper
# Generates temporary access URLs for your private S3 buckets

set -e

# Your bucket names
INPUT_BUCKET="openai-image-input-269552072239-eu-west-1"
OUTPUT_BUCKET="openai-image-output-269552072239-eu-west-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "🔐 Secure S3 Access Helper"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  upload-url <filename> [hours]    Generate upload URL for input bucket"
    echo "  download-url <filename> [hours]  Generate download URL from output bucket"
    echo "  list-input                       List files in input bucket"
    echo "  list-output                      List files in output bucket"
    echo "  cleanup                          Delete all files (emergency cleanup)"
    echo ""
    echo "Examples:"
    echo "  $0 upload-url image.jpg 2        # 2-hour upload URL"
    echo "  $0 download-url result.json      # 1-hour download URL"
    echo "  $0 list-input                    # Show input bucket contents"
    echo ""
    exit 1
}

generate_upload_url() {
    local filename="$1"
    local hours="${2:-1}"
    local expires=$((hours * 3600))
    
    echo -e "${BLUE}🔗 Generating secure upload URL...${NC}"
    echo ""
    
    local url=$(aws s3 presign "s3://$INPUT_BUCKET/$filename" --expires-in $expires --profile default 2>/dev/null || echo "ERROR")
    
    if [[ "$url" == "ERROR" ]]; then
        echo -e "${RED}❌ Error: Could not generate URL. Check AWS credentials.${NC}"
        exit 1
    fi
    
    local expiry=$(date -d "+$hours hours" '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${GREEN}✅ Upload URL generated successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📁 File:${NC} $filename"
    echo -e "${YELLOW}📦 Bucket:${NC} $INPUT_BUCKET (Input)"
    echo -e "${YELLOW}⏰ Expires:${NC} $expiry"
    echo ""
    echo -e "${YELLOW}🔗 URL:${NC}"
    echo "$url"
    echo ""
    echo -e "${BLUE}📤 Usage:${NC}"
    echo "curl -X PUT '$url' --upload-file /path/to/$filename"
    echo ""
    echo -e "${BLUE}Or with a web form:${NC}"
    echo "curl -X PUT '$url' -H 'Content-Type: image/jpeg' --data-binary @$filename"
}

generate_download_url() {
    local filename="$1"
    local hours="${2:-1}"
    local expires=$((hours * 3600))
    
    echo -e "${BLUE}🔗 Generating secure download URL...${NC}"
    echo ""
    
    # Check if file exists first
    aws s3 ls "s3://$OUTPUT_BUCKET/$filename" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error: File '$filename' not found in output bucket${NC}"
        exit 1
    fi
    
    local url=$(aws s3 presign "s3://$OUTPUT_BUCKET/$filename" --expires-in $expires --profile default 2>/dev/null || echo "ERROR")
    
    if [[ "$url" == "ERROR" ]]; then
        echo -e "${RED}❌ Error: Could not generate URL. Check AWS credentials.${NC}"
        exit 1
    fi
    
    local expiry=$(date -d "+$hours hours" '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${GREEN}✅ Download URL generated successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📁 File:${NC} $filename"
    echo -e "${YELLOW}📦 Bucket:${NC} $OUTPUT_BUCKET (Output)"
    echo -e "${YELLOW}⏰ Expires:${NC} $expiry"
    echo ""
    echo -e "${YELLOW}🔗 URL:${NC}"
    echo "$url"
    echo ""
    echo -e "${BLUE}📥 Usage:${NC}"
    echo "curl '$url' -o $filename"
    echo ""
    echo -e "${BLUE}Or open in browser:${NC}"
    echo "Simply click the URL above"
}

list_bucket() {
    local bucket="$1"
    local bucket_type="$2"
    
    echo -e "${BLUE}📋 Listing $bucket_type bucket contents...${NC}"
    echo ""
    
    local files=$(aws s3 ls "s3://$bucket" --recursive | awk '{print $4}')
    
    if [ -z "$files" ]; then
        echo -e "${YELLOW}📂 Bucket is empty${NC}"
    else
        echo -e "${GREEN}📁 Files found:${NC}"
        echo "$files" | while read -r file; do
            if [ -n "$file" ]; then
                local size=$(aws s3 ls "s3://$bucket/$file" | awk '{print $3}')
                local date=$(aws s3 ls "s3://$bucket/$file" | awk '{print $1, $2}')
                echo -e "  ${YELLOW}•${NC} $file ${BLUE}($size bytes, $date)${NC}"
            fi
        done
    fi
    echo ""
}

cleanup_buckets() {
    echo -e "${RED}⚠️  WARNING: This will delete ALL files in both buckets!${NC}"
    echo -e "${YELLOW}📦 Input bucket:${NC} $INPUT_BUCKET"
    echo -e "${YELLOW}📦 Output bucket:${NC} $OUTPUT_BUCKET"
    echo ""
    read -p "Are you sure? Type 'DELETE' to confirm: " confirm
    
    if [ "$confirm" = "DELETE" ]; then
        echo -e "${BLUE}🧹 Cleaning up buckets...${NC}"
        aws s3 rm "s3://$INPUT_BUCKET" --recursive
        aws s3 rm "s3://$OUTPUT_BUCKET" --recursive
        echo -e "${GREEN}✅ Cleanup completed${NC}"
    else
        echo -e "${YELLOW}❌ Cleanup cancelled${NC}"
    fi
}

# Main command handling
case "$1" in
    "upload-url")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Filename required${NC}"
            usage
        fi
        generate_upload_url "$2" "$3"
        ;;
    "download-url")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Filename required${NC}"
            usage
        fi
        generate_download_url "$2" "$3"
        ;;
    "list-input")
        list_bucket "$INPUT_BUCKET" "input"
        ;;
    "list-output")
        list_bucket "$OUTPUT_BUCKET" "output"
        ;;
    "cleanup")
        cleanup_buckets
        ;;
    *)
        usage
        ;;
esac
