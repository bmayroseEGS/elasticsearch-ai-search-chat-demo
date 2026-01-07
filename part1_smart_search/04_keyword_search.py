#!/usr/bin/env python3
"""
Part 1 - Step 4: Traditional Keyword Search (BM25)

This script demonstrates traditional keyword search using Elasticsearch's BM25 algorithm.
BM25 matches exact words and phrases - great for specific terms!

Try queries like:
- "Dell XPS" (exact model match)
- "SSD storage" (specific feature)
- "gaming laptop" (specific product type)

Compare with semantic search to see the difference!
"""

import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import config

console = Console()

def connect_to_elasticsearch():
    """Connect to Elasticsearch."""
    if hasattr(config, 'ELASTICSEARCH_API_KEY') and config.ELASTICSEARCH_API_KEY:
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
        console.print("[red]ERROR: Could not connect to Elasticsearch[/red]")
        sys.exit(1)

    return es

def keyword_search(es, query_text, size=5):
    """Perform keyword search using BM25."""

    search_query = {
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["name^3", "description^2", "features", "category"],
                "type": "best_fields"
            }
        },
        "size": size,
        "_source": ["name", "category", "price", "description"]
    }

    try:
        response = es.search(index=config.INDEX_NAME, body=search_query)
        return response
    except Exception as e:
        console.print(f"[red]ERROR during search: {e}[/red]")
        return None

def display_results(query, response):
    """Display search results in a formatted table."""
    if not response or 'hits' not in response:
        console.print("[yellow]No results found[/yellow]")
        return

    hits = response['hits']['hits']
    total = response['hits']['total']['value']

    # Show query
    console.print(Panel(f"[bold cyan]Query:[/bold cyan] {query}", title="Keyword Search (BM25)"))
    console.print(f"\nFound {total} results\n")

    # Create results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Product", style="cyan", width=30)
    table.add_column("Category", style="green", width=15)
    table.add_column("Price", justify="right", style="yellow", width=10)
    table.add_column("Description", width=50)

    for i, hit in enumerate(hits, 1):
        source = hit['_source']
        score = hit['_score']

        table.add_row(
            str(i),
            f"{score:.2f}",
            source.get('name', 'N/A')[:30],
            source.get('category', 'N/A')[:15],
            f"${source.get('price', 0):.2f}",
            source.get('description', 'N/A')[:50] + "..."
        )

    console.print(table)
    console.print()

def main():
    """Main search function."""
    if len(sys.argv) < 2:
        console.print("\n[bold]Usage:[/bold] python 04_keyword_search.py \"your search query\"")
        console.print("\n[bold]Example queries:[/bold]")
        console.print("  python 04_keyword_search.py \"Dell XPS\"")
        console.print("  python 04_keyword_search.py \"SSD storage\"")
        console.print("  python 04_keyword_search.py \"gaming laptop\"")
        console.print("  python 04_keyword_search.py \"USB-C monitor\"")
        console.print()
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    console.print("\n[bold]Part 1 - Step 4: Keyword Search (BM25)[/bold]\n")

    try:
        # Connect
        console.print(f"Connecting to Elasticsearch at {config.ELASTICSEARCH_URL}...")
        es = connect_to_elasticsearch()
        console.print("[green]✓ Connected[/green]\n")

        # Check if index exists
        if not es.indices.exists(index=config.INDEX_NAME):
            console.print(f"[red]ERROR: Index '{config.INDEX_NAME}' does not exist[/red]")
            console.print("Run 01_setup_index.py and 02_ingest_data.py first\n")
            sys.exit(1)

        # Perform search
        response = keyword_search(es, query, size=10)

        # Display results
        display_results(query, response)

        console.print("[dim]💡 Tip: Keyword search is great for exact terms![/dim]")
        console.print("[dim]   Try the same query with 03_semantic_search.py to compare[/dim]\n")

        es.close()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Search interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]ERROR: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
