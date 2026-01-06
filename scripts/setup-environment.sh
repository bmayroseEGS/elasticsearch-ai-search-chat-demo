#!/bin/bash

# Setup script for AI-Powered Search and Chat Demo
# This script initializes the Elasticsearch index and loads sample data

set -e  # Exit on error

echo "========================================"
echo "AI Search & Chat Demo - Setup"
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
    echo "Usage: cd /path/to/elasticsearch-ai-search-chat-demo && ./scripts/setup-environment.sh"
    exit 1
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo -e "${RED}ERROR: config.py not found${NC}"
    echo ""
    echo "Please create config.py from config.example.py:"
    echo "  cp config.example.py config.py"
    echo ""
    echo "Then edit config.py with your credentials:"
    echo "  - Elasticsearch URL and credentials"
    echo "  - OpenAI API key"
    echo ""
    exit 1
fi

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}WARNING: No virtual environment detected${NC}"
    echo "It's recommended to use a virtual environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install/verify dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt --quiet

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 1: Create index
echo ""
echo "========================================"
echo "Step 1: Creating Elasticsearch Index"
echo "========================================"
echo ""

python3 part1_smart_search/01_setup_index.py

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to create index${NC}"
    echo "Please check:"
    echo "  - Elasticsearch is running"
    echo "  - Credentials in config.py are correct"
    echo "  - Network connectivity"
    exit 1
fi

# Step 2: Generate embeddings and index data
echo ""
echo "========================================"
echo "Step 2: Generating Embeddings & Indexing Data"
echo "========================================"
echo ""
echo -e "${YELLOW}NOTE: This will call OpenAI API and incur costs${NC}"
echo "Estimated cost: < $0.10 for the sample dataset"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled. Index created but no data indexed."
    exit 0
fi

python3 part1_smart_search/02_generate_embeddings.py

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to generate embeddings and index data${NC}"
    echo "Please check:"
    echo "  - OpenAI API key in config.py is correct"
    echo "  - You have sufficient API credits"
    echo "  - Network connectivity to OpenAI"
    exit 1
fi

# Success!
echo ""
echo "========================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Your environment is ready for the workshop."
echo ""
echo -e "${GREEN}Part 1: Smart Search${NC}"
echo "Try these commands:"
echo "  python3 part1_smart_search/03_keyword_search.py \"gaming laptop\""
echo "  python3 part1_smart_search/04_semantic_search.py \"portable computer for coding\""
echo "  python3 part1_smart_search/05_hybrid_search.py \"affordable monitor for designers\""
echo ""
echo -e "${GREEN}Part 2: Conversational AI${NC}"
echo "Try these commands:"
echo "  python3 part2_conversational_ai/01_basic_rag.py"
echo "  python3 part2_conversational_ai/02_context_chat.py"
echo "  python3 part2_conversational_ai/03_controlled_responses.py"
echo ""
echo "Enjoy the workshop! 🚀"
echo ""
