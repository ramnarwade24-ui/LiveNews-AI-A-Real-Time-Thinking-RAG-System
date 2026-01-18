#!/usr/bin/env python3
"""
Example usage script for LiveNewsAI.
Demonstrates how to use the API programmatically.
"""

import requests
import json
import time
from typing import Optional


class LiveNewsAIClient:
    """Client for interacting with LiveNewsAI API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize client.

        Args:
            base_url: Base URL of LiveNewsAI API
        """
        self.base_url = base_url

    def health(self) -> dict:
        """Check system health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def ask(self, question: str, top_k: int = 5) -> dict:
        """
        Ask a question about the news.

        Args:
            question: Question to ask
            top_k: Number of articles to retrieve

        Returns:
            Response with answer and sources
        """
        payload = {"question": question, "top_k": top_k}
        response = requests.post(
            f"{self.base_url}/ask",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    def stats(self) -> dict:
        """Get system statistics."""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    def articles(self, limit: int = 10) -> dict:
        """Get recent articles."""
        response = requests.get(f"{self.base_url}/articles", params={"limit": limit})
        response.raise_for_status()
        return response.json()


def demo_basic_usage():
    """Basic usage demonstration."""
    print("\n" + "=" * 60)
    print("LiveNewsAI - Basic Usage Demo")
    print("=" * 60 + "\n")

    client = LiveNewsAIClient()

    # 1. Check health
    print("1. Checking system health...")
    try:
        health = client.health()
        print(f"   Status: {health['status']}")
        print(f"   Index Size: {health['index_size']} articles")
        print(f"   Pipeline Running: {health['pipeline_running']}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server. Is it running?")
        print("   Start server with: python livenewsai/app.py")
        return

    # Wait for articles to be indexed
    if health["index_size"] == 0:
        print("\n   ⏳ Waiting for articles to be indexed (up to 60 seconds)...")
        for i in range(6):
            time.sleep(10)
            health = client.health()
            if health["index_size"] > 0:
                print(f"   ✓ Articles indexed: {health['index_size']}")
                break
            print(f"   Still waiting... ({(i+1)*10}s)")

    # 2. Get statistics
    print("\n2. Getting system statistics...")
    stats = client.stats()
    print(f"   Total Documents: {stats['index_size']}")
    print(f"   Embedding Dimension: {stats['embedding_dimension']}")
    print(f"   Embedding Model: {stats['embedding_model']}")

    # 3. Ask questions
    questions = [
        "What are the latest developments in artificial intelligence?",
        "Tell me about recent business news",
        "What's happening in technology today?",
    ]

    print("\n3. Asking questions...")
    for question in questions:
        print(f"\n   Q: {question}")
        try:
            result = client.ask(question, top_k=3)
            print(f"   A: {result['answer'][:200]}...")
            print(f"   Sources: {len(result['sources'])} articles")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("   No relevant articles found")
            else:
                print(f"   Error: {e}")

    # 4. List recent articles
    print("\n4. Recent articles in index...")
    articles = client.articles(limit=5)
    for i, article in enumerate(articles["articles"], 1):
        print(f"\n   {i}. {article['title']}")
        print(f"      Source: {article['source']}")
        print(f"      URL: {article['url']}")


def demo_real_time_updates():
    """Demonstrate real-time updates."""
    print("\n" + "=" * 60)
    print("LiveNewsAI - Real-Time Updates Demo")
    print("=" * 60 + "\n")

    client = LiveNewsAIClient()

    question = "What is happening in technology?"

    print(f"Question: {question}\n")
    print("This demo shows how answers update as new articles arrive.\n")

    for iteration in range(3):
        print(f"Iteration {iteration + 1}:")

        # Get stats
        stats = client.stats()
        print(f"  Index size: {stats['index_size']} articles")

        # Ask question
        try:
            result = client.ask(question, top_k=3)
            print(f"  Answer: {result['answer'][:150]}...")
            print(f"  Sources: {len(result['sources'])} articles\n")
        except requests.exceptions.HTTPError:
            print("  Waiting for articles...\n")

        # Wait before next iteration
        if iteration < 2:
            print(f"  Waiting 30 seconds for new articles...")
            time.sleep(30)


def demo_batch_questions():
    """Demonstrate batch question processing."""
    print("\n" + "=" * 60)
    print("LiveNewsAI - Batch Questions Demo")
    print("=" * 60 + "\n")

    client = LiveNewsAIClient()

    questions = [
        "Latest AI breakthroughs",
        "Stock market updates",
        "Global health news",
        "Technology innovations",
        "Business mergers",
        "Science discoveries",
    ]

    print(f"Processing {len(questions)} questions...\n")

    results = []
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}...", end=" ")
        try:
            result = client.ask(question, top_k=3)
            print("✓")
            results.append(result)
        except requests.exceptions.HTTPError as e:
            print(f"✗ ({e.response.status_code})")

    # Summary
    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Questions processed: {len(results)}/{len(questions)}")
    if results:
        avg_sources = sum(r["num_documents"] for r in results) / len(results)
        print(f"  Avg sources per question: {avg_sources:.1f}")


def demo_api_integration():
    """Demonstrate API integration example."""
    print("\n" + "=" * 60)
    print("LiveNewsAI - API Integration Example")
    print("=" * 60 + "\n")

    print("""
Example code for integrating LiveNewsAI into your application:

```python
import requests

# Initialize
API_URL = "http://localhost:8000"

# Ask a question
response = requests.post(
    f"{API_URL}/ask",
    json={"question": "What's the latest news?", "top_k": 5}
)

result = response.json()

# Use the answer
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")

# Check health
health = requests.get(f"{API_URL}/health").json()
print(f"System healthy: {health['status']}")
print(f"Articles indexed: {health['index_size']}")
```
    """)


def main():
    """Run demonstrations."""
    import sys

    print("\n" + "=" * 60)
    print("LiveNewsAI - Example Usage")
    print("=" * 60)
    print("\nChoose a demo:")
    print("  1. Basic usage")
    print("  2. Real-time updates")
    print("  3. Batch questions")
    print("  4. API integration example")
    print("  5. Run all demos")
    print("  q. Quit")
    print()

    choice = input("Enter choice (1-5 or q): ").strip().lower()

    if choice == "1":
        demo_basic_usage()
    elif choice == "2":
        demo_real_time_updates()
    elif choice == "3":
        demo_batch_questions()
    elif choice == "4":
        demo_api_integration()
    elif choice == "5":
        demo_basic_usage()
        demo_batch_questions()
        demo_api_integration()
    elif choice == "q":
        return
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
