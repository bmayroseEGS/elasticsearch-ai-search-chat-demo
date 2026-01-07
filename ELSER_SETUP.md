# ELSER Setup Guide

This guide explains how to set up and use ELSER (Elastic Learned Sparse EncodeR) for semantic search in your Elasticsearch deployment.

## What is ELSER?

ELSER is Elasticsearch's built-in semantic search model that provides:

- **No API Keys Required** - Runs entirely within Elasticsearch
- **Semantic Understanding** - Understands meaning and intent, not just keywords
- **Optimized for English** - Specifically trained for English language text
- **Sparse Vectors** - Uses token expansion instead of dense embeddings
- **Lower Latency** - No external API calls needed

## Prerequisites

Before setting up ELSER, ensure you have:

1. **Elasticsearch 8.8+** (ELSER v2 requires 8.8 or higher)
2. **At least 4GB RAM** for ML nodes
3. **Python environment** with elasticsearch package installed
4. **config.py** file created (copy from config.example.py)

## Quick Start

### 1. Set Up ELSER

Run the setup script to download, deploy, and configure ELSER:

```bash
cd /Users/bmelasticendgame/dev/elasticsearch-ai-search-chat-demo
python scripts/setup-elser.py
```

**What this script does:**
- Creates an ELSER inference endpoint (automatically downloads the model)
- Deploys the ELSER model with autoscaling (1-4 allocations)
- Creates an index configured for ELSER sparse vectors
- Sets up an ingest pipeline for automatic embedding generation
- Verifies the deployment is ready

**Expected time:** 2-5 minutes (first run includes model download)

### 2. Ingest Sample Data

Load the sample product catalog with ELSER embeddings:

```bash
python scripts/ingest-with-elser.py
```

**What this script does:**
- Loads sample products from `data/sample_documents.json`
- Combines product fields into a searchable text representation
- Uses the ELSER ingest pipeline to generate embeddings automatically
- Bulk indexes all documents
- Verifies embeddings were created successfully

**Expected time:** 2-3 minutes for 500 documents

### 3. Search with ELSER

Try semantic search using natural language queries:

```bash
# Interactive mode
python scripts/search-with-elser.py

# Search from command line
python scripts/search-with-elser.py laptop for programming

# Run sample queries
python scripts/search-with-elser.py --samples
```

## Understanding ELSER vs. Dense Vectors

### ELSER (Sparse Vectors)
- **How it works:** Expands query/document into weighted tokens
- **Vector type:** Sparse (only non-zero values stored)
- **Best for:** Natural language text, English content
- **Advantages:**
  - No external dependencies
  - Explainable results (can see which tokens matched)
  - Lower operational complexity
- **Limitations:**
  - English language only
  - Requires ML node resources

### Dense Vectors (OpenAI Embeddings)
- **How it works:** Creates fixed-size dense embedding vectors
- **Vector type:** Dense (1536 or 3072 dimensions, all values stored)
- **Best for:** Multi-language, cross-modal search
- **Advantages:**
  - Supports many languages
  - Can embed images, code, etc.
  - Pre-trained on diverse content
- **Limitations:**
  - Requires API key and external service
  - Higher latency (API calls)
  - Ongoing API costs

## Architecture Overview

### ELSER Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Ingest Pipeline                         │
│  ┌────────────┐        ┌──────────────┐      ┌──────────┐  │
│  │  Document  │───────>│ ELSER Model  │─────>│  Sparse  │  │
│  │ (text)     │        │ (.elser_v2)  │      │  Vector  │  │
│  └────────────┘        └──────────────┘      └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Elasticsearch Index │
                    │  products-elser-search│
                    └───────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      Search Query                            │
│  ┌────────────┐        ┌──────────────┐      ┌──────────┐  │
│  │  Query     │───────>│ ELSER Model  │─────>│ Matches  │  │
│  │ (text)     │        │ (inference)  │      │ Ranked   │  │
│  └────────────┘        └──────────────┘      └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Index Structure

The ELSER index includes:

```json
{
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "name": {"type": "text"},
      "description": {"type": "text"},
      "category": {"type": "keyword"},
      "price": {"type": "float"},
      "elser_text": {"type": "text"},           // Combined text for ELSER
      "elser_embedding": {"type": "sparse_vector"}  // ELSER-generated
    }
  }
}
```

## Manual Operations

### Check ELSER Status

```bash
# Via Kibana Dev Tools
GET _ml/trained_models/.elser_model_2/_stats

# Expected response shows deployment state and allocations
```

### Search Query Structure

```json
POST products-elser-search/_search
{
  "query": {
    "sparse_vector": {
      "field": "elser_embedding",
      "inference_id": "elser-inference-endpoint",
      "query": "laptop for programming and video editing"
    }
  },
  "size": 5
}
```

### Index a Single Document

```bash
POST products-elser-search/_doc?pipeline=elser-ingest-pipeline
{
  "name": "New Laptop",
  "description": "High performance laptop",
  "elser_text": "New Laptop | High performance laptop for development"
}
```

## Sample Queries to Try

Here are some example queries that showcase ELSER's semantic understanding:

### 1. Intent-Based Queries
```
"laptop for programming and video editing"
"monitor for home office work"
"keyboard for long typing sessions"
```

### 2. Conceptual Queries
```
"affordable portable computer"
"high quality display for creative work"
"ergonomic input devices"
```

### 3. Use-Case Queries
```
"equipment for remote work setup"
"gaming setup under $2000"
"storage solution for large files"
```

### 4. Feature-Based Queries
```
"wireless devices with long battery life"
"high resolution display with accurate colors"
"fast processor for multitasking"
```

