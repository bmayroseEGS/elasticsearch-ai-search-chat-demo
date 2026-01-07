#!/usr/bin/env python3
"""
Part 1 - Step 3: Semantic Search with ELSER

This script demonstrates semantic search using ELSER.
ELSER understands meaning and intent - not just keyword matching!

Try queries like:
- "laptop for programming"
- "affordable monitor for home office"
- "wireless keyboard with long battery"

ELSER automatically handles synonyms, related concepts, and natural language.
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

def semantic_search(es, query_text, size=5):
    """Perform semantic search using ELSER."""

    search_query = {
        "query": {
            "sparse_vector": {
                "field": "elser_embedding",
                "inference_id": config.ELSER_INFERENCE_ID,
                "query": query_text
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
    console.print(Panel(f"[bold cyan]Query:[/bold cyan] {query}", title="Semantic Search"))
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
        console.print("\n[bold]Usage:[/bold] python 03_semantic_search.py \"your search query\"")
        console.print("\n[bold]Example queries:[/bold]")
        console.print("  python 03_semantic_search.py \"laptop for programming\"")
        console.print("  python 03_semantic_search.py \"affordable monitor for home office\"")
        console.print("  python 03_semantic_search.py \"wireless keyboard with long battery\"")
        console.print("  python 03_semantic_search.py \"portable storage with fast transfer\"")
        console.print()
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    console.print("\n[bold]Part 1 - Step 3: Semantic Search with ELSER[/bold]\n")

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
        response = semantic_search(es, query, size=10)

        # Display results
        display_results(query, response)

        console.print("[dim]💡 Tip: ELSER understands meaning, not just keywords![/dim]")
        console.print("[dim]   Try comparing with keyword search in step 04[/dim]\n")

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
