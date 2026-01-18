#!/bin/bash
# Docker Quick Start Script

echo "================================"
echo "LiveNewsAI - Docker Setup"
echo "================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "   Install from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✓ Docker found: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "   Install from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker Compose found: $(docker-compose --version)"
echo

# Check environment variables
echo "Checking environment variables..."
if [ -z "$NEWS_API_KEY" ]; then
    echo "⚠️  WARNING: NEWS_API_KEY not set"
    read -p "Enter your NEWS_API_KEY: " NEWS_API_KEY
    export NEWS_API_KEY
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set"
    read -p "Enter your OPENAI_API_KEY: " OPENAI_API_KEY
    export OPENAI_API_KEY
fi

echo "✓ API keys configured"
echo

# Build and start containers
echo "Building Docker image and starting containers..."
docker-compose up --build

echo
echo "================================"
echo "Server is running on:"
echo "  http://localhost:8000"
echo
echo "View logs:"
echo "  docker-compose logs -f app"
echo
echo "Stop containers:"
echo "  docker-compose down"
echo "================================"
