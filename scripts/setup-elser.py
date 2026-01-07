#!/usr/bin/env python3
"""
Setup ELSER (Elastic Learned Sparse EncodeR) for Semantic Search

This script automates the setup of ELSER in Elasticsearch:
1. Creates an ELSER inference endpoint (auto-downloads and deploys the model)
2. Checks deployment status
3. Creates an index configured for ELSER
4. Provides instructions for ingesting data

ELSER is Elasticsearch's built-in semantic search model:
- No external API keys needed
- Runs entirely within Elasticsearch
- Optimized for English text
- Uses sparse vectors (token expansion)

Requirements:
- Elasticsearch 8.8+ (ELSER v2)
- At least 4GB RAM for ML nodes
- Python elasticsearch package
"""

import sys
import os
import time

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
import config

# ELSER configuration
ELSER_MODEL_ID = ".elser_model_2"  # ELSER v2 (latest)
ELSER_INFERENCE_ID = "elser-inference-endpoint"
ELSER_INDEX_NAME = "products-elser-search"

def connect_to_elasticsearch():
    """Connect to Elasticsearch and verify connection."""
    print(f"Connecting to Elasticsearch at {config.ELASTICSEARCH_URL}...")

    if hasattr(config, 'ELASTICSEARCH_API_KEY'):
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

def check_ml_nodes(es):
    """Check if ML nodes are available."""
    print("Checking for ML nodes...")

    try:
        nodes = es.nodes.info()
        ml_nodes = []

        for node_id, node_info in nodes['nodes'].items():
            roles = node_info.get('roles', [])
            if 'ml' in roles:
                ml_nodes.append(node_info['name'])

        if ml_nodes:
            print(f"✓ Found {len(ml_nodes)} ML node(s): {', '.join(ml_nodes)}\n")
            return True
        else:
            print("WARNING: No dedicated ML nodes found.")
            print("ELSER will use general-purpose nodes (may impact performance)\n")
            return True  # Continue anyway

    except Exception as e:
        print(f"Warning: Could not check ML nodes: {e}\n")
        return True

def create_elser_inference_endpoint(es):
    """Create ELSER inference endpoint using the Inference API."""
    print(f"Creating ELSER inference endpoint: '{ELSER_INFERENCE_ID}'...")

    # Check if inference endpoint already exists
    try:
        existing = es.inference.get(inference_id=ELSER_INFERENCE_ID)
        print(f"✓ Inference endpoint '{ELSER_INFERENCE_ID}' already exists")
        print(f"  Model: {existing['model_id']}")
        print(f"  Service: {existing['service']}\n")
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
            "model_id": ELSER_MODEL_ID
        }
    }

    try:
        # Create the inference endpoint
        response = es.inference.put(
            task_type="sparse_embedding",
            inference_id=ELSER_INFERENCE_ID,
            body=inference_config
        )

        print("✓ Inference endpoint created successfully")
        print("  This will automatically download and deploy ELSER model")
        print("  Adaptive allocations enabled (auto-scaling 1-4 allocations)\n")
        return True

    except Exception as e:
        print(f"ERROR creating inference endpoint: {e}")
        print("\nTrying alternative method (manual deployment)...")
        return create_elser_manual(es)

def create_elser_manual(es):
    """Manually download and deploy ELSER model (fallback method)."""
    print(f"\nUsing manual ELSER deployment...")

    try:
        # Check if model exists
        try:
            model_info = es.ml.get_trained_models(model_id=ELSER_MODEL_ID)
            print(f"✓ Model {ELSER_MODEL_ID} already downloaded")
        except:
            # Download the model
            print(f"Downloading {ELSER_MODEL_ID}... (this may take a few minutes)")
            es.ml.put_trained_model(
                model_id=ELSER_MODEL_ID,
                body={
                    "input": {
                        "field_names": ["text_field"]
                    }
                }
            )
            print("✓ Model downloaded successfully")

        # Start deployment
        deployment_id = "elser-deployment"
        try:
            es.ml.start_trained_model_deployment(
                model_id=ELSER_MODEL_ID,
                deployment_id=deployment_id,
                number_of_allocations=1,
                threads_per_allocation=1,
                priority="normal",
                wait_for="started"
            )
            print(f"✓ Model deployment started: {deployment_id}\n")
            return True
        except Exception as deploy_error:
            if "already started" in str(deploy_error).lower():
                print(f"✓ Model already deployed\n")
                return True
            raise deploy_error

    except Exception as e:
        print(f"ERROR with manual deployment: {e}")
        return False

