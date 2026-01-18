# LiveNewsAI - Getting Started Guide

Welcome to LiveNewsAI! This guide will help you get started with the real-time RAG system.

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.10+** (for local development) OR **Docker** (for containerized deployment)
- **NewsAPI API Key** - Get your free key at [https://newsapi.org](https://newsapi.org)
- **OpenAI API Key** - Get your key at [https://platform.openai.com](https://platform.openai.com)
- **2GB RAM** minimum
- **100MB** free disk space

## 🔑 Getting API Keys

### 1. NewsAPI Key

1. Visit [https://newsapi.org](https://newsapi.org)
2. Click "Get API Key"
3. Sign up (free tier includes 100 requests/day)
4. Copy your API key

### 2. OpenAI API Key

1. Visit [https://platform.openai.com](https://platform.openai.com)
2. Sign in or create account
3. Go to API keys section
4. Create new API key
5. Copy your API key

## ⚡ Quick Start Options

Choose one of these three options:

### Option 1: Fastest Setup (Docker)

```bash
# Navigate to project directory
cd LiveNews-AI-A-Real-Time-Thinking-RAG-System

# Set your API keys
export NEWS_API_KEY="your-newsapi-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"

# Run quick start script
bash docker-quickstart.sh
```

This will:
- Build the Docker image
- Start the container
- Run the server on http://localhost:8000

### Option 2: Local Python Setup

```bash
# Navigate to project directory
cd LiveNews-AI-A-Real-Time-Thinking-RAG-System

# Set your API keys
export NEWS_API_KEY="your-newsapi-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"

# Run quick start script
bash quickstart.sh
```

This will:
- Create a virtual environment
- Install dependencies
- Start the server

### Option 3: Manual Setup

#### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
cd livenewsai
pip install -r requirements.txt
```

#### Step 3: Set Environment Variables

```bash
export NEWS_API_KEY="your-newsapi-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
```

#### Step 4: Start Server

```bash
python app.py
```

## 🌐 Accessing the Server

Once the server is running, visit:

- **API Documentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

## 🧪 First Steps

### 1. Check System Health

```bash
curl http://localhost:8000/health
```

### 2. Ask a Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the latest news in technology?",
    "top_k": 5
  }'
```

**Note**: If you get "Vector index is empty", wait 60 seconds for the first batch of articles to be fetched and indexed.

### 3. Check Statistics

```bash
curl http://localhost:8000/stats
```

### 4. View Recent Articles

```bash
curl http://localhost:8000/articles?limit=10
```

## 🎬 Interactive API Documentation

Visit http://localhost:8000/docs to see:
- All available endpoints
- Request/response schemas
- Try endpoints directly in the browser
- View example requests and responses

## 📝 Configuration

### Using Environment Variables

Set before starting the server:

```bash
# News API settings
export NEWS_POLLING_INTERVAL=60          # Fetch news every 60 seconds
export NEWS_BATCH_SIZE=20                # 20 articles per fetch

# Embedding settings
export EMBEDDING_MODEL=text-embedding-3-small
export TOP_K_RESULTS=5                   # Retrieve 5 articles per question

# LLM settings
export LLM_MODEL=gpt-4o-mini
export LLM_TEMPERATURE=0.7

# Server settings
export FASTAPI_PORT=8000
export LOG_LEVEL=INFO
```

### Using .env File

1. Copy `.env.example` to `.env`
2. Edit `.env` with your values
3. Load environment: `source .env` (Linux/Mac) or `.\.env` (Windows PowerShell)

## 📚 Usage Examples

### Python Client

```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/ask",
    json={
        "question": "What is happening in artificial intelligence?",
        "top_k": 5
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

### JavaScript/Node.js Client

```javascript
async function askQuestion(question) {
  const response = await fetch('http://localhost:8000/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: 5 })
  });
  return response.json();
}

askQuestion('What is the latest news?')
  .then(result => console.log(result.answer));
```

### CURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Ask question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Latest AI news", "top_k":5}'

# Get stats
curl http://localhost:8000/stats

# List articles
curl http://localhost:8000/articles?limit=20
```

## 🐛 Troubleshooting

### "Cannot connect to server"

- Check if server is running: `curl http://localhost:8000`
- Check port is free: `lsof -i :8000` (Mac/Linux)
- Try different port: `export FASTAPI_PORT=8001`

### "Vector index is empty"

- Wait 60+ seconds for initial article fetch
- Check API keys are set correctly
- View logs: `docker-compose logs app` (Docker) or check console output

### "API key invalid" errors

- Verify key is correct at [https://newsapi.org](https://newsapi.org) and [https://platform.openai.com](https://platform.openai.com)
- Check keys are exported: `echo $NEWS_API_KEY`
- Try without quotes: `export NEWS_API_KEY=your-key-no-quotes`

### Slow responses

- Reduce `TOP_K_RESULTS`: `export TOP_K_RESULTS=3`
- Use simpler embedding model: `export EMBEDDING_MODEL=text-embedding-3-small`
- Increase polling interval to reduce news fetching: `export NEWS_POLLING_INTERVAL=120`

### Docker errors

- Ensure Docker is running: `docker ps`
- Rebuild image: `docker-compose build --no-cache`
- View logs: `docker-compose logs -f app`
- Clean up: `docker-compose down -v`

## 📊 Monitoring

### View Logs

**Docker:**
```bash
docker-compose logs -f app
```

**Local:**
```bash
# Logs appear in console where you ran the server
# To see debug logs:
export LOG_LEVEL=DEBUG
```

### Monitor in Real-Time

```bash
# In one terminal, monitor index growth
watch -n 5 'curl -s http://localhost:8000/stats | jq .index_size'

# In another, ask questions
curl -X POST http://localhost:8000/ask \
  -d '{"question":"Your question"}' \
  -H "Content-Type: application/json"
```

## 🔄 Real-Time Demo

See the system update answers in real-time:

```bash
# Terminal 1: Start server
python livenewsai/app.py

# Terminal 2: Ask question
curl -X POST http://localhost:8000/ask \
  -d '{"question":"Technology news"}' \
  -H "Content-Type: application/json"

# Terminal 3: Watch index grow
watch -n 10 'curl http://localhost:8000/stats'

# After 60 seconds, ask the same question again
# Notice the answer includes newly arrived articles!
```

## 🚀 Advanced Configuration

### Performance Tuning

```bash
# Faster responses (fewer articles)
export TOP_K_RESULTS=3
export MAX_CONTEXT_LENGTH=1500

# More thorough answers (more articles)
export TOP_K_RESULTS=10
export MAX_CONTEXT_LENGTH=5000

# Faster indexing (fewer articles)
export NEWS_BATCH_SIZE=10
```

### Using Different LLM Model

```bash
# Faster and cheaper (recommended default)
export LLM_MODEL=gpt-4o-mini

# Slower but more powerful
export LLM_MODEL=gpt-4o
```

### Different Embedding Model

```bash
# Smaller and faster
export EMBEDDING_MODEL=text-embedding-3-small

# Larger and more accurate (more expensive)
export EMBEDDING_MODEL=text-embedding-3-large
```

## 📖 Next Steps

1. **Read Full Documentation**: [livenewsai/README.md](livenewsai/README.md)
2. **Check Examples**: `python examples.py`
3. **Run Tests**: `cd livenewsai && pytest test_livenewsai.py -v`
4. **Deploy to Cloud**: See [DEPLOYMENT.md](DEPLOYMENT.md)
5. **Extend the System**: Customize for your use case

## 🎓 Learning Resources

- [Pathway Documentation](https://pathway.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [NewsAPI Documentation](https://newsapi.org/docs)
- [RAG Concepts](https://blogs.nvidia.com/blog/2023/10/05/retrieval-augmented-generation-rag-illustrated/) (NVIDIA)

## 💬 Support

If you encounter issues:

1. Check [Troubleshooting](#-troubleshooting) section above
2. Read [livenewsai/README.md](livenewsai/README.md#troubleshooting)
3. Check logs for error messages
4. Open an issue on GitHub with:
   - Error message
   - Your configuration
   - Steps to reproduce

## 🎉 Success Checklist

After setup, verify:

- [ ] Server running on http://localhost:8000
- [ ] Health check returns `healthy` status
- [ ] `/docs` page loads with Swagger UI
- [ ] Successfully asked a question
- [ ] Got answer with sources
- [ ] Watched index grow over time
- [ ] Observed answer updates with new articles

## 🎓 What to Try Next

1. **Ask Different Questions**: Test various topics
2. **Monitor Growth**: Watch index size increase
3. **Check Performance**: Note response times
4. **Run Examples**: `python examples.py`
5. **Read Full Docs**: Explore advanced features
6. **Deploy to Cloud**: Try deployment options
7. **Customize**: Adapt for your use case

---

**Congratulations! You're now running a real-time RAG system! 🎉**

For more details, see the [full documentation](livenewsai/README.md).
