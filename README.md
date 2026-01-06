# AI-Powered Search and Chat with Elasticsearch

A hands-on workshop for building intelligent search and conversational AI using Elasticsearch's vector search capabilities and LLM integration.

## Overview

This workshop demonstrates how to create a complete AI-powered search and chat application using Elasticsearch. You'll build search that understands meaning (not just keywords) and conversational AI that doesn't hallucinate because it's grounded in your actual data.

## What You'll Build

### Part 1: Smart Search That Actually Works (2 hours)
- **Semantic search** that understands meaning, not just keywords
- **Hybrid search** combining BM25 (keyword) and vector similarity for best results
- **Vector embeddings** deployed efficiently using quantization
- **Memory optimization** techniques that reduce usage by ~95%

### Part 2: Conversational AI That Doesn't Hallucinate (1 hour)
- **RAG (Retrieval Augmented Generation)** chatbot grounded in real data
- **Conversational memory** for context-aware interactions
- **Controlled AI responses** using prompt engineering
- **Hallucination prevention** through search-based grounding

## Prerequisites

Before starting this workshop, you **must** have a running Elasticsearch and Kibana deployment. See [PREREQUISITES.md](PREREQUISITES.md) for detailed setup instructions.

### Quick Prerequisites Summary

- **Elasticsearch 8.x or 9.x** with vector search capabilities
- **Kibana** for Dev Tools and monitoring
- **Python 3.8+** for running example scripts
- **OpenAI API key** (or compatible embedding/LLM provider)

## Quick Start Using helm-elastic-fleet-quickstart

If you don't have Elasticsearch deployed yet, use the [helm-elastic-fleet-quickstart](https://github.com/bmayroseEGS/helm-elastic-fleet-quickstart) repository to set up your infrastructure. See [PREREQUISITES.md](PREREQUISITES.md) for step-by-step instructions.

## Project Structure

```
elasticsearch-ai-search-chat-demo/
├── README.md                          # This file
├── PREREQUISITES.md                   # Setup requirements and infrastructure
├── requirements.txt                   # Python dependencies
├── config.example.py                  # Example configuration file
├── data/
│   └── sample_documents.json         # Sample product catalog dataset
├── scripts/
│   ├── setup-environment.sh          # Initialize indices and templates
│   └── reset-environment.sh          # Reset to initial state
├── part1_smart_search/
│   ├── 01_setup_index.py            # Create index with vector mappings
│   ├── 02_generate_embeddings.py    # Generate embeddings and index data
│   ├── 03_keyword_search.py         # Traditional BM25 keyword search
│   ├── 04_semantic_search.py        # Pure vector similarity search
│   └── 05_hybrid_search.py          # Combined hybrid search (RRF)
├── part2_conversational_ai/
│   ├── 01_basic_rag.py              # Simple RAG implementation
│   ├── 02_context_chat.py           # Conversation with memory
│   └── 03_controlled_responses.py   # Prompt engineering and guardrails
└── notebooks/
    ├── search_workshop.ipynb        # Interactive search examples
    └── chat_workshop.ipynb          # Interactive chat examples
```

## Installation

### 1. Clone This Repository

```bash
git clone <your-repo-url>
cd elasticsearch-ai-search-chat-demo
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Credentials

Copy the example configuration and add your credentials:

```bash
cp config.example.py config.py
```

Edit `config.py` with your details:

```python
# Elasticsearch connection
ELASTICSEARCH_URL = "http://localhost:9200"
ELASTICSEARCH_API_KEY = "your-api-key-here"  # Or use username/password

