# AI-Powered Search and Chat with Elasticsearch

A hands-on workshop for building intelligent search and conversational AI using **ELSER** (Elasticsearch's built-in semantic search model).

## Why ELSER?

This workshop uses ELSER as the primary approach because:
- ✅ **No API keys required** - Runs entirely within Elasticsearch
- ✅ **No per-query costs** - Only infrastructure costs
- ✅ **Lower latency** - No external API calls
- ✅ **Semantic understanding** - Understands meaning, not just keywords
- ✅ **Simple setup** - Automated deployment scripts included

## What You'll Build

### Part 1: Smart Search That Actually Works (~2 hours)
1. **Setup ELSER** - Automated deployment and index creation
2. **Ingest Data** - Load sample products with automatic embedding generation
3. **Semantic Search** - Natural language queries with ELSER
4. **Keyword Search** - Traditional BM25 for comparison
5. **Hybrid Search** - Best of both worlds using Reciprocal Rank Fusion

### Part 2: Conversational AI (~1 hour)
1. **Basic RAG** - Retrieval Augmented Generation with ELSER + GPT
2. **Context Chat** - Conversational memory (coming soon)
3. **Controlled Responses** - Prompt engineering and guardrails (coming soon)

> **Note:** Part 2 requires OpenAI API key for the LLM (GPT), but retrieval uses ELSER

## Prerequisites

Before starting, you **must** have:

1. **Elasticsearch 8.8+** (ELSER v2 requires 8.8 or higher)
2. **At least 4GB RAM** for ML nodes
3. **Python 3.8+**
4. **(Optional) OpenAI API key** - Only for Part 2 conversational AI

📖 **Detailed Setup**: See [PREREQUISITES.md](PREREQUISITES.md)

## Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd elasticsearch-ai-search-chat-demo

# Install core dependencies (no OpenAI needed for Part 1!)
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.example.py config.py
```

Edit `config.py` with your Elasticsearch credentials:

```python
ELASTICSEARCH_URL = "http://localhost:9200"
ELASTICSEARCH_USERNAME = "elastic"
ELASTICSEARCH_PASSWORD = "elastic"

# ELSER is the default - no changes needed!
EMBEDDING_METHOD = "elser"
```

### 3. Run Part 1 - Smart Search

```bash
# Step 1: Setup ELSER (downloads model, creates index)
python part1_smart_search/01_setup_index.py

# Step 2: Load sample data with ELSER embeddings
python part1_smart_search/02_ingest_data.py

# Step 3: Try semantic search!
python part1_smart_search/03_semantic_search.py "laptop for programming"

# Step 4: Compare with keyword search
python part1_smart_search/04_keyword_search.py "laptop for programming"

# Step 5: Best results with hybrid search
python part1_smart_search/05_hybrid_search.py "laptop for programming"
```

### 4. (Optional) Run Part 2 - Conversational AI

For Part 2, you'll need OpenAI API key:

```bash
# Install OpenAI package
pip install openai

# Add to config.py:
# OPENAI_API_KEY = "sk-your-key-here"

# Run basic RAG
python part2_conversational_ai/01_basic_rag.py "What laptops do you have for video editing?"
```

## Project Structure

```
elasticsearch-ai-search-chat-demo/
├── README.md                          # This file
├── PREREQUISITES.md                   # Detailed setup guide
├── ELSER_SETUP.md                     # Deep dive on ELSER
├── requirements.txt                   # Python dependencies (OpenAI optional)
├── config.example.py                  # Example configuration
├── data/
│   └── sample_documents.json         # Sample product catalog
│
├── part1_smart_search/                # Smart Search Workshop (ELSER)
│   ├── 01_setup_index.py            # ELSER setup and index creation
│   ├── 02_ingest_data.py            # Load data with ELSER embeddings
│   ├── 03_semantic_search.py        # Semantic search with ELSER
│   ├── 04_keyword_search.py         # Traditional keyword search (BM25)
│   └── 05_hybrid_search.py          # Hybrid search (ELSER + BM25)
│
├── part2_conversational_ai/           # Conversational AI (ELSER + OpenAI)
│   ├── 01_basic_rag.py              # RAG with ELSER retrieval
│   ├── 02_context_chat.py           # With conversation memory (coming soon)
│   └── 03_controlled_responses.py   # Prompt engineering (coming soon)
│
├── scripts/                           # Standalone ELSER scripts
│   ├── setup-elser.py               # Standalone ELSER setup
│   ├── ingest-with-elser.py         # Standalone data ingestion
│   ├── search-with-elser.py         # Interactive search tool
│   └── README-ELSER.md              # ELSER scripts quick reference
│
└── examples/
    └── openai_alternative/            # OpenAI-based alternatives
        ├── README.md                  # How to use OpenAI instead
        └── *.py                       # Original OpenAI-based scripts
```

## Example Queries to Try

### Semantic Search Queries (ELSER understands these!)

```bash
# Intent-based
python part1_smart_search/03_semantic_search.py "laptop for programming and video editing"

# Conceptual
python part1_smart_search/03_semantic_search.py "affordable portable computer for developers"

# Use-case
python part1_smart_search/03_semantic_search.py "equipment for remote work setup"

# Feature-based
python part1_smart_search/03_semantic_search.py "wireless devices with long battery life"
```

### Keyword Search Queries (exact terms)

```bash
# Specific models
python part1_smart_search/04_keyword_search.py "Dell XPS"

# Technical specs
python part1_smart_search/04_keyword_search.py "SSD NVMe"
```

### Hybrid Search (best results!)

```bash
# Combines meaning + exact terms
python part1_smart_search/05_hybrid_search.py "Dell laptop for machine learning under $2000"
```

## Key Concepts

### ELSER (Elastic Learned Sparse EncodeR)

ELSER is Elasticsearch's built-in ML model that:
- Expands queries and documents into weighted tokens
- Understands semantic relationships (synonyms, related concepts)
- Optimized for English language text
- Uses **sparse vectors** (only non-zero values stored)
- No external dependencies or API calls

### Hybrid Search with RRF

Combines two search methods:
1. **Semantic Search (ELSER)** - Understands meaning and intent
2. **Keyword Search (BM25)** - Matches exact terms

**Reciprocal Rank Fusion (RRF)** intelligently merges results:
```
RRF_score = 1/(k + rank_elser) + 1/(k + rank_bm25)
```

Hybrid search typically provides the best results!

### RAG (Retrieval Augmented Generation)

RAG prevents AI hallucinations by:
1. **Retrieve** - Search for relevant documents (using ELSER)
2. **Augment** - Add documents as context to LLM prompt
3. **Generate** - LLM creates response based ONLY on retrieved context

The LLM can't make up facts because it only sees your actual data!

## Troubleshooting

### "Index does not exist"
- Run scripts in order: 01 → 02 → 03/04/05

### "Could not connect to Elasticsearch"
- Check Elasticsearch is running: `curl http://localhost:9200`
- Verify credentials in `config.py`

### "ELSER model not ready"
- First-time setup takes 2-5 minutes to download model
- Check status: `GET _ml/trained_models/.elser_model_2/_stats`

### "OpenAI API key error" (Part 2 only)
- Part 2 requires OpenAI for LLM (GPT)
- Add API key to config.py
- Install OpenAI: `pip install openai`

## What About OpenAI Embeddings?

Want to use OpenAI embeddings instead of ELSER? Check [examples/openai_alternative/README.md](examples/openai_alternative/README.md)

OpenAI may be better if you need:
- Multi-language support (ELSER is English-only)
- Cross-modal search (images, code, etc.)
- Already using OpenAI for other features

## Documentation

- **[PREREQUISITES.md](PREREQUISITES.md)** - Detailed infrastructure setup
- **[ELSER_SETUP.md](ELSER_SETUP.md)** - Deep dive on ELSER configuration
- **[scripts/README-ELSER.md](scripts/README-ELSER.md)** - ELSER scripts reference
- **[examples/openai_alternative/README.md](examples/openai_alternative/README.md)** - Using OpenAI instead

## Resources

### Elasticsearch Documentation
- [ELSER Guide](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)
- [Inference API](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html)
- [Sparse Vector Field](https://www.elastic.co/guide/en/elasticsearch/reference/current/sparse-vector.html)

### Blog Posts
- [Elasticsearch: Retrieval Augmented Generation](https://www.elastic.co/blog/retrieval-augmented-generation-elasticsearch)
- [Hybrid Search Best Practices](https://www.elastic.co/blog/hybrid-search-elastic-part-1)

## Cost Analysis

### ELSER (Main Workshop)
- **Infrastructure**: ML node resources (same as general Elasticsearch node)
- **Per-Query**: $0 (no external API calls)
- **For this workshop**: Included in Elasticsearch costs

### OpenAI Alternative
- **Embeddings**: $0.02/1M tokens (text-embedding-3-small)
- **LLM**: $0.50/1M tokens (gpt-3.5-turbo)
- **For this workshop**: ~$1 total

## License

This project is provided as-is for educational purposes.

## Contributing

Contributions welcome! Please:
- Follow existing code style
- Test all scripts before submitting
- Update documentation for new features

## Author

Workshop created by Brian Mayrose

Inspired by real-world Elasticsearch implementations and best practices from the Elastic community.

## Support

For issues:
1. Check [PREREQUISITES.md](PREREQUISITES.md) for setup
2. Review [ELSER_SETUP.md](ELSER_SETUP.md) for ELSER-specific issues
3. Consult official Elasticsearch documentation
4. Open an issue on GitHub
