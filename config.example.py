"""
Configuration file for AI-Powered Search and Chat workshop.

Copy this file to config.py and fill in your actual credentials.
NEVER commit config.py to version control!
"""

# ============================================================================
# Elasticsearch Configuration
# ============================================================================

# Elasticsearch connection URL
# For local helm deployment: http://localhost:9200
# For Elastic Cloud: https://your-deployment.es.region.cloud.es.io:9243
ELASTICSEARCH_URL = "http://localhost:9200"

# Authentication method 1: Username and password
ELASTICSEARCH_USERNAME = "elastic"
ELASTICSEARCH_PASSWORD = "elastic"

# Authentication method 2: API key (comment out username/password if using this)
# ELASTICSEARCH_API_KEY = "your-api-key-here"

# Verify SSL certificates (set to False for local development with self-signed certs)
ELASTICSEARCH_VERIFY_CERTS = False

# ============================================================================
# OpenAI Configuration
# ============================================================================

# OpenAI API key - get from https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-your-api-key-here"

# Embedding model
# Options:
# - "text-embedding-3-small" (1536 dims, $0.02/1M tokens) - Recommended for workshop
# - "text-embedding-3-large" (3072 dims, $0.13/1M tokens) - Better quality
# - "text-embedding-ada-002" (1536 dims, $0.10/1M tokens) - Legacy
EMBEDDING_MODEL = "text-embedding-3-small"

# LLM model for chat
# Options:
# - "gpt-4-turbo-preview" - Most capable, $10/1M input tokens
# - "gpt-4" - Previous version, $30/1M input tokens
# - "gpt-3.5-turbo" - Faster and cheaper, $0.50/1M input tokens
LLM_MODEL = "gpt-3.5-turbo"

# Maximum tokens for LLM responses
MAX_TOKENS = 500

# Temperature for LLM (0.0 = deterministic, 1.0 = creative)
TEMPERATURE = 0.7

# ============================================================================
# Index Configuration
# ============================================================================

# Primary index name for vector search
INDEX_NAME = "products-semantic-search"

# Vector field dimensions (must match embedding model)
# text-embedding-3-small: 1536
# text-embedding-3-large: 3072
# text-embedding-ada-002: 1536
VECTOR_DIMENSIONS = 1536

# Enable scalar quantization for memory reduction
USE_QUANTIZATION = True

# Number of shards for the index
NUMBER_OF_SHARDS = 1

# Number of replicas
NUMBER_OF_REPLICAS = 0

# ============================================================================
# Search Configuration
# ============================================================================

# Number of results to return from searches
DEFAULT_SEARCH_SIZE = 10

# Number of candidates for kNN search (higher = better recall, slower)
KNN_NUM_CANDIDATES = 100

# RRF rank constant for hybrid search
# Lower values (1-20) give more weight to top-ranked results
# Higher values (60-100) distribute weight more evenly
RRF_RANK_CONSTANT = 60

# ============================================================================
# RAG Configuration
# ============================================================================

# Number of documents to retrieve for RAG context
RAG_TOP_K = 3

# Maximum conversation history length (in messages)
MAX_CONVERSATION_HISTORY = 10

# System prompt for RAG chatbot
RAG_SYSTEM_PROMPT = """You are a helpful product assistant for an electronics store.

RULES:
1. Only answer questions using information from the provided product search results
2. If no relevant products are found, say "I don't have information about that"
3. Always include product names and prices in your recommendations
4. Do not make up specifications, features, or prices
5. Be concise (max 3-4 sentences per product mentioned)
6. If asked about something outside the product catalog, politely decline

Format your responses to be helpful and informative."""

# ============================================================================
# Data Configuration
# ============================================================================

# Path to sample data file
SAMPLE_DATA_PATH = "data/sample_documents.json"

# Batch size for embedding generation
EMBEDDING_BATCH_SIZE = 100

# Batch size for bulk indexing
BULK_INDEX_BATCH_SIZE = 100

# ============================================================================
# Development Settings
# ============================================================================

# Enable verbose logging
VERBOSE = True

# Enable response caching (for development)
ENABLE_CACHE = False

# Retry settings for API calls
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# ============================================================================
# Cost Tracking (Optional)
# ============================================================================

# Track API costs
TRACK_COSTS = True

# Approximate costs per 1M tokens (update these based on current OpenAI pricing)
COST_PER_1M_EMBEDDING_TOKENS = {
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
    "text-embedding-ada-002": 0.10,
}

COST_PER_1M_LLM_INPUT_TOKENS = {
    "gpt-4-turbo-preview": 10.00,
    "gpt-4": 30.00,
    "gpt-3.5-turbo": 0.50,
}

COST_PER_1M_LLM_OUTPUT_TOKENS = {
    "gpt-4-turbo-preview": 30.00,
    "gpt-4": 60.00,
    "gpt-3.5-turbo": 1.50,
}