# OpenAI configuration
OPENAI_API_KEY = "your-openai-api-key"
EMBEDDING_MODEL = "text-embedding-3-small"  # Or "text-embedding-ada-002"
LLM_MODEL = "gpt-4-turbo-preview"           # Or "gpt-3.5-turbo"
```

### 4. Initialize the Environment

Run the setup script to create indices and load sample data:

```bash
cd scripts
./setup-environment.sh
```

This script will:
- Create an index with proper vector field mappings
- Configure scalar quantization for 95% memory reduction
- Load sample product catalog data
- Generate embeddings for all documents
- Verify the environment is ready

## Workshop Guide

### Part 1: Smart Search That Actually Works

#### Step 1: Understand the Data

Review the sample dataset in [data/sample_documents.json](data/sample_documents.json). We're using a product catalog with:
- Product names and descriptions
- Categories and prices
- Technical specifications
- Customer reviews

#### Step 2: Set Up the Index

Run the index setup script to create an index with vector field mappings:

```bash
python part1_smart_search/01_setup_index.py
```

**What this does:**
- Creates index `products-semantic-search`
- Defines `dense_vector` field for embeddings (1536 dimensions for OpenAI)
- Configures **scalar quantization** to reduce memory by ~95%
- Sets up text fields for keyword search

**Key concept:** Scalar quantization converts 32-bit floats to 8-bit integers, dramatically reducing memory usage with minimal accuracy loss (~1-2% retrieval quality).

#### Step 3: Generate and Index Embeddings

```bash
python part1_smart_search/02_generate_embeddings.py
```

**What this does:**
- Reads sample documents
- Calls OpenAI API to generate embeddings for each product
- Indexes documents with embeddings into Elasticsearch
- Shows progress and costs

**Optimization tip:** Batch embedding requests to reduce API calls and costs.

#### Step 4: Compare Search Methods

Now try different search approaches on the same query:

**Traditional Keyword Search (BM25):**
```bash
python part1_smart_search/03_keyword_search.py "laptop for programming"
```

**Semantic Search (Vector Similarity):**
```bash
python part1_smart_search/04_semantic_search.py "laptop for programming"
```

**Hybrid Search (Best of Both):**
```bash
python part1_smart_search/05_hybrid_search.py "laptop for programming"
```

**Try these queries to see the difference:**
- "affordable computer for coding" (semantic understanding)
- "XPS 15" (exact keyword match)
- "machine learning workstation under $2000" (hybrid combines both)

**Key insight:** Hybrid search using RRF (Reciprocal Rank Fusion) typically provides the best results by combining:
- **Keyword search** for exact matches and specific terms
- **Semantic search** for understanding intent and context

### Part 2: Conversational AI That Doesn't Hallucinate

#### Step 1: Basic RAG Implementation

Run the basic RAG chatbot:

```bash
python part2_conversational_ai/01_basic_rag.py
```

**How it works:**
1. User asks a question: "What laptops do you have for video editing?"
2. System generates embedding for the question
3. Elasticsearch searches for relevant products using vector similarity
4. Top results are sent to LLM as context
5. LLM generates response based **only** on the provided context

**Key concept:** RAG (Retrieval Augmented Generation) grounds LLM responses in your actual data, preventing hallucinations.

#### Step 2: Conversational Chat with Memory

Run the chatbot with conversation memory:

```bash
python part2_conversational_ai/02_context_chat.py
```

**Example conversation:**
```
User: What gaming laptops do you have?
Bot: [Lists gaming laptops from search results]

User: Which one has the best GPU?
Bot: [Remembers previous context, compares GPUs from those laptops]