def wait_for_elser_ready(es, max_wait_seconds=300):
    """Wait for ELSER model to be fully deployed and ready."""
    print("Waiting for ELSER model to be ready...")
    print("(This may take 2-5 minutes on first setup)\n")

    start_time = time.time()
    check_interval = 10  # seconds

    while time.time() - start_time < max_wait_seconds:
        try:
            # Check inference endpoint status
            try:
                stats = es.ml.get_trained_models_stats(model_id=ELSER_MODEL_ID)

                if stats['trained_model_stats']:
                    model_stats = stats['trained_model_stats'][0]
                    deployment_stats = model_stats.get('deployment_stats', {})

                    if deployment_stats:
                        state = deployment_stats.get('state', 'unknown')
                        allocation_status = deployment_stats.get('allocation_status', {})
                        target_allocations = allocation_status.get('target_allocation_count', 0)
                        current_allocations = allocation_status.get('allocation_count', 0)

                        elapsed = int(time.time() - start_time)
                        print(f"[{elapsed}s] State: {state} | Allocations: {current_allocations}/{target_allocations}")

                        if state == "started" and current_allocations >= target_allocations and target_allocations > 0:
                            print("\n✓ ELSER model is ready!\n")
                            return True
            except:
                pass

            time.sleep(check_interval)

        except Exception as e:
            print(f"Error checking status: {e}")
            time.sleep(check_interval)

    print(f"\nWARNING: Timeout waiting for ELSER to be ready")
    print("The model may still be deploying. Check status manually:\n")
    print(f"GET _ml/trained_models/{ELSER_MODEL_ID}/_stats")
    return False

def create_elser_index(es):
    """Create an index configured to use ELSER inference."""
    print(f"Creating ELSER index: '{ELSER_INDEX_NAME}'...")

    # Delete index if it exists
    if es.indices.exists(index=ELSER_INDEX_NAME):
        print(f"Index '{ELSER_INDEX_NAME}' already exists. Deleting...")
        es.indices.delete(index=ELSER_INDEX_NAME)
        print("✓ Deleted existing index")

    # Define index with ELSER inference pipeline
    index_config = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
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
                # Combined text field for ELSER
                "elser_text": {"type": "text"},
                # ELSER sparse vector field
                "elser_embedding": {
                    "type": "sparse_vector"
                }
            }
        }
    }

    # Create the index
    es.indices.create(index=ELSER_INDEX_NAME, body=index_config)
    print("✓ Index created successfully\n")

    print("Index Configuration:")
    print(f"  Name: {ELSER_INDEX_NAME}")
    print(f"  Sparse vector field: elser_embedding")
    print(f"  Text field for inference: elser_text\n")

def create_ingest_pipeline(es):
    """Create an ingest pipeline that uses ELSER inference."""
    pipeline_id = "elser-ingest-pipeline"

    print(f"Creating ingest pipeline: '{pipeline_id}'...")

    pipeline_config = {
        "description": "Ingest pipeline to generate ELSER embeddings",
        "processors": [
            {
                "inference": {
                    "model_id": ELSER_MODEL_ID,
                    "input_output": {
                        "input_field": "elser_text",
                        "output_field": "elser_embedding"
                    }
                }
            }
        ]
    }

    try:
        es.ingest.put_pipeline(id=pipeline_id, body=pipeline_config)
        print(f"✓ Ingest pipeline created: {pipeline_id}\n")
        return pipeline_id
    except Exception as e:
        print(f"ERROR creating pipeline: {e}\n")
        return None

def print_usage_instructions(pipeline_id):
    """Print instructions for using ELSER."""
    print("=" * 70)
    print("ELSER Setup Complete!")
    print("=" * 70)
    print("\n📚 Next Steps:\n")

    print("1. Index documents using the ELSER ingest pipeline:")
    print(f"   Run: python scripts/ingest-with-elser.py")
    print()

    print("2. Or manually index via Dev Tools:")
    print(f"""
POST {ELSER_INDEX_NAME}/_doc?pipeline={pipeline_id}
{{
  "name": "Sample Product",
  "description": "Product description here",
  "elser_text": "Product name and full description for ELSER"
}}
""")

    print("\n3. Search using ELSER:")
    print(f"""
POST {ELSER_INDEX_NAME}/_search
{{
  "query": {{
    "sparse_vector": {{
      "field": "elser_embedding",
      "inference_id": "{ELSER_INFERENCE_ID}",
      "query": "your search query here"
    }}
  }}
}}
""")

    print("\n4. Check ELSER status anytime:")
    print(f"   GET _ml/trained_models/{ELSER_MODEL_ID}/_stats")
    print()

    print("=" * 70)
    print("\n💡 Benefits of ELSER:")
    print("  • No external API keys required")
    print("  • Runs entirely within Elasticsearch")
    print("  • Optimized for English language text")
    print("  • Automatic semantic understanding")
    print("  • Lower latency than external APIs")
    print()

def main():
    """Main setup function."""
    print("=" * 70)
    print("ELSER Setup Script")
    print("=" * 70)
    print()

    try:
        # Connect to Elasticsearch
        es = connect_to_elasticsearch()

        # Check for ML nodes
        check_ml_nodes(es)

        # Create ELSER inference endpoint (auto-downloads model)
        if not create_elser_inference_endpoint(es):
            print("\nERROR: Failed to create ELSER endpoint")
            sys.exit(1)

        # Wait for model to be ready
        wait_for_elser_ready(es)

        # Create index for ELSER
        create_elser_index(es)

        # Create ingest pipeline
        pipeline_id = create_ingest_pipeline(es)

        # Print usage instructions
        print_usage_instructions(pipeline_id)

        es.close()

    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
