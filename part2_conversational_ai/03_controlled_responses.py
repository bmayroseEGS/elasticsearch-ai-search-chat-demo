#!/usr/bin/env python3
"""
Part 2 - Step 3: Controlled Responses with Prompt Engineering

Demonstrates how to control AI behavior through:
1. Strict system prompts with clear boundaries
2. Response format requirements
3. Tone and style guidelines
4. Safety guardrails

Usage: python 03_controlled_responses.py
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

CONTROLLED_SYSTEM_PROMPT = """You are a professional product assistant for an electronics store.

STRICT RULES - YOU MUST FOLLOW THESE:

1. **Only use provided data**: Answer ONLY based on the product information given. Never make up specifications, prices, or features.

2. **Admit ignorance**: If the information isn't in the search results, say "I don't have that information in my database."

3. **Be accurate with numbers**: Always state exact prices, ratings, and specifications from the data. Don't round or estimate.

4. **Stay on topic**: Only answer questions about products. Politely decline:
   - Personal advice unrelated to products
   - General tech support
   - Questions about competitors not in the database
   - Requests to perform actions (placing orders, etc.)

5. **Response format**:
   - Start with a direct answer
   - Include product name(s) and price(s)
   - Mention key specifications relevant to the question
   - Keep responses under 150 words
   - Use bullet points for comparisons

6. **Tone**: Professional, helpful, concise. No fluff or marketing speak.

7. **Comparisons**: When comparing products, use factual differences only. Don't make subjective judgments beyond what's in review data.

8. **Availability**: Never claim products are "in stock" or make promises about availability. Stick to product specifications.

EXAMPLES OF GOOD RESPONSES:
- "The Dell XPS 15 at $1,899 has 32GB RAM and RTX 4050 graphics, ideal for video editing."
- "I found 3 gaming laptops under $2000: [lists with names, prices, key specs]"
- "I don't have information about battery replacement costs in my database."

EXAMPLES OF BAD RESPONSES:
- "This is the best laptop ever!" (subjective)
- "It costs around $2000" (imprecise)
- "We have plenty in stock" (outside scope)
- "You should definitely buy this" (pushy)
"""

def generate_query_embedding(client: OpenAI, query: str) -> list:
    """Generate embedding for search query."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=query
    )
    return response.data[0].embedding

def search_products(es: Elasticsearch, client: OpenAI, query: str, top_k: int = 3) -> list:
    """Search for relevant products."""

    query_vector = generate_query_embedding(client, query)

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

    documents = []
    for hit in results['hits']['hits']:
        documents.append(hit['_source'])

    return documents

def format_context(documents: list) -> str:
    """Format retrieved documents into context."""

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
            product_info += "- Specifications:\n"
            for key, value in specs.items():
                product_info += f"  • {key}: {value}\n"

        if 'features' in doc:
            product_info += f"- Features: {', '.join(doc['features'][:5])}\n"

        if 'reviews' in doc:
            reviews = doc['reviews']
            product_info += f"- Customer Rating: {reviews.get('rating')}/5.0 ({reviews.get('count')} reviews)\n"
            product_info += f"- Review Summary: {reviews.get('summary')}\n"

        context_parts.append(product_info)

    return "\n".join(context_parts)

