#!/bin/bash
# LiveNewsAI Quick Start Script
# This script sets up and runs LiveNewsAI locally

set -e

echo "================================"
echo "LiveNewsAI - Quick Start Setup"
echo "================================"
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if API keys are set
echo
echo "Checking environment variables..."
if [ -z "$NEWS_API_KEY" ]; then
    echo "⚠️  WARNING: NEWS_API_KEY not set"
    echo "   Get a free key at: https://newsapi.org"
    echo
    read -p "Enter your NEWS_API_KEY: " NEWS_API_KEY
    export NEWS_API_KEY
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set"
    echo "   Get a key at: https://platform.openai.com"
    echo
    read -p "Enter your OPENAI_API_KEY: " OPENAI_API_KEY
    export OPENAI_API_KEY
fi

echo "✓ API keys configured"
echo

# Create virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Install dependencies
echo "Installing dependencies..."
cd livenewsai
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"
echo

# Run the application
echo "Starting LiveNewsAI..."
echo
echo "================================"
echo "Server starting on:"
echo "  http://localhost:8000"
echo
echo "API Documentation:"
echo "  http://localhost:8000/docs"
echo
echo "Example requests:"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/ask \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"question\": \"Latest AI news\"}'"
echo
echo "Press Ctrl+C to stop"
echo "================================"
echo

python app.py
