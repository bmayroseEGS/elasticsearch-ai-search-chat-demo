#!/usr/bin/env python3
"""
Part 2 - Step 2: Conversational Chat with Memory

Extends basic RAG with conversation history:
1. Maintains context across multiple turns
2. Uses previous messages to understand references ("it", "that one", "the first")
3. Provides coherent multi-turn conversations

Usage: python 02_context_chat.py
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
from typing import List, Dict

class ConversationHistory:
    """Manages conversation history with size limits."""

    def __init__(self, max_messages: int = 10):
        self.messages: List[Dict[str, str]] = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str):
        """Add a message to history."""
        self.messages.append({"role": role, "content": content})

        # Trim if exceeds max
        if len(self.messages) > self.max_messages:
            # Keep system message (if present) and trim oldest user/assistant messages
            system_messages = [m for m in self.messages if m["role"] == "system"]
            other_messages = [m for m in self.messages if m["role"] != "system"]
            self.messages = system_messages + other_messages[-(self.max_messages - len(system_messages)):]

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages."""
        return self.messages

    def clear(self):
        """Clear conversation history."""
        self.messages = []

def generate_query_embedding(client: OpenAI, query: str) -> list:
    """Generate embedding for search query."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=query
    )
    return response.data[0].embedding

def search_products(es: Elasticsearch, client: OpenAI, query: str, conversation: List[Dict], top_k: int = 3) -> list:
    """
    Search for relevant products using conversational context.

    Args:
        es: Elasticsearch client
        client: OpenAI client
        query: Current user question
        conversation: Previous conversation history
        top_k: Number of products to retrieve

    Returns:
        List of relevant product documents
    """

    # If there's conversation history, use LLM to reformulate query for better search
    if len([m for m in conversation if m["role"] == "user"]) > 1:
        # Use LLM to create a standalone search query
        reformulation_messages = [
            {
                "role": "system",
                "content": "Given a conversation history and the latest question, create a standalone search query that captures the user's intent. Return ONLY the search query, nothing else."
            },
            *conversation[-4:],  # Last 2 turns
            {
                "role": "user",
                "content": f"Create a standalone search query for: {query}"
            }
        ]

        reformulation = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=reformulation_messages,
            temperature=0.3,
            max_tokens=50
        )

        search_query_text = reformulation.choices[0].message.content.strip()
    else:
        search_query_text = query

    # Generate query embedding
    query_vector = generate_query_embedding(client, search_query_text)

    # Hybrid search
    search_query = {
        "query": {
            "multi_match": {
                "query": search_query_text,
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

    documents = []
    for hit in results['hits']['hits']:
        documents.append(hit['_source'])

    return documents

def format_context(documents: list) -> str:
    """Format retrieved documents into context for the LLM."""

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

        if 'specifications' in doc and doc['specifications']:
            specs = doc['specifications']
            product_info += "- Key Specs:\n"
            for key, value in list(specs.items())[:5]:
                product_info += f"  • {key}: {value}\n"

        if 'reviews' in doc:
            reviews = doc['reviews']
            product_info += f"- Rating: {reviews.get('rating')}/5.0 ({reviews.get('count')} reviews)\n"

        context_parts.append(product_info)

    return "\n".join(context_parts)

def generate_response(client: OpenAI, question: str, context: str, history: ConversationHistory) -> str:
    """
    Generate LLM response with conversation history.

    Args:
        client: OpenAI client
        question: Current user question
        context: Retrieved product information
        history: Conversation history

    Returns:
        LLM's response
    """

    # Build messages with context
    messages = [
        {
            "role": "system",
            "content": f"""{config.RAG_SYSTEM_PROMPT}

IMPORTANT: You have access to the conversation history. Use it to understand references like:
- "it", "that one", "the first one" (refer to previously mentioned products)
- "compared to", "versus" (compare with products mentioned earlier)
- "tell me more" (expand on previous topic)

Always maintain context across the conversation."""
        }
    ]

    # Add conversation history (excluding system messages)
    for msg in history.get_messages():
        if msg["role"] != "system":
            messages.append(msg)

    # Add current question with context
    messages.append({
        "role": "user",
        "content": f"""Based on the following product information, please answer the user's question.

PRODUCT INFORMATION:
{context}

USER QUESTION:
{question}

Remember to use the conversation history to understand references and maintain coherent dialogue."""
    })

    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )

    return response.choices[0].message.content

def chat_loop(es: Elasticsearch, client: OpenAI, console: Console):
    """Interactive chat loop with conversation memory."""

    console.print("\n[bold green]🤖 Contextual RAG Chatbot Ready![/bold green]")
    console.print("I remember our conversation! Try asking follow-up questions.")
    console.print("Type 'quit' to exit, 'clear' to reset conversation.\n")

    history = ConversationHistory(max_messages=config.MAX_CONVERSATION_HISTORY)

    while True:
        try:
            # Get user input
            question = console.input("[bold blue]You:[/bold blue] ")

            if question.lower() in ['quit', 'exit', 'q']:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break

            if question.lower() == 'clear':
                history.clear()
                console.print("\n[green]✓ Conversation cleared[/green]\n")
                continue

            if not question.strip():
                continue

            # Add user message to history
            history.add_message("user", question)

            # Search for relevant products (with conversation context)
            console.print("\n[dim]🔍 Searching with conversational context...[/dim]")
            documents = search_products(es, client, question, history.get_messages(), top_k=config.RAG_TOP_K)

            if not documents:
                response = "I don't have information about that in my product database. Could you rephrase your question?"
                history.add_message("assistant", response)
                console.print(f"\n[bold yellow]Bot:[/bold yellow] {response}\n")
                continue

            # Format context
            context = format_context(documents)

            # Generate response with history
            console.print("[dim]💭 Generating contextual response...[/dim]")
            response = generate_response(client, question, context, history)

            # Add assistant response to history
            history.add_message("assistant", response)

            # Display response
            console.print(f"\n[bold yellow]Bot:[/bold yellow]")
            console.print(Panel(Markdown(response), border_style="yellow"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Goodbye! 👋[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]\n")
            import traceback
            traceback.print_exc()

def main():
    """Main function."""

    console = Console()

    # Display intro
    intro = """
# Conversational RAG with Memory

This extends basic RAG with **conversation history**:

✅ **Remembers context** across multiple questions
✅ **Understands references** like "it", "that one", "the first"
✅ **Maintains coherent** multi-turn dialogue
✅ **Query reformulation** for better search with context

**Try this conversation flow:**
1. "Show me gaming laptops"
2. "Which one has the best GPU?"  ← Uses context from #1
3. "How much does it cost?"       ← Knows "it" from #2
4. "Compare it to the MacBook"    ← References across turns
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
