#!/usr/bin/env python3
"""
Search Using ELSER Semantic Search

This script demonstrates how to perform semantic search using ELSER.
It allows you to enter natural language queries and see relevant results.

ELSER understands semantic meaning, so you can search by:
- Intent ("laptop for programming")
- Concepts ("affordable home office setup")
- Related terms (ELSER handles synonyms automatically)
"""

import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
import config

# ELSER configuration
ELSER_INDEX_NAME = "products-elser-search"
ELSER_INFERENCE_ID = "elser-inference-endpoint"

def connect_to_elasticsearch():
    """Connect to Elasticsearch."""
    if hasattr(config, 'ELASTICSEARCH_API_KEY'):
        es = Elasticsearch(
            config.ELASTICSEARCH_URL,
            api_key=config.ELASTICSEARCH_API_KEY,
            verify_certs=config.ELASTICSEARCH_VERIFY_CERTS,
            request_timeout=30
        )
    else:
        es = Elasticsearch(
            config.ELASTICSEARCH_URL,
            basic_auth=(config.ELASTICSEARCH_USERNAME, config.ELASTICSEARCH_PASSWORD),
            verify_certs=config.ELASTICSEARCH_VERIFY_CERTS,
            request_timeout=30
        )

    if not es.ping():
        print("ERROR: Could not connect to Elasticsearch")
        sys.exit(1)

    return es

def search_with_elser(es, query_text, size=5):
    """Perform semantic search using ELSER."""

    search_query = {
        "query": {
            "sparse_vector": {
                "field": "elser_embedding",
                "inference_id": ELSER_INFERENCE_ID,
                "query": query_text
            }
        },
        "size": size,
        "_source": ["name", "category", "price", "description"]
    }

    try:
        response = es.search(index=ELSER_INDEX_NAME, body=search_query)
        return response
    except Exception as e:
        print(f"ERROR during search: {e}")
        return None

def display_results(response):
    """Display search results in a readable format."""
    if not response or 'hits' not in response:
        print("No results found")
        return

    hits = response['hits']['hits']
    total = response['hits']['total']['value']

    print(f"\nFound {total} results:\n")
    print("=" * 70)

    for i, hit in enumerate(hits, 1):
        source = hit['_source']
        score = hit['_score']

        print(f"\n{i}. {source.get('name', 'Unknown Product')}")
        print(f"   Category: {source.get('category', 'N/A')}")
        print(f"   Price: ${source.get('price', 0):.2f}")
        print(f"   Relevance Score: {score:.2f}")
        print(f"   Description: {source.get('description', 'N/A')[:150]}...")

    print("\n" + "=" * 70)

def interactive_search(es):
    """Interactive search loop."""
    print("\n" + "=" * 70)
    print("ELSER Semantic Search - Interactive Mode")
    print("=" * 70)
    print("\nEnter your search queries (or 'quit' to exit)")
    print("Try natural language like:")
    print("  - 'laptop for programming and video editing'")
    print("  - 'affordable monitor for home office'")
    print("  - 'wireless keyboard with long battery life'\n")

    while True:
        try:
            query = input("\nSearch: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            # Perform search
            print(f"\nSearching for: '{query}'")
            response = search_with_elser(es, query, size=5)

            # Display results
            display_results(response)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"ERROR: {e}")

def run_sample_queries(es):
    """Run predefined sample queries."""
    sample_queries = [
        "laptop for programming",
        "affordable monitor for home office",
        "wireless keyboard with long battery",
        "portable storage with fast speed",
        "gaming computer high performance"
    ]

    print("\n" + "=" * 70)
    print("Running Sample ELSER Queries")
    print("=" * 70)

    for query in sample_queries:
        print(f"\n\n{'='*70}")
        print(f"Query: '{query}'")
        print('='*70)

        response = search_with_elser(es, query, size=3)
        display_results(response)

        input("\nPress Enter to continue to next query...")

def main():
    """Main search function."""
    print("=" * 70)
    print("ELSER Search Script")
    print("=" * 70)
    print(f"\nConnecting to Elasticsearch at {config.ELASTICSEARCH_URL}...")

    try:
        # Connect to Elasticsearch
        es = connect_to_elasticsearch()
        print("✓ Connected to Elasticsearch")

        # Check if index exists
        if not es.indices.exists(index=ELSER_INDEX_NAME):
            print(f"\nERROR: Index '{ELSER_INDEX_NAME}' does not exist")
            print("Run setup-elser.py and ingest-with-elser.py first\n")
            sys.exit(1)

        # Get document count
        stats = es.indices.stats(index=ELSER_INDEX_NAME)
        doc_count = stats['_all']['primaries']['docs']['count']
        print(f"✓ Index contains {doc_count} documents")

        # Check mode
        if len(sys.argv) > 1:
            if sys.argv[1] == '--samples':
                # Run sample queries
                run_sample_queries(es)
            else:
                # Search for command line query
                query = ' '.join(sys.argv[1:])
                print(f"\nSearching for: '{query}'")
                response = search_with_elser(es, query, size=10)
                display_results(response)
        else:
            # Interactive mode
            interactive_search(es)

        es.close()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