User: How much is it?
Bot: [Knows "it" refers to the laptop just discussed]
```

**How memory works:**
- Previous messages are included in the prompt
- Each new search uses conversation context for better relevance
- LLM maintains coherent dialogue across multiple turns

#### Step 3: Controlled Responses with Prompt Engineering

Run the chatbot with guardrails:

```bash
python part2_conversational_ai/03_controlled_responses.py
```

**What's different:**
- **Strict instructions** for the LLM about what it can/cannot say
- **Response format** requirements (e.g., always include price)
- **Boundary enforcement** (only answer product questions)
- **Tone control** (professional, helpful, concise)

**Example prompt engineering:**
```
You are a helpful product assistant.
RULES:
1. Only answer questions about products in the search results
2. If no relevant products found, say "I don't have information about that"
3. Always include product names and prices in recommendations
4. Do not make up specifications or features
5. Be concise (max 3 sentences per product)
```

## Interactive Notebooks

For hands-on experimentation, use the Jupyter notebooks:

```bash
jupyter notebook notebooks/search_workshop.ipynb
```

The notebooks provide:
- Interactive examples of all search types
- Visualization of search results and rankings
- Side-by-side comparison of keyword vs semantic search
- Embedding similarity analysis
- RAG pipeline walkthrough

## Key Concepts Explained

### Semantic Search vs Keyword Search

**Keyword Search (BM25):**
- Matches exact terms in the query
- Good for specific names, model numbers, SKUs
- Example: "MacBook Pro 16" finds exact matches

**Semantic Search (Vector Similarity):**
- Understands meaning and intent
- Good for natural language queries
- Example: "portable computer for developers" matches laptops even without those exact words

### Hybrid Search with RRF

**Reciprocal Rank Fusion (RRF)** combines rankings from multiple search methods:

```
RRF_score = 1/(k + rank_keyword) + 1/(k + rank_semantic)
```

Where `k=60` is a constant that controls the impact of different rankings.

**Benefits:**
- Balances precision (keyword) and recall (semantic)
- Works well across different query types
- Often outperforms either method alone

### Vector Quantization

**Without Quantization:**
- 1536-dimensional vector (OpenAI embeddings)
- 4 bytes per dimension (float32)
- Memory per vector: 1536 × 4 = 6,144 bytes (~6 KB)

**With Scalar Quantization:**
- Same 1536 dimensions
- 1 byte per dimension (int8)
- Memory per vector: 1536 × 1 = 1,536 bytes (~1.5 KB)
- **Reduction: 75% smaller** in storage, even more in RAM due to indexing overhead

For 1 million documents:
- Unquantized: ~6 GB
- Quantized: ~1.5 GB
- **Savings: ~4.5 GB**

### RAG Architecture

```
User Question
    ↓
Generate Query Embedding
    ↓
Search Elasticsearch (Vector Similarity)
    ↓
Retrieve Top K Documents
    ↓
Format as Context for LLM
    ↓
LLM Generates Response
    ↓
