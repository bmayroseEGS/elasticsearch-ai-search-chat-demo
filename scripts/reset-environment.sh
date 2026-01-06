#!/bin/bash

# Reset script for AI-Powered Search and Chat Demo
# This script deletes the index and allows you to start fresh

set -e  # Exit on error

echo "========================================"
echo "AI Search & Chat Demo - Reset"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}ERROR: Must run from project root directory${NC}"
    echo "Usage: cd /path/to/elasticsearch-ai-search-chat-demo && ./scripts/reset-environment.sh"
    exit 1
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo -e "${RED}ERROR: config.py not found${NC}"
    echo "Cannot connect to Elasticsearch without configuration."
    exit 1
fi

echo -e "${YELLOW}WARNING: This will delete the following:${NC}"
echo "  - Index: products-semantic-search"
echo "  - All indexed documents and embeddings"
echo ""
echo "You will need to run setup-environment.sh again to recreate the environment."
echo ""
read -p "Are you sure you want to reset? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Reset cancelled."
    exit 0
fi

# Python script to delete index
cat > /tmp/reset_index.py << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

from elasticsearch import Elasticsearch
import config

def reset_index():
    """Delete the index if it exists."""

    # Connect to Elasticsearch
    print(f"Connecting to Elasticsearch at {config.ELASTICSEARCH_URL}...")

    if hasattr(config, 'ELASTICSEARCH_API_KEY'):
        es = Elasticsearch(
            config.ELASTICSEARCH_URL,
            api_key=config.ELASTICSEARCH_API_KEY,
            verify_certs=config.ELASTICSEARCH_VERIFY_CERTS
        )
    else:
        es = Elasticsearch(
            config.ELASTICSEARCH_URL,
            basic_auth=(config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD),
            verify_certs=config.ELASTICSEARCH_VERIFY_CERTS
        )

    if not es.ping():
        print("ERROR: Could not connect to Elasticsearch")
        sys.exit(1)

    print("✓ Connected to Elasticsearch\n")

    # Check if index exists
    if es.indices.exists(index=config.INDEX_NAME):
        print(f"Deleting index '{config.INDEX_NAME}'...")
        es.indices.delete(index=config.INDEX_NAME)
        print(f"✓ Index '{config.INDEX_NAME}' deleted")
    else:
        print(f"Index '{config.INDEX_NAME}' does not exist (already clean)")

    es.close()

if __name__ == "__main__":
    try:
        reset_index()
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
EOF

# Run the reset script
python3 /tmp/reset_index.py

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to reset environment${NC}"
    rm /tmp/reset_index.py
    exit 1
fi

# Cleanup
rm /tmp/reset_index.py

# Success!
echo ""
echo "========================================"
echo -e "${GREEN}✓ Environment Reset Complete${NC}"
echo "========================================"
echo ""
echo "The index has been deleted."
echo ""
echo -e "${YELLOW}To recreate the environment, run:${NC}"
echo "  ./scripts/setup-environment.sh"
echo ""