## Performance Tuning

### Adjusting Allocations

Modify autoscaling settings for your workload:

```bash
POST _ml/trained_models/.elser_model_2/deployment/_update
{
  "adaptive_allocations": {
    "enabled": true,
    "min_number_of_allocations": 1,
    "max_number_of_allocations": 8
  }
}
```

### Optimizing for Ingest vs. Search

**For High Ingest Volume:**
- Increase `max_number_of_allocations`
- Use larger `chunk_size` in bulk operations
- Consider separate deployment for ingest

**For Low Latency Search:**
- Keep allocations warm (don't scale to zero)
- Use dedicated ML nodes
- Enable request caching

## Troubleshooting

### Model Download Fails

**Issue:** Timeout or connection error during model download

**Solution:**
```bash
# Increase timeout and retry
PUT _inference/sparse_embedding/elser-inference-endpoint
{
  "service": "elasticsearch",
  "service_settings": {
    "model_id": ".elser_model_2",
    "num_threads": 1
  }
}

# Check download status
GET _ml/trained_models/.elser_model_2
```

### Deployment Not Starting

**Issue:** Model deployment stuck in "starting" state

**Solution:**
```bash
# Check ML node resources
GET _cat/ml/nodes?v&h=id,name,heap.current,heap.max

# Stop and restart deployment
POST _ml/trained_models/.elser_model_2/deployment/_stop
POST _ml/trained_models/.elser_model_2/deployment/_start?wait_for=started
```

### Search Returns No Results

**Issue:** Queries return empty results

**Solution:**
1. Verify embeddings were created:
   ```bash
   GET products-elser-search/_search
   {
     "size": 1,
     "_source": ["elser_embedding"]
   }
   ```

2. Check if `elser_embedding` field exists and has values

3. Verify inference endpoint:
   ```bash
   GET _inference/sparse_embedding/elser-inference-endpoint
   ```

### Memory Issues

**Issue:** Cluster running out of memory

**Solution:**
- Reduce `max_number_of_allocations`
- Use dedicated ML nodes with more RAM
- Process documents in smaller batches

## Resource Requirements

### Minimum Resources

- **Memory:** 4GB per allocation
- **CPU:** 2 cores recommended
- **Storage:** ~1GB for ELSER model

### Recommended for Production

- **Memory:** 8GB+ per ML node
- **CPU:** 4+ cores
- **ML Nodes:** Dedicated node(s) with ML role
- **Allocations:** 2-4 for high availability

## Monitoring ELSER

### Key Metrics to Watch

```bash
# Deployment statistics
GET _ml/trained_models/.elser_model_2/_stats

# Important fields:
# - deployment_stats.state (should be "started")
# - deployment_stats.allocation_status.allocation_count
# - deployment_stats.inference_count
# - deployment_stats.peak_throughput_per_minute
```

### Health Checks

```bash
# Check if model is deployed and ready
GET _ml/trained_models/.elser_model_2/_stats
{
  "filter": {
    "term": {
      "deployment_stats.state": "started"
    }
  }
}
```

## Comparison with OpenAI Embeddings

| Feature | ELSER | OpenAI Embeddings |
|---------|-------|-------------------|
| **API Key Required** | No | Yes |
| **Cost** | Elasticsearch resources only | $0.02-$0.13 per 1M tokens |
| **Latency** | Low (internal) | Higher (API calls) |
| **Languages** | English only | 100+ languages |
| **Setup Complexity** | Medium | Low |
| **Operational Complexity** | Higher (manage ML nodes) | Lower (managed service) |
| **Explainability** | High (token weights) | Low (dense vector) |
| **Offline Capability** | Yes | No |

## When to Use ELSER

**Choose ELSER when:**
- ✅ Content is primarily English
- ✅ You want to avoid external API dependencies
- ✅ You need explainable search results
- ✅ You prefer lower latency
- ✅ You have sufficient ML node resources

**Choose OpenAI Embeddings when:**
- ✅ Content is multi-language
- ✅ You need cross-modal search (text + images)
- ✅ You want simpler operations (no ML nodes to manage)
- ✅ You're already using OpenAI for other features

## Cost Analysis

### ELSER Costs
- **Infrastructure:** ML node resources (compute + memory)
- **Example:** 1 ML node (4GB RAM) ≈ same cost as general node
- **Scaling:** Linear with allocations

### OpenAI Costs (for comparison)
- **Embeddings:** $0.02/1M tokens (text-embedding-3-small)
- **Example:** 500 products ≈ $0.01-$0.05 one-time
- **Ongoing:** Per query/update

## Next Steps

1. **Try Hybrid Search:** Combine ELSER with keyword search for best results
2. **Customize Ingest:** Modify `elser_text` field construction for your data
3. **Tune Performance:** Adjust allocations based on your load patterns
4. **Monitor Usage:** Track inference counts and latency
5. **Scale Up:** Add more ML nodes as needed

## Additional Resources

- [ELSER Documentation](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)
- [Inference API Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html)
- [Sparse Vector Field Type](https://www.elastic.co/guide/en/elasticsearch/reference/current/sparse-vector.html)
- [ML Node Configuration](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-node.html#ml-node)

## Support

For issues specific to this setup:
1. Check the troubleshooting section above
2. Review Elasticsearch logs for ML nodes
3. Verify ML node resources are sufficient
4. Check ELSER model deployment status

For general ELSER questions:
- Visit: https://discuss.elastic.co/c/elastic-stack/machine-learning/30
- Documentation: https://www.elastic.co/guide/en/machine-learning/current/index.html
