#!/usr/bin/env python3
"""
Part 2 - Step 1: Basic RAG (Retrieval Augmented Generation)

Implements a simple RAG chatbot that:
1. Takes a user question
2. Searches Elasticsearch for relevant products
3. Passes search results to LLM as context
4. Generates a grounded response

This prevents hallucinations by grounding the LLM in actual data.

Usage: python 01_basic_rag.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from openai import OpenAI
import config
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

def generate_query_embedding(client: OpenAI, query: str) -> list:
    """Generate embedding for search query."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=query
    )
    return response.data[0].embedding

def search_products(es: Elasticsearch, client: OpenAI, query: str, top_k: int = 3) -> list:
    """
    Search for relevant products using hybrid search.

    Args:
        es: Elasticsearch client
        client: OpenAI client
        query: User's question
        top_k: Number of products to retrieve

    Returns:
        List of relevant product documents
    """

    # Generate query embedding
    query_vector = generate_query_embedding(client, query)

    # Hybrid search query
    search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description^2", "category", "features"],
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        },
        "knn": {
            "field": "embedding_vector",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": 50
        },
        "rank": {
            "rrf": {
                "window_size": 50,
                "rank_constant": config.RRF_RANK_CONSTANT
            }
        },
        "size": top_k
    }

    results = es.search(index=config.INDEX_NAME, body=search_query)

    # Extract relevant documents
    documents = []
    for hit in results['hits']['hits']:
        documents.append(hit['_source'])

    return documents

def format_context(documents: list) -> str:
    """
    Format retrieved documents into context for the LLM.

    Args:
        documents: List of product documents

    Returns:
        Formatted context string
    """

    if not documents:
        return "No relevant products found in the database."

    context_parts = []

    for idx, doc in enumerate(documents, 1):
        product_info = f"""
Product {idx}:
- Name: {doc.get('name')}
- Category: {doc.get('category')}
- Price: ${doc.get('price', 0):,.2f}
- Description: {doc.get('description')}
"""

        # Add specifications if available
        if 'specifications' in doc and doc['specifications']:
            specs = doc['specifications']
            product_info += "- Key Specs:\n"
            for key, value in list(specs.items())[:5]:  # Limit to 5 specs
                product_info += f"  • {key}: {value}\n"

        # Add reviews if available
        if 'reviews' in doc:
            reviews = doc['reviews']
            product_info += f"- Rating: {reviews.get('rating')}/5.0 ({reviews.get('count')} reviews)\n"
            product_info += f"- Review Summary: {reviews.get('summary')}\n"

        context_parts.append(product_info)

    return "\n".join(context_parts)

def generate_response(client: OpenAI, question: str, context: str) -> str:
    """
    Generate LLM response based on retrieved context.

    Args:
        client: OpenAI client
        question: User's question
        context: Retrieved product information

    Returns:
        LLM's response
    """

    messages = [
        {
            "role": "system",
            "content": config.RAG_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""Based on the following product information, please answer the user's question.

PRODUCT INFORMATION:
{context}

USER QUESTION:
{question}

Please provide a helpful and accurate response based only on the information provided above."""
        }
    ]

    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )

    return response.choices[0].message.content

def display_rag_process(console: Console, question: str, documents: list, response: str):
    """Display the RAG process visually."""

    # Step 1: Question
    console.print("\n[bold cyan]STEP 1: User Question[/bold cyan]")
    console.print(Panel(question, border_style="cyan"))

    # Step 2: Retrieved Documents
    console.print("\n[bold cyan]STEP 2: Retrieved Products (from Elasticsearch)[/bold cyan]")
    for idx, doc in enumerate(documents, 1):
        doc_summary = f"""**{doc.get('name')}** - ${doc.get('price', 0):,.2f}
{doc.get('description')[:150]}..."""
        console.print(Panel(doc_summary, title=f"Product {idx}", border_style="green"))

    # Step 3: LLM Response
    console.print("\n[bold cyan]STEP 3: LLM Response (Grounded in Retrieved Data)[/bold cyan]")
    console.print(Panel(Markdown(response), border_style="yellow"))

def chat_loop(es: Elasticsearch, client: OpenAI, console: Console):
    """Interactive chat loop."""

    console.print("\n[bold green]🤖 RAG Chatbot Ready![/bold green]")
    console.print("Ask me questions about products. Type 'quit' to exit.\n")

    while True:
        try:
            # Get user input
            question = console.input("[bold blue]You:[/bold blue] ")

            if question.lower() in ['quit', 'exit', 'q']:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break

            if not question.strip():
                continue

            # Search for relevant products
            console.print("\n[dim]🔍 Searching for relevant products...[/dim]")
            documents = search_products(es, client, question, top_k=config.RAG_TOP_K)

            if not documents:
                console.print("[red]No relevant products found. Try a different question.[/red]\n")
                continue

            # Format context
            context = format_context(documents)

            # Generate response
            console.print("[dim]💭 Generating response...[/dim]")
            response = generate_response(client, question, context)

            # Display results
            display_rag_process(console, question, documents, response)
            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Goodbye! 👋[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]\n")

def main():
    """Main function."""

    console = Console()

    # Display intro
    intro = """
# Basic RAG Chatbot

This demonstrates Retrieval Augmented Generation:
1. **Retrieve** relevant products from Elasticsearch
2. **Augment** the LLM prompt with retrieved data
3. **Generate** a response grounded in actual data

**Why this prevents hallucinations:**
The LLM only sees information from your database, so it can't make up facts.
"""
    console.print(Panel(Markdown(intro), title="Welcome", border_style="cyan"))

    # Connect to Elasticsearch
    console.print("\n[dim]Connecting to Elasticsearch...[/dim]")

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
        console.print("[red]ERROR: Could not connect to Elasticsearch[/red]")
        sys.exit(1)

    if not es.indices.exists(index=config.INDEX_NAME):
        console.print(f"[red]ERROR: Index '{config.INDEX_NAME}' does not exist[/red]")
        console.print("Run part1_smart_search scripts first")
        sys.exit(1)

    # Initialize OpenAI client
    console.print("[dim]Initializing OpenAI client...[/dim]")
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    # Start chat loop
    try:
        chat_loop(es, client, console)
    finally:
        es.close()

if __name__ == "__main__":
    main()
