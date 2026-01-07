# Quick Start Guide

Get up and running with ELSER-powered search in 10 minutes!

## Prerequisites

1. **Elasticsearch 8.8+** running (see [PREREQUISITES.md](PREREQUISITES.md))
2. **Python 3.8+** installed

**That's it!** No API keys needed for Part 1.

## 5-Minute Setup

### 1. Clone and Configure

```bash
# Clone repository
cd ~/dev/elasticsearch-ai-search-chat-demo

# Copy example config
cp config.example.py config.py

# Edit config.py with your Elasticsearch credentials
# Default works for local helm deployment:
#   ELASTICSEARCH_URL = "http://localhost:9200"
#   ELASTICSEARCH_USERNAME = "elastic"
#   ELASTICSEARCH_PASSWORD = "elastic"
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install packages (no OpenAI needed!)
pip install -r requirements.txt
```

### 3. Run Part 1 - Smart Search

```bash
# Step 1: Setup ELSER (downloads model, ~2-5 minutes first time)
python part1_smart_search/01_setup_index.py

# Step 2: Load sample data (~2-3 minutes for 500 products)
python part1_smart_search/02_ingest_data.py

# Step 3: Try it out!
python part1_smart_search/03_semantic_search.py "laptop for programming"
```

**Total time:** ~5-8 minutes

## Try It Out

### Semantic Search (Natural Language)

```bash
# Intent-based
python part1_smart_search/03_semantic_search.py "laptop for programming and video editing"

# Conceptual
python part1_smart_search/03_semantic_search.py "affordable portable computer for developers"

# Use-case
python part1_smart_search/03_semantic_search.py "equipment for remote work"
```

### Keyword Search (Exact Terms)

```bash
# Specific models
python part1_smart_search/04_keyword_search.py "Dell XPS"

# Technical specs
python part1_smart_search/04_keyword_search.py "SSD NVMe"
```

### Hybrid Search (Best Results!)

```bash
# Combines meaning + exact terms
python part1_smart_search/05_hybrid_search.py "Dell laptop for machine learning under $2000"
```

## Optional: Part 2 - Conversational AI

For the chatbot, you'll need OpenAI API key:

### 1. Install OpenAI

```bash
pip install openai
```

### 2. Add API Key

Edit `config.py`:
```python
OPENAI_API_KEY = "sk-your-api-key-here"
```

Get key from: https://platform.openai.com/api-keys

### 3. Run RAG Chatbot

```bash
python part2_conversational_ai/01_basic_rag.py "What laptops do you have for video editing?"
```

## Common Issues

### "Could not connect to Elasticsearch"

**Check if Elasticsearch is running:**
```bash
curl http://localhost:9200
```

**If using kubectl:**
```bash
kubectl get pods -n elastic
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
```

**Verify credentials** in `config.py`

### "ELSER model not ready"

First-time setup downloads the model (~2-5 minutes).

**Check status:**
```bash
curl http://localhost:9200/_ml/trained_models/.elser_model_2/_stats
```

Look for `"state": "started"`

### "ModuleNotFoundError"

**Activate virtual environment:**
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Reinstall dependencies:**
```bash
pip install -r requirements.txt
```

## Cost Estimate

### Part 1 (ELSER Search)
- **Infrastructure**: Elasticsearch only
- **API costs**: $0 (ELSER runs in Elasticsearch)

### Part 2 (Conversational AI) - Optional
- **Search**: $0 (uses ELSER)
- **LLM responses** (20 messages): ~$0.10 - $0.50
- **Total**: Under $1 for entire workshop

## What's Different from Other Tutorials?

✅ **No API keys for search** - ELSER runs in Elasticsearch
✅ **No per-query costs** - Only infrastructure
✅ **Semantic understanding** - Built-in, no external service
✅ **Lower latency** - No external API calls
✅ **Simpler setup** - Start with just Elasticsearch

## Project Structure

```
part1_smart_search/
├── 01_setup_index.py      # Setup ELSER (run once)
├── 02_ingest_data.py       # Load sample data (run once)
├── 03_semantic_search.py   # Try semantic search
├── 04_keyword_search.py    # Try keyword search
└── 05_hybrid_search.py     # Try hybrid search

part2_conversational_ai/
└── 01_basic_rag.py         # RAG chatbot (needs OpenAI)
```

## Next Steps

1. **Try different queries** - See how ELSER understands meaning
2. **Compare search methods** - Run same query with 03, 04, 05
3. **Read [README.md](README.md)** - Understand how it works
4. **Explore [ELSER_SETUP.md](ELSER_SETUP.md)** - Deep dive on ELSER
5. **Modify data** - Edit `data/sample_documents.json`

## Alternative: Use OpenAI Embeddings

Want to use OpenAI instead of ELSER?

See [examples/openai_alternative/README.md](examples/openai_alternative/README.md) for:
- When to use OpenAI vs ELSER
- How to switch to OpenAI embeddings
- Multi-language support
- Cross-modal search

## Getting Help

**Elasticsearch connection issues:**
- Check [PREREQUISITES.md](PREREQUISITES.md)
- Verify version: `curl http://localhost:9200`

**ELSER issues:**
- See [ELSER_SETUP.md](ELSER_SETUP.md)
- Check ML nodes: `curl http://localhost:9200/_cat/ml/nodes?v`

**OpenAI issues (Part 2 only):**
- Verify API key: https://platform.openai.com/api-keys
- Check credits: https://platform.openai.com/account/billing

## What You'll Learn

By the end of this workshop:

✅ How ELSER provides semantic search without API keys
✅ Difference between keyword, semantic, and hybrid search
✅ How hybrid search (RRF) combines the best of both
✅ How to implement RAG to prevent AI hallucinations
✅ When to use ELSER vs OpenAI embeddings

Enjoy the workshop! 🚀
