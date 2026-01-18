#!/usr/bin/env python3
"""
LiveNewsAI - File Index and Navigation Guide
This script provides an overview of all project files and their purposes.
"""

import os
from pathlib import Path


def print_file_structure():
    """Print the complete project structure with descriptions."""

    structure = {
        "Root Documentation": {
            "README.md": "Main project overview, features, and quick start",
            "GETTING_STARTED.md": "Step-by-step setup guide for first-time users",
            "DEPLOYMENT.md": "Cloud deployment guide (AWS, GCP, Kubernetes)",
            "PROJECT_SUMMARY.md": "Executive summary and validation checklist",
            "LICENSE": "MIT License",
        },
        "Docker & Deployment": {
            "Dockerfile": "Production-ready Docker image definition",
            "docker-compose.yml": "Multi-container orchestration configuration",
            ".env.example": "Environment variable template",
            ".gitignore": "Git ignore patterns",
        },
        "Quick Start Scripts": {
            "quickstart.sh": "Automated local setup (venv + dependencies + run)",
            "docker-quickstart.sh": "Automated Docker setup and deployment",
            "setup-permissions.sh": "Make scripts executable",
            "examples.py": "Interactive demonstration and usage examples",
        },
        "Application Code": {
            "livenewsai/": {
                "app.py": "FastAPI server with 5 REST endpoints",
                "pathway_pipeline.py": "Streaming pipeline, embeddings, vector indexing",
                "connectors.py": "NewsAPI connector with polling and deduplication",
                "rag.py": "RAG engine with LLM integration",
                "config.py": "Configuration management",
                "__init__.py": "Package initialization",
                "requirements.txt": "Python dependencies",
                "README.md": "Full API documentation",
                "test_livenewsai.py": "Comprehensive test suite",
            }
        },
    }

    print("\n" + "=" * 80)
    print("LiveNewsAI - Complete Project Structure")
    print("=" * 80 + "\n")

    for section, files in structure.items():
        print(f"\n📁 {section}")
        print("-" * 80)

        if isinstance(files, dict):
            for key, value in files.items():
                if isinstance(value, dict):
                    # Nested section
                    print(f"\n  📂 {key}")
                    for file, desc in value.items():
                        print(f"    • {file:<30} - {desc}")
                else:
                    print(f"  • {key:<30} - {value}")


def print_quick_navigation():
    """Print quick navigation guide."""

    print("\n\n" + "=" * 80)
    print("Quick Navigation")
    print("=" * 80 + "\n")

    navigation = {
        "🚀 Getting Started": [
            "1. Read: GETTING_STARTED.md",
            "2. Run: bash quickstart.sh (local) OR bash docker-quickstart.sh (Docker)",
            "3. Visit: http://localhost:8000/docs",
        ],
        "📚 Documentation": [
            "API Reference: livenewsai/README.md",
            "Setup Guide: GETTING_STARTED.md",
            "Deployment: DEPLOYMENT.md",
            "Project Summary: PROJECT_SUMMARY.md",
        ],
        "🔑 Key Files": [
            "API Server: livenewsai/app.py",
            "Streaming Pipeline: livenewsai/pathway_pipeline.py",
            "News Connector: livenewsai/connectors.py",
            "RAG Engine: livenewsai/rag.py",
            "Configuration: livenewsai/config.py",
        ],
        "🐳 Docker": [
            "Build & Run: docker-compose up --build",
            "Quick Start: bash docker-quickstart.sh",
            "Stop: docker-compose down",
            "Logs: docker-compose logs -f app",
        ],
        "🧪 Testing": [
            "Tests: livenewsai/test_livenewsai.py",
            "Examples: python examples.py",
            "Run Tests: pytest livenewsai/test_livenewsai.py -v",
        ],
    }

    for category, items in navigation.items():
        print(f"{category}")
        for item in items:
            print(f"  • {item}")
        print()


def print_getting_started():
    """Print quick getting started commands."""

    print("\n" + "=" * 80)
    print("Quick Start Commands")
    print("=" * 80 + "\n")

    commands = {
        "Set API Keys (Required)": [
            "export NEWS_API_KEY='your-newsapi-key'",
            "export OPENAI_API_KEY='your-openai-api-key'",
        ],
        "Local Setup": [
            "bash quickstart.sh",
            "Or manually:",
            "  python3 -m venv venv",
            "  source venv/bin/activate",
            "  cd livenewsai && pip install -r requirements.txt",
            "  python app.py",
        ],
        "Docker Setup": [
            "bash docker-quickstart.sh",
            "Or manually:",
            "  docker-compose up --build",
        ],
        "Test Endpoints": [
            "curl http://localhost:8000/health",
            "curl -X POST http://localhost:8000/ask \\",
            "  -H 'Content-Type: application/json' \\",
            "  -d '{\"question\":\"Latest news\", \"top_k\":5}'",
        ],
        "View Documentation": [
            "Open: http://localhost:8000/docs",
            "Swagger UI with all endpoints and examples",
        ],
    }

    for category, cmds in commands.items():
        print(f"📌 {category}")
        for cmd in cmds:
            print(f"   {cmd}")
        print()


