# ELSER Scripts Quick Reference

This directory contains scripts for setting up and using ELSER (Elastic Learned Sparse EncodeR) for semantic search.

## Quick Start

```bash
# 1. Setup ELSER (downloads model, creates index, configures pipeline)
python scripts/setup-elser.py

# 2. Ingest sample data with ELSER embeddings
python scripts/ingest-with-elser.py

# 3. Search using ELSER
python scripts/search-with-elser.py
```

## Script Overview

### setup-elser.py
**Purpose:** Complete ELSER setup automation

**What it does:**
- Creates ELSER inference endpoint
- Downloads .elser_model_2 automatically
- Deploys model with autoscaling (1-4 allocations)
- Creates index: `products-elser-search`
- Creates ingest pipeline: `elser-ingest-pipeline`
- Verifies deployment is ready

**Runtime:** 2-5 minutes (first run)

**Requirements:**
- Elasticsearch 8.8+
- 4GB+ RAM for ML nodes

---

### ingest-with-elser.py
**Purpose:** Load sample data with ELSER embeddings

**What it does:**
- Loads products from `data/sample_documents.json`
- Combines fields into `elser_text` for semantic search
- Uses ingest pipeline to generate embeddings automatically
- Bulk indexes all documents
- Verifies embeddings were created

**Runtime:** 2-3 minutes for 500 products

**Output:** Documents with `elser_embedding` sparse vectors

---

### search-with-elser.py
**Purpose:** Search using ELSER semantic search

**Usage:**
```bash
# Interactive mode - type queries interactively
python scripts/search-with-elser.py

# Command line query
python scripts/search-with-elser.py laptop for programming

# Run predefined sample queries
python scripts/search-with-elser.py --samples
```

**Features:**
- Natural language queries
- Semantic understanding (not just keywords)
- Interactive or command-line modes
- Sample queries included

---

## Workflow Diagram

```
┌─────────────────────┐
│  setup-elser.py     │  (Run once)
│  • Download model   │
│  • Create index     │
│  • Setup pipeline   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ ingest-with-elser.py│  (Run when loading data)
│  • Load products    │
│  • Generate vectors │
│  • Bulk index       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│search-with-elser.py │  (Run anytime to search)
│  • Enter queries    │
│  • Get results      │
│  • See rankings     │
└─────────────────────┘
```

## Configuration

All scripts use settings from `config.py`:

```python
# Elasticsearch connection
ELASTICSEARCH_URL = "http://localhost:9200"
ELASTICSEARCH_USERNAME = "elastic"
ELASTICSEARCH_PASSWORD = "elastic"

# Sample data location
SAMPLE_DATA_PATH = "data/sample_documents.json"
```

## Troubleshooting

### Script fails with "Index does not exist"
**Solution:** Run scripts in order (setup → ingest → search)

### "Could not connect to Elasticsearch"
**Solution:**
- Verify Elasticsearch is running: `curl http://localhost:9200`
- Check config.py has correct URL and credentials

### "Model deployment timeout"
**Solution:**
- Model download may take longer (especially first time)
- Check ML node resources: `GET _cat/ml/nodes?v`
- Check model status: `GET _ml/trained_models/.elser_model_2/_stats`

### No search results
**Solution:**
- Verify data was ingested: `GET products-elser-search/_count`
- Check embeddings exist: `GET products-elser-search/_search` and look for `elser_embedding` field
- Verify ELSER is running: `GET _ml/trained_models/.elser_model_2/_stats`

## Sample Queries

Try these in search-with-elser.py:

**Intent-based:**
- "laptop for programming and video editing"
- "monitor for home office work"
- "keyboard for long typing sessions"

**Conceptual:**
- "affordable portable computer"
- "high quality display for creative work"
- "ergonomic input devices"

**Use-case:**
- "equipment for remote work setup"
- "gaming setup under $2000"
- "storage solution for large files"

## Index Structure

The ELSER index (`products-elser-search`) contains:

```json
{
  "id": "product-id",
  "name": "Product Name",
  "category": "Category",
  "price": 999.99,
  "description": "Product description...",
  "specifications": {...},
  "features": [...],
  "elser_text": "Combined text for ELSER",
  "elser_embedding": {
    "token1": 0.85,
    "token2": 0.72,
    ...
  }
}
```

## Performance Tips

**For faster ingestion:**
- Increase allocations in setup-elser.py
- Reduce `chunk_size` in ingest-with-elser.py if getting timeouts

**For better search:**
- Keep model allocations warm (don't let autoscaling go to 0)
- Use dedicated ML nodes in production
- Combine with keyword search for hybrid approach

## Resources

- **Full Guide:** [ELSER_SETUP.md](../ELSER_SETUP.md)
- **Prerequisites:** [PREREQUISITES.md](../PREREQUISITES.md)
- **ELSER Docs:** https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html

## Cost Comparison

### ELSER
- Cost: Elasticsearch ML node resources only
- No per-query costs
- No API keys needed

### OpenAI Embeddings
- Cost: $0.02/1M tokens (text-embedding-3-small)
- Ongoing costs for queries/updates
- Requires API key and external service

For this workshop dataset (500 products):
- **ELSER:** Infrastructure only (~same as running Elasticsearch)
- **OpenAI:** ~$0.01-$0.05 one-time + query costs
