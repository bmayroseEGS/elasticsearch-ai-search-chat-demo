#!/usr/bin/env python3
"""
Part 1 - Step 3: Keyword Search (BM25)

Traditional keyword search using Elasticsearch's BM25 algorithm.
Good for: Exact matches, specific model numbers, brand names

Usage: python 03_keyword_search.py "your search query"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
import config
from rich import print as rprint
from rich.console import Console
from rich.table import Table

def keyword_search(es: Elasticsearch, query: str, size: int = 5) -> dict:
    """
    Perform keyword (BM25) search.

    Args:
        es: Elasticsearch client
        query: Search query string
        size: Number of results to return

    Returns:
        Search results dictionary
    """

    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "name^3",          # Boost name field 3x
                    "description^2",   # Boost description 2x
                    "category",
                    "features",
                    "reviews.summary"
                ],
                "type": "best_fields",
                "fuzziness": "AUTO"  # Allow typos
            }
        },
        "size": size
    }

    results = es.search(index=config.INDEX_NAME, body=search_query)
    return results

def display_results(results: dict, query: str):
    """Display search results in a formatted table."""

    console = Console()

    console.print(f"\n[bold cyan]Keyword Search Results (BM25)[/bold cyan]")
    console.print(f"Query: [yellow]\"{query}\"[/yellow]")
    console.print(f"Total hits: {results['hits']['total']['value']}\n")

    if not results['hits']['hits']:
        console.print("[red]No results found[/red]")
        return

    # Create results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", width=6)
    table.add_column("Score", width=8)
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
            f"{score:.2f}",
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

def main():
    """Main function."""

    if len(sys.argv) < 2:
        print("Usage: python 03_keyword_search.py \"your search query\"")
        print("\nExample queries:")
        print("  python 03_keyword_search.py \"gaming laptop\"")
        print("  python 03_keyword_search.py \"MacBook Pro\"")
        print("  python 03_keyword_search.py \"ultrawide monitor\"")
        print("  python 03_keyword_search.py \"mechanical keyboard\"")
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

    # Perform search
    try:
        results = keyword_search(es, query, size=config.DEFAULT_SEARCH_SIZE)
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
