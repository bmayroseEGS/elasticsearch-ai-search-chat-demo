#!/usr/bin/env python3
"""
Part 1 - Step 1: Set Up Index with Vector Mappings

This script creates an Elasticsearch index configured for hybrid search:
- Text fields for keyword (BM25) search
- Dense vector field for semantic search
- Scalar quantization for 95% memory reduction

Run this first to create the index structure.
"""

import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
import config

def create_index():
    """Create index with mappings for hybrid search."""

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

    # Check connection
    if not es.ping():
        print("ERROR: Could not connect to Elasticsearch")
        sys.exit(1)

    print("✓ Connected to Elasticsearch")
    print(f"Cluster: {es.info()['cluster_name']}")
    print(f"Version: {es.info()['version']['number']}\n")

    # Delete index if it exists
    if es.indices.exists(index=config.INDEX_NAME):
        print(f"Index '{config.INDEX_NAME}' already exists. Deleting...")
        es.indices.delete(index=config.INDEX_NAME)
        print("✓ Deleted existing index\n")

    # Define index settings and mappings
    index_config = {
        "settings": {
            "number_of_shards": config.NUMBER_OF_SHARDS,
            "number_of_replicas": config.NUMBER_OF_REPLICAS,
            "index": {
                "codec": "best_compression"  # Optimize storage
            }
        },
        "mappings": {
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "category": {
                    "type": "keyword"
                },
                "price": {
                    "type": "float"
                },
                "description": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "specifications": {
                    "type": "object",
                    "enabled": True
                },
                "features": {
                    "type": "text"
                },
                "reviews": {
                    "properties": {
                        "rating": {
                            "type": "float"
                        },
                        "count": {
                            "type": "integer"
                        },
                        "summary": {
                            "type": "text"
                        }
                    }
                },
                "embedding_vector": {
                    "type": "dense_vector",
                    "dims": config.VECTOR_DIMENSIONS,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }

    # Add quantization if enabled
    if config.USE_QUANTIZATION:
        index_config["mappings"]["properties"]["embedding_vector"]["index_options"] = {
            "type": "int8_hnsw",  # Scalar quantization
            "m": 16,  # Number of connections per layer
            "ef_construction": 100  # Size of candidate list during index build
        }
        print("✓ Scalar quantization enabled (int8_hnsw)")
        print("  Memory reduction: ~95%")
        print("  Accuracy impact: ~1-2%\n")

    # Create the index
    print(f"Creating index '{config.INDEX_NAME}'...")
    es.indices.create(index=config.INDEX_NAME, body=index_config)
    print("✓ Index created successfully\n")

    # Display configuration
    print("Index Configuration:")
    print(f"  Name: {config.INDEX_NAME}")
    print(f"  Shards: {config.NUMBER_OF_SHARDS}")
    print(f"  Replicas: {config.NUMBER_OF_REPLICAS}")
    print(f"  Vector dimensions: {config.VECTOR_DIMENSIONS}")
    print(f"  Similarity function: cosine")
    print(f"  Compression: best_compression\n")

    # Get and display mapping
    mapping = es.indices.get_mapping(index=config.INDEX_NAME)
    print("✓ Index ready for data ingestion")
    print("\nNext step: Run 02_generate_embeddings.py to index data")

    es.close()

if __name__ == "__main__":
    try:
        create_index()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
