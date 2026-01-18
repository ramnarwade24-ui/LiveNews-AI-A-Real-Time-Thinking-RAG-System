"""
LiveNewsAI - Real-Time RAG System for Breaking News

A production-grade streaming RAG system that continuously ingests breaking news
and answers questions using the latest articles without restarts or re-indexing.
"""

__version__ = "1.0.0"
__author__ = "LiveNewsAI Contributors"
__license__ = "MIT"

from .config import config
from .connectors import create_news_connector
from .pathway_pipeline import query_vector_index, get_index_stats
from .rag import rag_engine

__all__ = [
    "config",
    "create_news_connector",
    "query_vector_index",
    "get_index_stats",
    "rag_engine",
]