Return Answer to User
```

**Why this prevents hallucinations:**
- LLM only sees information from search results
- Cannot make up facts not in your data
- If no relevant results found, LLM can say "I don't know"

## Best Practices

### For Search

1. **Use hybrid search by default** - Combines strengths of both approaches
2. **Tune RRF rank constant** - Adjust `k` parameter (typically 1-100) based on your data
3. **Enable quantization** - Reduces memory by ~95% with minimal quality loss
4. **Monitor relevance** - Track click-through rates and user feedback
5. **A/B test search methods** - Compare keyword vs semantic vs hybrid for your use case

### For Conversational AI

1. **Always retrieve first** - Never rely on LLM memory for facts
2. **Limit context size** - Use top 3-5 search results to avoid overwhelming the LLM
3. **Validate responses** - Check that answers are grounded in retrieved context
4. **Handle no-results** - Train LLM to admit when it doesn't have information
5. **Manage conversation length** - Summarize or truncate old messages to stay within token limits
6. **Use prompt templates** - Standardize system prompts for consistent behavior

### For Production

1. **Cache embeddings** - Store vectors with documents, don't regenerate on every search
2. **Batch operations** - Generate embeddings in batches to reduce API costs
3. **Monitor costs** - Track OpenAI API usage for embeddings and LLM calls
4. **Implement rate limiting** - Protect against API quota exhaustion
5. **Handle failures gracefully** - Fallback to keyword search if embedding generation fails
6. **Log queries and results** - Track performance and identify areas for improvement

## Troubleshooting

### Search returns no results

**Check:**
1. Are documents indexed? `GET products-semantic-search/_count`
2. Do documents have embeddings? Check `embedding_vector` field exists
3. Is query embedding generated successfully? Check API key and model name

### Semantic search performs poorly

**Try:**
1. Verify embedding model matches (generation and search must use same model)
2. Increase `num_candidates` in kNN search for better recall
3. Check if quantization is impacting quality (compare with/without)
4. Review sample queries - semantic search works best for natural language

### LLM responses are inaccurate

**Check:**
1. Are retrieved documents relevant? Review search results separately
2. Is context too long? LLM may miss details in large contexts
3. Are instructions clear? Improve system prompt with specific examples
4. Is LLM hallucinating? Emphasize "only use provided context" in prompt

### High costs

**Reduce:**
1. Use smaller embedding model (ada-002 vs text-embedding-3-large)
2. Use cheaper LLM (gpt-3.5-turbo vs gpt-4)
3. Cache embeddings to avoid regenerating
4. Reduce conversation history length
5. Implement request deduplication

## Advanced Topics

### Custom Embedding Models

Instead of OpenAI, you can use:
- **Sentence Transformers** (open source, run locally)
- **Cohere embeddings** (alternative API)
- **Elasticsearch ELSER** (learned sparse encoder)
- **Custom fine-tuned models** for domain-specific search

### Hybrid Search Variations

- **Weighted hybrid** - Adjust importance of keyword vs semantic (not just RRF)
- **Multi-field semantic** - Embed title separately from description
- **Filtered semantic** - Combine filters (price, category) with vector search

### Advanced RAG Patterns

- **Re-ranking** - Use cross-encoder to re-score search results before LLM
- **Query expansion** - Use LLM to generate multiple query variations
- **Iterative retrieval** - LLM requests more context if initial results insufficient
- **Fact verification** - Validate LLM statements against source documents

## Example Queries to Try

### Test Keyword vs Semantic Differences

| Query | Keyword Search | Semantic Search | Why Different? |
|-------|----------------|-----------------|----------------|
| "gaming rig" | May miss "gaming laptop" | Finds gaming laptops | Understands synonyms |
| "ASUS ROG Strix" | Exact matches | Broader gaming laptops | Literal vs conceptual |
| "budget machine learning computer" | Misses if no exact terms | Finds powerful affordable laptops | Understands intent |
| "Model X123" | Perfect match | Irrelevant results | Model numbers need exact match |

**Conclusion:** Hybrid search handles all these cases well.

### Test Conversational Understanding

Try this conversation flow:

```
1. "Show me laptops under $1000"
2. "Which one has the best battery life?"  # Requires context
3. "Tell me more about it"                # Requires conversation memory
4. "How does it compare to the Lenovo?"   # Entity resolution
```

## Resources and References

### Elasticsearch Documentation
- [Vector Search Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)
- [Dense Vector Field Type](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html)
- [Quantization](https://www.elastic.co/guide/en/elasticsearch/reference/current/quantization.html)

### OpenAI Documentation
- [Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Text Embedding Models](https://platform.openai.com/docs/guides/embeddings/embedding-models)
- [Chat Completions API](https://platform.openai.com/docs/guides/chat)

### Blog Posts and Tutorials
- [Elasticsearch: Retrieval Augmented Generation](https://www.elastic.co/blog/retrieval-augmented-generation-elasticsearch)
- [Hybrid Search Best Practices](https://www.elastic.co/blog/hybrid-search-elastic-part-1)
- [Vector Search Memory Optimization](https://www.elastic.co/blog/scalar-quantization-elasticsearch-8-15)

## License

This project is provided as-is for educational purposes.

## Support

For issues:
1. Check [PREREQUISITES.md](PREREQUISITES.md) for infrastructure setup
2. Review troubleshooting section above
3. Consult official Elasticsearch and OpenAI documentation

## Contributing

Contributions welcome! Please:
- Follow existing code style
- Test all scripts before submitting
- Update documentation for new features
- Include example queries for new search patterns

## Author

Workshop created by Brian Mayrose

Inspired by real-world Elasticsearch implementations and best practices from the Elastic community.
