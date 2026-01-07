#!/usr/bin/env python3
"""
Part 1 - Step 1: Set Up ELSER and Create Index

This script performs the complete ELSER setup:
1. Creates ELSER inference endpoint (downloads model if needed)
2. Deploys the ELSER model
3. Creates an index configured for ELSER sparse vectors
4. Creates an ingest pipeline for automatic embedding generation

ELSER is Elasticsearch's built-in semantic search model - no API keys needed!

Requirements:
- Elasticsearch 8.8+
- At least 4GB RAM for ML nodes
"""

import sys
import os
import time

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
import config

def connect_to_elasticsearch():
    """Connect to Elasticsearch and verify connection."""
    print(f"Connecting to Elasticsearch at {config.ELASTICSEARCH_URL}...")

    if hasattr(config, 'ELASTICSEARCH_API_KEY') and config.ELASTICSEARCH_API_KEY:
        es = Elasticsearch(
            config.ELASTICSEARCH_URL,
            api_key=config.ELASTICSEARCH_API_KEY,
            verify_certs=config.ELASTICSEARCH_VERIFY_CERTS,
            request_timeout=60
        )
    else:
        es = Elasticsearch(
            config.ELASTICSEARCH_URL,
            basic_auth=(config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD),
            verify_certs=config.ELASTICSEARCH_VERIFY_CERTS,
            request_timeout=60
        )

    if not es.ping():
        print("ERROR: Could not connect to Elasticsearch")
        sys.exit(1)

    print("✓ Connected to Elasticsearch")
    print(f"Cluster: {es.info()['cluster_name']}")
    print(f"Version: {es.info()['version']['number']}\n")

    return es

def create_elser_inference_endpoint(es):
    """Create ELSER inference endpoint (auto-downloads model)."""
    print(f"Creating ELSER inference endpoint: '{config.ELSER_INFERENCE_ID}'...")

    # Check if inference endpoint already exists
    try:
        es.inference.get(inference_id=config.ELSER_INFERENCE_ID)
        print(f"✓ Inference endpoint already exists\n")
        return True
    except:
        pass  # Endpoint doesn't exist, create it

    # Create inference endpoint configuration
    inference_config = {
        "service": "elasticsearch",
        "service_settings": {
            "adaptive_allocations": {
                "enabled": True,
                "min_number_of_allocations": 1,
                "max_number_of_allocations": 4
            },
            "num_threads": 1,
            "model_id": config.ELSER_MODEL_ID
        }
    }

    try:
        es.inference.put(
            task_type="sparse_embedding",
            inference_id=config.ELSER_INFERENCE_ID,
            body=inference_config
        )
        print("✓ Inference endpoint created")
        print("  Model will be downloaded and deployed automatically")
        print("  This may take 2-5 minutes...\n")
        return True
    except Exception as e:
        print(f"ERROR creating inference endpoint: {e}")
        return False

def wait_for_elser_ready(es, max_wait_seconds=300):
    """Wait for ELSER model to be fully deployed."""
    print("Waiting for ELSER model to be ready...")

    start_time = time.time()
    check_interval = 10

    while time.time() - start_time < max_wait_seconds:
        try:
            stats = es.ml.get_trained_models_stats(model_id=config.ELSER_MODEL_ID)

            if stats['trained_model_stats']:
                model_stats = stats['trained_model_stats'][0]
                deployment_stats = model_stats.get('deployment_stats', {})

                if deployment_stats:
                    state = deployment_stats.get('state', 'unknown')
                    allocation_status = deployment_stats.get('allocation_status', {})
                    target_allocations = allocation_status.get('target_allocation_count', 0)
                    current_allocations = allocation_status.get('allocation_count', 0)

                    elapsed = int(time.time() - start_time)
                    print(f"  [{elapsed}s] State: {state} | Allocations: {current_allocations}/{target_allocations}")

                    if state == "started" and current_allocations >= target_allocations and target_allocations > 0:
                        print("\n✓ ELSER model is ready!\n")
                        return True

            time.sleep(check_interval)

        except Exception as e:
            time.sleep(check_interval)

    print("\nWARNING: Timeout waiting for ELSER")
    return False

def create_index(es):
    """Create index configured for ELSER."""
    print(f"Creating index: '{config.INDEX_NAME}'...")

    # Delete index if it exists
    if es.indices.exists(index=config.INDEX_NAME):
        print(f"  Index already exists, deleting...")
        es.indices.delete(index=config.INDEX_NAME)

    # Define index with ELSER fields
    index_config = {
        "settings": {
            "number_of_shards": config.NUMBER_OF_SHARDS,
            "number_of_replicas": config.NUMBER_OF_REPLICAS
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "description": {"type": "text"},
                "specifications": {"type": "object", "enabled": True},
                "features": {"type": "text"},
                "reviews": {
                    "properties": {
                        "rating": {"type": "float"},
                        "count": {"type": "integer"},
                        "summary": {"type": "text"}
                    }
                },
                # Combined text for ELSER
                "elser_text": {"type": "text"},
                # ELSER sparse vector field
                "elser_embedding": {"type": "sparse_vector"}
            }
        }
    }

    es.indices.create(index=config.INDEX_NAME, body=index_config)
    print("✓ Index created successfully\n")

def create_ingest_pipeline(es):
    """Create ingest pipeline for ELSER."""
    print(f"Creating ingest pipeline: '{config.ELSER_PIPELINE_ID}'...")

    pipeline_config = {
        "description": "Ingest pipeline to generate ELSER embeddings",
        "processors": [
            {
                "inference": {
                    "model_id": config.ELSER_MODEL_ID,
                    "input_output": {
                        "input_field": "elser_text",
                        "output_field": "elser_embedding"
                    }
                }
            }
        ]
    }

    try:
        es.ingest.put_pipeline(id=config.ELSER_PIPELINE_ID, body=pipeline_config)
        print(f"✓ Ingest pipeline created\n")
        return True
    except Exception as e:
        print(f"ERROR creating pipeline: {e}\n")
        return False

def main():
    """Main setup function."""
    print("=" * 70)
    print("Part 1 - Step 1: ELSER Setup and Index Creation")
    print("=" * 70)
    print()

    try:
        # Connect
        es = connect_to_elasticsearch()

        # Create ELSER inference endpoint
        if not create_elser_inference_endpoint(es):
            sys.exit(1)

        # Wait for ELSER to be ready
        if not wait_for_elser_ready(es):
            print("WARNING: ELSER may still be deploying")
            print("You can proceed, but ingestion may be slow\n")

        # Create index
        create_index(es)

        # Create ingest pipeline
        create_ingest_pipeline(es)

        print("=" * 70)
        print("✓ Setup Complete!")
        print("=" * 70)
        print("\nNext step: Run 02_ingest_data.py to load sample data")
        print()

        es.close()

    except KeyboardInterrupt:
        print("\n\nSetup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