def generate_controlled_response(client: OpenAI, question: str, context: str) -> Dict:
    """
    Generate a controlled response with validation.

    Returns:
        Dictionary with 'response', 'followed_rules', and 'explanation'
    """

    messages = [
        {
            "role": "system",
            "content": CONTROLLED_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""PRODUCT DATA:
{context}

USER QUESTION:
{question}

Provide a helpful response following all the rules in your system prompt."""
        }
    ]

    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=0.3,  # Lower temperature for more consistent, factual responses
        max_tokens=300
    )

    answer = response.choices[0].message.content

    # Basic validation
    followed_rules = {
        "includes_price": "$" in answer,
        "concise": len(answer.split()) < 200,
        "no_superlatives": not any(word in answer.lower() for word in ["best", "amazing", "incredible", "perfect"]),
        "factual_tone": True  # Would need more sophisticated NLP to verify
    }

    return {
        "response": answer,
        "followed_rules": followed_rules
    }

def test_scenarios(es: Elasticsearch, client: OpenAI, console: Console):
    """Test the chatbot with various scenarios to demonstrate control."""

    test_cases = [
        {
            "name": "Normal product question",
            "question": "What laptops do you have for video editing under $2000?",
            "expected": "Should list relevant laptops with exact prices and specs"
        },
        {
            "name": "Out-of-scope question",
            "question": "Can you help me fix my printer?",
            "expected": "Should politely decline and stay within product Q&A scope"
        },
        {
            "name": "Request for unavailable info",
            "question": "When will the new MacBook be released?",
            "expected": "Should admit lack of information"
        },
        {
            "name": "Comparison request",
            "question": "Compare the Dell XPS and MacBook Pro",
            "expected": "Should provide factual comparison with specs and prices"
        }
    ]

    console.print("\n[bold cyan]Testing Controlled Response System[/bold cyan]\n")

    for i, test in enumerate(test_cases, 1):
        console.print(f"[bold yellow]Test {i}: {test['name']}[/bold yellow]")
        console.print(f"Question: [italic]{test['question']}[/italic]")
        console.print(f"Expected: [dim]{test['expected']}[/dim]\n")

        # Search and generate response
        documents = search_products(es, client, test['question'], top_k=3)
        context = format_context(documents)
        result = generate_controlled_response(client, test['question'], context)

        # Display response
        console.print("[bold green]Response:[/bold green]")
        console.print(Panel(Markdown(result['response']), border_style="green"))

        # Show rule compliance
        rules = result['followed_rules']
        compliance = f"""
**Rule Compliance:**
- ✅ Includes pricing: {rules['includes_price']}
- ✅ Concise (< 200 words): {rules['concise']}
- ✅ No superlatives: {rules['no_superlatives']}
        """
        console.print(Panel(compliance.strip(), border_style="blue"))
        console.print()

        # Pause between tests
        if i < len(test_cases):
            console.input("[dim]Press Enter for next test...[/dim]\n")

def chat_loop(es: Elasticsearch, client: OpenAI, console: Console):
    """Interactive chat loop with controlled responses."""

    console.print("\n[bold green]🤖 Controlled RAG Chatbot Ready![/bold green]")
    console.print("Responses are controlled by strict prompt engineering.")
    console.print("Type 'quit' to exit.\n")

    while True:
        try:
            question = console.input("[bold blue]You:[/bold blue] ")

            if question.lower() in ['quit', 'exit', 'q']:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break

            if not question.strip():
                continue

            # Search and generate
            console.print("\n[dim]🔍 Searching...[/dim]")
            documents = search_products(es, client, question, top_k=config.RAG_TOP_K)
            context = format_context(documents)

            console.print("[dim]💭 Generating controlled response...[/dim]")
            result = generate_controlled_response(client, question, context)

            # Display
            console.print(f"\n[bold yellow]Bot:[/bold yellow]")
            console.print(Panel(Markdown(result['response']), border_style="yellow"))

            # Show compliance
            rules = result['followed_rules']
            if all(rules.values()):
                console.print("[dim green]✓ All rules followed[/dim green]\n")
            else:
                console.print(f"[dim yellow]⚠ Rule compliance: {rules}[/dim yellow]\n")

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
# Controlled Responses with Prompt Engineering

This demonstrates **strict AI control** through:

✅ **Clear boundaries**: Only answer product questions
✅ **Factual accuracy**: Never make up information
✅ **Consistent format**: Structured responses with prices/specs
✅ **Professional tone**: No marketing hype or superlatives
✅ **Safety guardrails**: Admits ignorance when appropriate

**Prompt engineering includes:**
- Explicit rules in system prompt
- Response format requirements
- Examples of good/bad responses
- Lower temperature (0.3) for consistency

Choose an option:
"""
    console.print(Panel(Markdown(intro), title="Welcome", border_style="cyan"))

    console.print("[1] Run test scenarios (demonstrates control)")
    console.print("[2] Interactive chat")
    choice = console.input("\n[bold]Choose (1 or 2):[/bold] ")

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

    # Run chosen mode
    try:
        if choice == "1":
            test_scenarios(es, client, console)
        else:
            chat_loop(es, client, console)
    finally:
        es.close()

if __name__ == "__main__":
    main()
