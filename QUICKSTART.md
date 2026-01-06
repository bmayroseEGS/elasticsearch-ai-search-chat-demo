# Quick Start Guide

Get up and running with the AI-Powered Search and Chat workshop in 15 minutes!

## Prerequisites

1. **Elasticsearch & Kibana** running (see [PREREQUISITES.md](PREREQUISITES.md))
2. **Python 3.8+** installed
3. **OpenAI API key** with credits

## 5-Minute Setup

### 1. Create Configuration

```bash
# Copy example config
cp config.example.py config.py

# Edit with your credentials
# - Add Elasticsearch URL (default: http://localhost:9200)
# - Add OpenAI API key
```

### 2. Install Dependencies

```bash
# Recommended: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install packages
pip install -r requirements.txt
```

### 3. Run Setup Script

```bash
./scripts/setup-environment.sh
```

This script will:
- Create the Elasticsearch index with vector mappings
- Generate embeddings for sample products (~$0.05)
- Index all documents
- Verify everything is ready

**Total time:** ~5 minutes (depending on internet speed)

## Try It Out

### Part 1: Smart Search (2 minutes)

**Keyword Search (BM25):**
```bash
python3 part1_smart_search/03_keyword_search.py "MacBook Pro"
```

**Semantic Search (Vectors):**
```bash
python3 part1_smart_search/04_semantic_search.py "portable computer for programming"
```

**Hybrid Search (Best Results):**
```bash
python3 part1_smart_search/05_hybrid_search.py "affordable gaming laptop"
```

### Part 2: Conversational AI (5 minutes)

**Basic RAG Chatbot:**
```bash
python3 part2_conversational_ai/01_basic_rag.py
```

Try asking: "What laptops do you have for video editing?"

**Chat with Memory:**
```bash
python3 part2_conversational_ai/02_context_chat.py
```

Try this conversation:
1. "Show me gaming laptops"
2. "Which one has the best GPU?"
3. "How much does it cost?"

**Controlled Responses:**
```bash
python3 part2_conversational_ai/03_controlled_responses.py
```

Choose option 1 to see automated test scenarios.

## Common Issues

### "Could not connect to Elasticsearch"

**Check:**
```bash
# Is Elasticsearch running?
curl http://localhost:9200

# Are port-forwards active? (if using Kubernetes)
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
```

### "Invalid API key" (OpenAI)

**Fix:**
1. Get a new key: https://platform.openai.com/api-keys
2. Update `config.py` with the new key
3. Ensure you have credits: https://platform.openai.com/account/billing

### "ModuleNotFoundError"

**Fix:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Cost Estimate

For the complete workshop:

- **Embeddings** (500 products): ~$0.01 - $0.05
- **Search queries** (20 queries): ~$0.01
- **Chat interactions** (20 messages): ~$0.10 - $0.50

**Total: Under $1** for the entire workshop

## Next Steps

1. **Read the main README.md** for detailed explanations
2. **Review [PREREQUISITES.md](PREREQUISITES.md)** for infrastructure details
3. **Experiment** with your own queries and data
4. **Modify** the sample dataset in `data/sample_documents.json`
5. **Customize** prompts and search parameters in `config.py`

## Reset and Start Over

To delete everything and start fresh:

```bash
./scripts/reset-environment.sh
./scripts/setup-environment.sh
```

## Getting Help

- **Elasticsearch issues**: Check [PREREQUISITES.md](PREREQUISITES.md)
- **OpenAI issues**: https://platform.openai.com/docs
- **Python issues**: Verify Python 3.8+ with `python3 --version`

## What You'll Learn

By the end of this workshop, you'll understand:

✅ How to set up vector search in Elasticsearch
✅ Difference between keyword, semantic, and hybrid search
✅ How to implement RAG to prevent AI hallucinations
✅ How to build conversational AI with memory
✅ How to control AI behavior with prompt engineering
✅ Memory optimization with scalar quantization

Enjoy the workshop! 🚀
