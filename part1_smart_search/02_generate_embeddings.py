#!/usr/bin/env python3
"""
Part 1 - Step 2: Generate Embeddings and Index Data

This script:
1. Loads sample documents from JSON file
2. Generates embeddings using OpenAI API
3. Indexes documents with embeddings into Elasticsearch

Embeddings are generated for the product name + description.
"""

import sys
import os
import json
import time
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from openai import OpenAI
from tqdm import tqdm
import config

def load_documents() -> List[Dict]:
    """Load sample documents from JSON file."""
    print(f"Loading documents from {config.SAMPLE_DATA_PATH}...")

    with open(config.SAMPLE_DATA_PATH, 'r') as f:
        documents = json.load(f)

    print(f"✓ Loaded {len(documents)} documents\n")
    return documents

def generate_embedding(client: OpenAI, text: str) -> List[float]:
    """Generate embedding for a single text using OpenAI API."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def generate_embeddings_batch(client: OpenAI, texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts in a single API call."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

def prepare_text_for_embedding(doc: Dict) -> str:
    """Combine relevant fields into text for embedding generation."""
    # Combine name and description for richer semantic understanding
    parts = [doc['name'], doc['description']]

    # Add category
    parts.append(f"Category: {doc['category']}")

    # Add key features if available
    if 'features' in doc and doc['features']:
        parts.append("Features: " + ", ".join(doc['features'][:5]))  # Limit to top 5

    return " | ".join(parts)

def index_documents_with_embeddings(es: Elasticsearch, client: OpenAI, documents: List[Dict]):
    """Generate embeddings and index documents into Elasticsearch."""

    print(f"Generating embeddings for {len(documents)} documents...")
    print(f"Model: {config.EMBEDDING_MODEL}")
    print(f"Batch size: {config.EMBEDDING_BATCH_SIZE}\n")

    # Prepare texts for embedding
    texts = [prepare_text_for_embedding(doc) for doc in documents]

    # Generate embeddings in batches
    all_embeddings = []
    total_batches = (len(texts) + config.EMBEDDING_BATCH_SIZE - 1) // config.EMBEDDING_BATCH_SIZE

    for i in tqdm(range(0, len(texts), config.EMBEDDING_BATCH_SIZE), desc="Generating embeddings"):
        batch_texts = texts[i:i + config.EMBEDDING_BATCH_SIZE]

        # Retry logic for API calls
        for attempt in range(config.MAX_RETRIES):
            try:
                batch_embeddings = generate_embeddings_batch(client, batch_texts)
                all_embeddings.extend(batch_embeddings)
                break
            except Exception as e:
                if attempt < config.MAX_RETRIES - 1:
                    print(f"\nRetrying after error: {str(e)}")
                    time.sleep(config.RETRY_DELAY * (attempt + 1))
                else:
                    raise

    print(f"\n✓ Generated {len(all_embeddings)} embeddings")

    # Prepare documents for bulk indexing
    print("\nIndexing documents into Elasticsearch...")
    actions = []

    for doc, embedding in zip(documents, all_embeddings):
        # Add embedding to document
        doc_with_embedding = doc.copy()
        doc_with_embedding['embedding_vector'] = embedding

        action = {
            "_index": config.INDEX_NAME,
            "_id": doc['id'],
            "_source": doc_with_embedding
        }
        actions.append(action)

    # Bulk index
    success, failed = bulk(es, actions, stats_only=True)

    print(f"✓ Indexed {success} documents")
    if failed:
        print(f"⚠ Failed to index {failed} documents")

    # Verify indexing
    print("\nVerifying index...")
    es.indices.refresh(index=config.INDEX_NAME)
    count = es.count(index=config.INDEX_NAME)['count']
    print(f"✓ Total documents in index: {count}")

    # Calculate approximate cost
    if config.TRACK_COSTS:
        total_tokens = sum(len(text.split()) * 1.3 for text in texts)  # Rough estimate
        cost_per_million = config.COST_PER_1M_EMBEDDING_TOKENS.get(config.EMBEDDING_MODEL, 0)
        estimated_cost = (total_tokens / 1_000_000) * cost_per_million
        print(f"\nEstimated embedding cost: ${estimated_cost:.4f}")

def main():
    """Main function."""

    # Load documents
    documents = load_documents()

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

    if not es.ping():
        print("ERROR: Could not connect to Elasticsearch")
        sys.exit(1)

    print("✓ Connected to Elasticsearch\n")

    # Check if index exists
    if not es.indices.exists(index=config.INDEX_NAME):
        print(f"ERROR: Index '{config.INDEX_NAME}' does not exist")
        print("Run 01_setup_index.py first to create the index")
        sys.exit(1)

    # Initialize OpenAI client
    print(f"Initializing OpenAI client...")
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    print("✓ OpenAI client ready\n")

    # Index documents with embeddings
    index_documents_with_embeddings(es, client, documents)

    print("\n✓ Setup complete!")
    print("\nNext steps:")
    print("  Run 03_keyword_search.py to try BM25 keyword search")
    print("  Run 04_semantic_search.py to try vector similarity search")
    print("  Run 05_hybrid_search.py to try combined hybrid search")

    es.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
