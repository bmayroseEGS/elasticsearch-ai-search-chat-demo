# OpenAI Alternative Examples

This directory contains the original scripts that use OpenAI for embeddings and LLM functionality.

## About These Scripts

These scripts demonstrate how to build AI-powered search and chat using:
- **OpenAI embeddings** (text-embedding-3-small) for dense vectors
- **OpenAI GPT models** for conversational AI

## Why This is "Alternative"

The main workshop now uses **ELSER** (Elasticsearch's built-in semantic search model) as the primary approach because:
- ✅ No external API keys required
- ✅ No per-query costs
- ✅ Lower latency (no external API calls)
- ✅ Runs entirely within Elasticsearch

## When to Use OpenAI Instead

Consider using these OpenAI-based scripts if you need:
- **Multi-language support** - ELSER is English-only
- **Cross-modal search** - Embedding images, code, etc.
- **Latest OpenAI models** - Access to GPT-4 and newest embeddings
- **Existing OpenAI integration** - Already using OpenAI for other features

## Using These Scripts

### 1. Update Configuration

Edit `config.py` to enable OpenAI:

```python
# Change embedding method
EMBEDDING_METHOD = "openai"

# Add your OpenAI API key
OPENAI_API_KEY = "sk-your-api-key-here"

# Use OpenAI index name
INDEX_NAME = "products-openai-search"
```

### 2. Install OpenAI Package

Uncomment in `requirements.txt`:

```bash
# Uncomment this line:
openai>=1.0.0
```

Then install:

```bash
pip install openai
```

### 3. Run the Scripts

Follow the same order as the main workshop:

**Part 1: Smart Search**
```bash
python examples/openai_alternative/01_setup_index.py
python examples/openai_alternative/02_generate_embeddings.py
python examples/openai_alternative/03_keyword_search.py
python examples/openai_alternative/04_semantic_search.py
python examples/openai_alternative/05_hybrid_search.py
```

**Part 2: Conversational AI**
```bash
python examples/openai_alternative/01_basic_rag.py
python examples/openai_alternative/02_context_chat.py
python examples/openai_alternative/03_controlled_responses.py
```

## Cost Estimates

Using OpenAI for this workshop:

**Embeddings (one-time for 500 products):**
- Model: text-embedding-3-small
- Cost: ~$0.01 - $0.05

**LLM Queries (100 interactions):**
- Model: gpt-3.5-turbo
- Cost: ~$0.10 - $0.50

**Total: Under $1 for the entire workshop**

## Comparison: ELSER vs OpenAI

| Feature | ELSER (Main Workshop) | OpenAI (These Scripts) |
|---------|----------------------|------------------------|
| **API Key Required** | No | Yes |
| **Cost** | Infrastructure only | Per-token pricing |
| **Latency** | Low (internal) | Higher (API calls) |
| **Languages** | English only | 100+ languages |
| **Setup Complexity** | Medium | Low |
| **Vector Type** | Sparse | Dense |
| **Memory Usage** | Lower | Higher |
| **Offline Capable** | Yes | No |

## Converting Back to ELSER

To switch back to the main ELSER-based workshop:

1. Edit `config.py`:
   ```python
   EMBEDDING_METHOD = "elser"
   INDEX_NAME = "products-elser-search"
   ```

2. Run the main workshop scripts in `part1_smart_search/` and `part2_conversational_ai/`

## Support

For OpenAI-specific issues:
- OpenAI Documentation: https://platform.openai.com/docs
- OpenAI Help Center: https://help.openai.com/

For the main ELSER workshop:
- See [ELSER_SETUP.md](../../ELSER_SETUP.md)
- See [README.md](../../README.md)
