#!/usr/bin/env python3
"""
Part 1 - Step 4: Semantic Search (Vector Similarity)

Semantic search using vector embeddings and cosine similarity.
Good for: Natural language queries, conceptual matching, understanding intent

Usage: python 04_semantic_search.py "your search query"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from openai import OpenAI
import config
from rich import print as rprint
from rich.console import Console
from rich.table import Table

def generate_query_embedding(client: OpenAI, query: str) -> list:
    """Generate embedding for search query."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=query
    )
    return response.data[0].embedding

def semantic_search(es: Elasticsearch, query_vector: list, size: int = 5) -> dict:
    """
    Perform semantic search using vector similarity.

    Args:
        es: Elasticsearch client
        query_vector: Query embedding vector
        size: Number of results to return

    Returns:
        Search results dictionary
    """

    search_query = {
        "knn": {
            "field": "embedding_vector",
            "query_vector": query_vector,
            "k": size,
            "num_candidates": config.KNN_NUM_CANDIDATES
        },
        "_source": True
    }

    results = es.search(index=config.INDEX_NAME, body=search_query)
    return results

def display_results(results: dict, query: str):
    """Display search results in a formatted table."""

    console = Console()

    console.print(f"\n[bold cyan]Semantic Search Results (Vector Similarity)[/bold cyan]")
    console.print(f"Query: [yellow]\"{query}\"[/yellow]")
    console.print(f"Total hits: {results['hits']['total']['value']}\n")

    if not results['hits']['hits']:
        console.print("[red]No results found[/red]")
        return

    # Create results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", width=6)
    table.add_column("Similarity", width=10)
    table.add_column("Product", width=35)
    table.add_column("Category", width=12)
    table.add_column("Price", width=10)
    table.add_column("Snippet", width=50)

    for idx, hit in enumerate(results['hits']['hits'], 1):
        source = hit['_source']
        score = hit['_score']

        # Create snippet from description
        description = source.get('description', '')
        snippet = description[:100] + "..." if len(description) > 100 else description

        table.add_row(
            str(idx),
            f"{score:.4f}",
            source.get('name', 'N/A'),
            source.get('category', 'N/A'),
            f"${source.get('price', 0):,.2f}",
            snippet
        )

    console.print(table)

    # Show detailed view of top result
    console.print("\n[bold]Top Result Details:[/bold]")
    top_hit = results['hits']['hits'][0]['_source']

    console.print(f"  Name: [cyan]{top_hit.get('name')}[/cyan]")
    console.print(f"  Category: {top_hit.get('category')}")
    console.print(f"  Price: ${top_hit.get('price'):,.2f}")
    console.print(f"  Description: {top_hit.get('description')}")

    if 'reviews' in top_hit:
        reviews = top_hit['reviews']
        console.print(f"  Rating: ⭐ {reviews.get('rating')}/5.0 ({reviews.get('count')} reviews)")

    # Show semantic matching explanation
    console.print("\n[bold]Why semantic search is powerful:[/bold]")
    console.print("  • Understands [green]intent[/green] and [green]meaning[/green], not just keywords")
    console.print("  • Finds conceptually similar products even without exact word matches")
    console.print("  • Works great for natural language queries")

def main():
    """Main function."""

    if len(sys.argv) < 2:
        print("Usage: python 04_semantic_search.py \"your search query\"")
        print("\nExample queries to try:")
        print("  python 04_semantic_search.py \"portable computer for programming\"")
        print("  python 04_semantic_search.py \"affordable machine for gaming\"")
        print("  python 04_semantic_search.py \"display for creative work\"")
        print("  python 04_semantic_search.py \"productivity mouse\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # Connect to Elasticsearch
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

    # Check if index exists
    if not es.indices.exists(index=config.INDEX_NAME):
        print(f"ERROR: Index '{config.INDEX_NAME}' does not exist")
        print("Run 01_setup_index.py and 02_generate_embeddings.py first")
        sys.exit(1)

    # Initialize OpenAI client
    print(f"Generating query embedding...")
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    try:
        # Generate query embedding
        query_vector = generate_query_embedding(client, query)
        print(f"✓ Query embedding generated ({len(query_vector)} dimensions)\n")

        # Perform search
        results = semantic_search(es, query_vector, size=config.DEFAULT_SEARCH_SIZE)
        display_results(results, query)

    except Exception as e:
        print(f"ERROR during search: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        es.close()

if __name__ == "__main__":
    main()