def print_file_purposes():
    """Print detailed purpose of each file."""

    print("\n" + "=" * 80)
    print("File Purposes (Detailed)")
    print("=" * 80 + "\n")

    purposes = {
        "Core Application": {
            "livenewsai/app.py": """
            FastAPI server implementing REST API
            - GET / : API information
            - GET /health : System health check
            - POST /ask : Answer questions about news
            - GET /stats : System statistics
            - GET /articles : List recent articles
            """,
            "livenewsai/pathway_pipeline.py": """
            Real-time streaming data pipeline
            - NewsAPI connector integration
            - Article text processing
            - OpenAI embedding generation
            - In-memory KNN vector index
            - Query search functionality
            """,
            "livenewsai/connectors.py": """
            NewsAPI connector implementation
            - Polls NewsAPI every 60 seconds
            - Deduplicates articles by URL
            - Parses article metadata
            - Yields articles as they arrive
            """,
            "livenewsai/rag.py": """
            RAG (Retrieval Augmented Generation) engine
            - Builds context from retrieved documents
            - Calls OpenAI LLM for answer generation
            - Formats responses with sources
            - Handles error cases
            """,
            "livenewsai/config.py": """
            Configuration management
            - API keys from environment variables
            - Model and parameter settings
            - Logging configuration
            - Path management
            """,
        },
        "Deployment": {
            "Dockerfile": """
            Docker image definition
            - Python 3.11 slim base
            - Dependency installation
            - Application setup
            - Health check configuration
            """,
            "docker-compose.yml": """
            Multi-container orchestration
            - Service definition
            - Port mapping
            - Environment variables
            - Volume mounting
            - Resource limits
            """,
            ".env.example": """
            Environment variable template
            - API key placeholders
            - Configuration examples
            - Documentation for each option
            """,
        },
        "Scripts": {
            "quickstart.sh": """
            Local development quick start
            - Creates virtual environment
            - Installs dependencies
            - Sets up environment
            - Starts server
            """,
            "docker-quickstart.sh": """
            Docker quick start
            - Checks Docker installation
            - Validates API keys
            - Builds and runs containers
            - Shows access URLs
            """,
            "examples.py": """
            Interactive usage demonstrations
            - Basic API usage
            - Real-time update demo
            - Batch processing
            - API integration examples
            """,
        },
        "Documentation": {
            "README.md": """
            Main project documentation
            - Overview and features
            - Architecture explanation
            - Quick start guide
            - API examples
            - Tech stack
            - Troubleshooting
            """,
            "GETTING_STARTED.md": """
            Step-by-step setup guide
            - Prerequisites
            - API key setup
            - Installation options
            - First steps
            - Configuration
            """,
            "DEPLOYMENT.md": """
            Cloud deployment guide
            - AWS EC2 setup
            - Google Cloud Run
            - Kubernetes
            - Performance tuning
            - Monitoring
            """,
            "PROJECT_SUMMARY.md": """
            Executive summary
            - Complete deliverables
            - Validation checklist
            - Use cases
            - Cost estimation
            """,
            "livenewsai/README.md": """
            Full API documentation
            - Architecture details
            - API endpoints
            - Configuration options
            - Performance characteristics
            - Troubleshooting
            """,
        },
        "Testing": {
            "livenewsai/test_livenewsai.py": """
            Comprehensive test suite
            - Unit tests for all modules
            - Integration tests
            - API endpoint tests
            - Error handling tests
            """,
        },
    }

    for category, files in purposes.items():
        print(f"\n{category}")
        print("-" * 80)
        for filename, purpose in files.items():
            print(f"\n📄 {filename}")
            print(purpose.strip())


def main():
    """Print complete project navigation guide."""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          LiveNewsAI - File Index                             ║
║         Real-Time RAG System for Breaking News with Pathway                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    print_file_structure()
    print_quick_navigation()
    print_getting_started()
    print_file_purposes()

    print("\n" + "=" * 80)
    print("📞 Support & Resources")
    print("=" * 80)
    print("""
Documentation:
  • Full Docs: livenewsai/README.md
  • Getting Started: GETTING_STARTED.md
  • Deployment: DEPLOYMENT.md
  • Project Summary: PROJECT_SUMMARY.md

Examples:
  • Interactive Demo: python examples.py
  • Test Suite: pytest livenewsai/test_livenewsai.py -v

Online Resources:
  • Pathway: https://pathway.com/docs
  • FastAPI: https://fastapi.tiangolo.com/
  • OpenAI: https://platform.openai.com/docs
  • NewsAPI: https://newsapi.org/docs
    """)

    print("\n" + "=" * 80)
    print("✨ Ready to Start?")
    print("=" * 80)
    print("""
1. Get API keys:
   • NewsAPI: https://newsapi.org
   • OpenAI: https://platform.openai.com

2. Set environment variables:
   export NEWS_API_KEY='your-key'
   export OPENAI_API_KEY='your-key'

3. Run quick start:
   bash quickstart.sh          # Local
   OR
   bash docker-quickstart.sh   # Docker

4. Visit: http://localhost:8000/docs

5. Ask your first question!
    """)

    print("=" * 80)
    print("Happy streaming! 🚀\n")


if __name__ == "__main__":
    main()
