LiveNewsAI — Real-Time Streaming RAG System for Breaking News

🚀 Production-grade real-time Retrieval Augmented Generation (RAG) system built with Pathway that continuously ingests breaking news and answers questions using the latest articles — without requiring restarts or re-indexing.

Live AI — Answers update automatically as new articles arrive. No batch processing. No manual re-indexing.

🎥 Hackathon Live Demo

Live Swagger UI (GitHub Codespaces):
https://curly-umbrella-4j5x7vp6pxvqcjrj-8000.app.github.dev/docs

Health Check:
https://curly-umbrella-4j5x7vp6pxvqcjrj-8000.app.github.dev/health

Example Query:

"What are today's top business headlines?"

The system demonstrates:

Real-time ingestion

Streaming vector indexing

Live retrieval

RAG pipeline execution

✨ Key Features

Real-Time Streaming — Continuously ingests news from NewsAPI every 60 seconds

Dynamic Vector Index — Live KNN index updates automatically

RAG-Powered Answers — Questions answered using latest articles

Zero Downtime Updates — New articles indexed without restart

FastAPI REST API — Production-ready API with Swagger UI

Docker-Ready — One-command deployment

Fully Async — High concurrency support

Modular Architecture — Clean extensible codebase

⭐ Bonus Capabilities

Graceful AI Fallback — If OpenAI quota is unavailable, system still returns real-time retrieved news context, article summaries, and sources.

No-Credit Mode — Fully functional retrieval + indexing pipeline without OpenAI credits.

🏗️ Architecture
Live News Stream (NewsAPI)
        ↓
   Pathway Connector
        ↓
  Streaming Pipeline
        ↓
  Embeddings (OpenAI)
        ↓
  Real-Time Vector Index (KNN)
        ↓
   RAG Query Engine
        ↓
  LLM Answer Generation (GPT-4o-mini with fallback mode)
        ↓
   FastAPI REST API

🚀 Quick Start
Prerequisites

Python 3.10+ or Docker

NewsAPI key (free at https://newsapi.org
)

OpenAI API key (optional, only for AI summaries)

Local Setup
git clone https://github.com/ramnarwade24-ui/LiveNews-AI-A-Real-Time-Thinking-RAG-System
cd LiveNews-AI-A-Real-Time-Thinking-RAG-System

export NEWS_API_KEY="your-newsapi-key"

# Optional: only required for AI-generated answers
export OPENAI_API_KEY="your-openai-key"

bash quickstart.sh


Server runs at:
👉 http://localhost:8000

👉 Swagger UI: http://localhost:8000/docs

Docker Setup
export NEWS_API_KEY="your-newsapi-key"
export OPENAI_API_KEY="your-openai-key"   # optional

bash docker-quickstart.sh

📖 API Examples
Ask a Question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the latest AI breakthroughs?",
    "top_k": 5
  }'

Health Check
curl http://localhost:8000/health

Get Stats
curl http://localhost:8000/stats

🧠 Graceful Fallback Mode (No OpenAI Credits Required)

If OpenAI quota is unavailable, the system automatically switches to fallback mode:

{
  "answer": "AI model temporarily unavailable — showing retrieved news context.",
  "article_summaries": [...],
  "sources": [...],
  "ai_status": "rate_limited"
}


This allows full real-time RAG functionality without paid APIs.

📁 Project Structure

LiveNews-AI-A-Real-Time-Thinking-RAG-System/
│
├── livenewsai/ # Main application package
│ ├── app.py # FastAPI server
│ ├── pathway_pipeline.py # Pathway streaming pipeline
│ ├── connectors.py # NewsAPI connector
│ ├── rag.py # RAG query engine
│ ├── config.py # Configuration
│ ├── requirements.txt # Dependencies
│ └── test_livenewsai.py # Tests
│
├── Dockerfile # Docker image
├── docker-compose.yml # Multi-container setup
├── quickstart.sh # Local quick start
├── docker-quickstart.sh # Docker quick start
├── DEPLOYMENT.md # Deployment guide
├── .env.example # Environment template
└── README.md # Project documentation

🔧 Configuration
export NEWS_POLLING_INTERVAL=60
export NEWS_BATCH_SIZE=20
export EMBEDDING_MODEL=text-embedding-3-small
export TOP_K_RESULTS=5
export LLM_MODEL=gpt-4o-mini
export LOG_LEVEL=INFO

🛠️ Tech Stack
Component	Technology
Streaming	Pathway
Framework	FastAPI
Embeddings	OpenAI
LLM	GPT-4o-mini
Data	NewsAPI
Vector Index	In-Memory KNN
Server	Uvicorn
Container	Docker
🚦 API Endpoints
Method	Endpoint	Purpose
GET	/	API info
GET	/health	System status
POST	/ask	Ask question
GET	/stats	System statistics
GET	/articles	Recent articles
GET	/docs	Swagger UI
📊 Performance

Latency: <500ms

Streaming updates every 60 seconds

Index grows live without restart

Supports concurrent users

🧪 Testing
pytest livenewsai/test_livenewsai.py -v

📈 Monitoring
curl http://localhost:8000/health
curl http://localhost:8000/stats

📜 License

MIT License

🏁 Hackathon Readiness

✔ Real-time streaming
✔ Pathway pipeline
✔ RAG architecture
✔ Live demo
✔ Public GitHub repo
✔ API documentation
✔ Docker deployment
✔ Graceful failure handling

💡 Use Cases

Real-time news assistant

Market intelligence

AI-powered newsroom

Research monitoring

Breaking news summarizer

🤝 Team

Built for DataQuest 2026 – Team Megalith (IIT Kharagpur)
Hackathon Category: Real-Time Data Science & AI Systems

Made with ❤️ using Pathway, FastAPI, and OpenAI

Live Demo • Real-Time Streaming • Production Ready
