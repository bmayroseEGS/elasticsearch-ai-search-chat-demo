#!/usr/bin/env python3
"""
Part 2 - Step 1: Basic RAG (Retrieval Augmented Generation)

This script demonstrates RAG using ELSER for retrieval and OpenAI for generation.

RAG Flow:
1. User asks a question
2. ELSER searches for relevant products (semantic understanding!)
3. Retrieved products are sent to LLM as context
4. LLM generates response based ONLY on the retrieved context

This prevents hallucinations - the LLM can only use information from your data!

Note: Requires OpenAI API key for the LLM (GPT) part.
      The search/retrieval uses ELSER (no API key needed for that).
"""

import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import config

console = Console()

# Check if OpenAI is available for LLM
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

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

def retrieve_context(es, query, top_k=3):
    """Retrieve relevant products using ELSER semantic search."""

    search_query = {
        "query": {
            "sparse_vector": {
                "field": "elser_embedding",
                "inference_id": config.ELSER_INFERENCE_ID,
                "query": query
            }
        },
        "size": top_k,
        "_source": ["name", "category", "price", "description", "specifications", "features"]
    }

    try:
        response = es.search(index=config.INDEX_NAME, body=search_query)
        hits = response['hits']['hits']

        # Format context for LLM
        context_docs = []
        for hit in hits:
            source = hit['_source']
            doc_text = f"""
Product: {source.get('name', 'Unknown')}
Category: {source.get('category', 'N/A')}
Price: ${source.get('price', 0):.2f}
Description: {source.get('description', 'N/A')}
"""
            if source.get('features'):
                features = source['features'] if isinstance(source['features'], list) else [source['features']]
                doc_text += f"Features: {', '.join(features)}\n"

            if source.get('specifications'):
                specs = source['specifications']
                spec_str = ', '.join([f"{k}: {v}" for k, v in specs.items()])
                doc_text += f"Specifications: {spec_str}\n"

            context_docs.append(doc_text.strip())

        return context_docs, hits

    except Exception as e:
        console.print(f"[red]ERROR during retrieval: {e}[/red]")
        return [], []

def generate_response(client, query, context_docs):
    """Generate LLM response based on retrieved context."""

    # Create context string
    context = "\n\n---\n\n".join(context_docs)

    # System prompt
    system_prompt = """You are a helpful product assistant for an electronics store.

IMPORTANT RULES:
1. Only answer questions using information from the provided product search results
2. If no relevant products are found in the context, say "I don't have information about that"
3. Always include product names and prices in your recommendations
4. Do not make up specifications, features, or prices
5. Be concise and helpful
6. If asked about something not in the product catalog, politely decline"""

    # User prompt
    user_prompt = f"""Based on the following product information, please answer this question:

Question: {query}

Product Information:
{context}

Answer the question based ONLY on the information provided above."""

    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )

        return response.choices[0].message.content

    except Exception as e:
        console.print(f"[red]ERROR generating response: {e}[/red]")
        return None

def main():
    """Main RAG function."""
    if len(sys.argv) < 2:
        console.print("\n[bold]Usage:[/bold] python 01_basic_rag.py \"your question\"")
        console.print("\n[bold]Example questions:[/bold]")
        console.print("  python 01_basic_rag.py \"What laptops do you have for video editing?\"")
        console.print("  python 01_basic_rag.py \"I need a monitor for home office work\"")
        console.print("  python 01_basic_rag.py \"Which keyboards have good battery life?\"")
        console.print()
        sys.exit(1)

    question = ' '.join(sys.argv[1:])

    console.print("\n[bold]Part 2 - Step 1: Basic RAG with ELSER + OpenAI[/bold]\n")

    # Check for OpenAI
    if not OPENAI_AVAILABLE:
        console.print("[red]ERROR: OpenAI package not installed[/red]")
        console.print("\nTo use conversational AI features, install OpenAI:")
        console.print("  pip install openai")
        console.print("\nAnd add your API key to config.py:")
        console.print("  OPENAI_API_KEY = 'sk-your-key-here'")
        console.print()
        sys.exit(1)

    if not hasattr(config, 'OPENAI_API_KEY') or not config.OPENAI_API_KEY:
        console.print("[red]ERROR: OpenAI API key not configured[/red]")
        console.print("\nAdd your API key to config.py:")
        console.print("  OPENAI_API_KEY = 'sk-your-key-here'")
        console.print()
        sys.exit(1)

    try:
        # Connect to Elasticsearch
        console.print(f"Connecting to Elasticsearch at {config.ELASTICSEARCH_URL}...")
        es = connect_to_elasticsearch()
        console.print("[green]✓ Connected to Elasticsearch[/green]\n")

        # Check if index exists
        if not es.indices.exists(index=config.INDEX_NAME):
            console.print(f"[red]ERROR: Index '{config.INDEX_NAME}' does not exist[/red]")
            console.print("Run part1 scripts first to set up ELSER and ingest data\n")
            sys.exit(1)

        # Initialize OpenAI client
        client = OpenAI(api_key=config.OPENAI_API_KEY)

        # Show question
        console.print(Panel(f"[bold cyan]{question}[/bold cyan]", title="Your Question"))

        # Step 1: Retrieve context using ELSER
        console.print("\n[dim]Step 1: Searching for relevant products using ELSER...[/dim]")
        context_docs, hits = retrieve_context(es, question, top_k=config.RAG_TOP_K)

        if not context_docs:
            console.print("[yellow]No relevant products found[/yellow]")
            sys.exit(0)

        console.print(f"[green]✓ Found {len(context_docs)} relevant products[/green]")

        # Show retrieved products
        console.print("\n[bold]Retrieved Products:[/bold]")
        for i, hit in enumerate(hits, 1):
            source = hit['_source']
            console.print(f"  {i}. {source.get('name')} - ${source.get('price', 0):.2f}")

        # Step 2: Generate response
        console.print("\n[dim]Step 2: Generating response with OpenAI...[/dim]")
        response = generate_response(client, question, context_docs)

        if not response:
            console.print("[red]Failed to generate response[/red]")
            sys.exit(1)

        console.print("[green]✓ Response generated[/green]\n")

        # Show response
        console.print(Panel(Markdown(response), title="Assistant Response", border_style="green"))

        console.print("\n[dim]💡 How RAG Works:[/dim]")
        console.print("[dim]  1. ELSER found relevant products (semantic search)[/dim]")
        console.print("[dim]  2. Products sent to GPT as context[/dim]")
        console.print("[dim]  3. GPT can ONLY use information from those products[/dim]")
        console.print("[dim]  4. This prevents hallucinations![/dim]\n")

        es.close()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]ERROR: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
