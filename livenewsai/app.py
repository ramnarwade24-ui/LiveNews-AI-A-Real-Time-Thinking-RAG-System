"""
FastAPI server for LiveNewsAI.
Exposes REST endpoints for querying the real-time RAG system.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from .config import config
from .pathway_pipeline import (
    run_pathway_pipeline,
    query_vector_index,
    get_index_stats,
    vector_index,
)
from .rag import rag_engine
import threading

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
)

# Global state
pathway_thread = None
pipeline_running = False


def start_pipeline_background():
    """Start Pathway pipeline in a background thread."""
    global pathway_thread, pipeline_running

    if pipeline_running:
        logger.warning("Pipeline is already running")
        return

    def run_pipeline():
        try:
            logger.info("Starting Pathway pipeline thread")
            run_pathway_pipeline()
        except Exception as e:
            logger.error(f"Pipeline thread error: {e}")

    pathway_thread = threading.Thread(target=run_pipeline, daemon=True)
    pathway_thread.start()
    pipeline_running = True
    logger.info("Pipeline background thread started")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting LiveNewsAI application")
    start_pipeline_background()
    yield
    # Shutdown
    logger.info("Shutting down LiveNewsAI application")
    global pipeline_running
    pipeline_running = False


# Initialize FastAPI app
app = FastAPI(
    title="LiveNewsAI",
    description="Real-time RAG system for breaking news",
    version="1.0.0",
    lifespan=lifespan,
)


# Request/Response models
class AskRequest(BaseModel):
    """Request model for ask endpoint."""

    question: str = Field(..., description="Question to ask about news")
    top_k: int = Field(5, description="Number of articles to retrieve", ge=1, le=20)


class AskResponse(BaseModel):
    """Response model for ask endpoint."""

    question: str
    answer: str
    sources: list[str] = Field(default_factory=list)
    article_summaries: list[str] = Field(
        default_factory=list,
        description=(
            "Extracted summaries of retrieved articles (used when AI is temporarily unavailable)."
        ),
    )
    num_documents: int
    timestamp: str
    index_size: int
    ai_status: Optional[str] = Field(
        default=None,
        description="AI status indicator (e.g. 'rate_limited' when OpenAI is unavailable).",
    )
    note: Optional[str] = Field(
        default=None,
        description="Additional note shown when AI model is unavailable.",
    )


class HealthResponse(BaseModel):
    """Response model for health endpoint."""

    status: str
    pipeline_running: bool
    index_size: int
    index_stats: dict
    timestamp: str


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns system status and index information.
    """
    try:
        stats = get_index_stats()
        return HealthResponse(
            status="healthy",
            pipeline_running=pipeline_running,
            index_size=vector_index.size(),
            index_stats=stats,
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            pipeline_running=pipeline_running,
            index_size=0,
            index_stats={},
            timestamp=datetime.utcnow().isoformat(),
        )


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Ask a question about the latest news.
    Uses real-time RAG to answer based on current articles.

    Args:
        request: Ask request with question and optional top_k

    Returns:
        AskResponse with answer, sources, and metadata
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        if vector_index.size() == 0:
            raise HTTPException(
                status_code=503,
                detail="Vector index is empty. Pipeline may still be initializing.",
            )

        logger.info(f"Processing question: {request.question}")

        # Query vector index
        retrieved_documents = await query_vector_index(request.question, k=request.top_k)

        if not retrieved_documents:
            raise HTTPException(
                status_code=404,
                detail="No relevant articles found",
            )

        # Generate answer using RAG
        result = rag_engine.answer_question(
            question=request.question,
            retrieved_documents=retrieved_documents,
        )

        # Format response
        response = AskResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            article_summaries=result.get("article_summaries", []),
            num_documents=result["num_documents"],
            timestamp=result["timestamp"],
            index_size=vector_index.size(),
            ai_status=result.get("ai_status"),
            note=result.get("note"),
        )

        logger.info(f"Question answered successfully. Sources: {len(result['sources'])}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/stats")
async def get_stats():
    """
    Get statistics about the RAG system.

    Returns:
        Dictionary with system statistics
    """
    try:
        stats = get_index_stats()
        return {
            "index_size": vector_index.size(),
            "embedding_dimension": stats["embedding_dimension"],
            "embedding_model": stats["embedding_model"],
            "pipeline_running": pipeline_running,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/articles")
async def list_articles(limit: int = Query(10, ge=1, le=100)):
    """
    List recently indexed articles.

    Args:
        limit: Maximum number of articles to return

    Returns:
        List of articles with metadata
    """
    try:
        # Get latest articles from index
        article_ids = vector_index.ids[-limit:]
        articles = vector_index.get_documents(article_ids)

        return {
            "count": len(articles),
            "articles": articles,
        }
    except Exception as e:
        logger.error(f"Error listing articles: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "LiveNewsAI",
        "version": "1.0.0",
        "description": "Real-time RAG system for breaking news",
        "endpoints": {
            "GET /health": "Health check and system status",
            "POST /ask": "Ask a question about the latest news",
            "GET /stats": "Get system statistics",
            "GET /articles": "List recently indexed articles",
            "GET /docs": "Interactive API documentation",
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting FastAPI server on {config.FASTAPI_HOST}:{config.FASTAPI_PORT}")
    uvicorn.run(
        app,
        host=config.FASTAPI_HOST,
        port=config.FASTAPI_PORT,
        reload=config.FASTAPI_RELOAD,
        log_level=config.LOG_LEVEL.lower(),
    )
