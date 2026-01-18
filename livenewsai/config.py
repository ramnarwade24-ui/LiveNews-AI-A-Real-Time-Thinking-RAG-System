"""Configuration module for LiveNewsAI.

Loads environment variables (including from a repo-root `.env`) and exposes a
typed configuration object.
"""

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def _load_env() -> None:
    """Load environment variables from repo-root `.env` if present.

    Does not override already-exported environment variables.
    """
    repo_root = Path(__file__).resolve().parents[1]
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)


def _normalize_llm_model(model: str) -> str:
    """Normalize/deprecate old OpenAI chat model names.

    Keeps the app runnable even if an older model name is provided via env.
    """
    deprecated_to_supported = {
        "gpt-4-turbo": "gpt-4o-mini",
        "gpt-3.5-turbo": "gpt-4o-mini",
    }

    normalized = (model or "").strip()
    if not normalized:
        return "gpt-4o-mini"
    if normalized in deprecated_to_supported:
        logger.warning(
            "LLM_MODEL '%s' is deprecated; using '%s' instead.",
            normalized,
            deprecated_to_supported[normalized],
        )
        return deprecated_to_supported[normalized]
    return normalized


@dataclass
class Config:
    """Configuration for LiveNewsAI system."""

    # API Keys
    NEWS_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: Optional[str] = None

    # News API Settings
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    NEWS_POLLING_INTERVAL: int = 60  # seconds
    NEWS_BATCH_SIZE: int = 20  # articles per fetch
    NEWS_LANGUAGE: str = "en"
    NEWS_SORT_BY: str = "publishedAt"  # or 'popularity', 'relevancy'

    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"  # OpenAI model
    EMBEDDING_DIMENSION: int = 1536
    BATCH_EMBEDDING_SIZE: int = 100  # batch process embeddings

    # Vector Search
    VECTOR_INDEX_TYPE: str = "knn"  # k-nearest neighbors
    TOP_K_RESULTS: int = 5  # retrieve top-k articles
    SIMILARITY_THRESHOLD: float = 0.7

    # LLM Settings
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1024

    # Server Settings
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    FASTAPI_RELOAD: bool = True

    # Pathway Settings
    PATHWAY_PERSISTENCE_PATH: str = "/tmp/livenewsai"
    PATHWAY_LOG_LEVEL: str = "INFO"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Context window
    MAX_CONTEXT_LENGTH: int = 3000  # max chars for RAG context
    ARTICLE_RETENTION_DAYS: int = 7  # keep articles for 7 days

    def __post_init__(self):
        """Validate configuration after initialization."""
        _load_env()

        # Populate from environment after loading dotenv
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY", self.NEWS_API_KEY)
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", self.OPENAI_API_KEY)
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", self.GEMINI_API_KEY)

        self.FASTAPI_HOST = os.getenv("FASTAPI_HOST", self.FASTAPI_HOST)
        self.FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", str(self.FASTAPI_PORT)))
        self.FASTAPI_RELOAD = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"

        self.PATHWAY_PERSISTENCE_PATH = os.getenv(
            "PATHWAY_PERSISTENCE_PATH", self.PATHWAY_PERSISTENCE_PATH
        )
        self.PATHWAY_LOG_LEVEL = os.getenv("PATHWAY_LOG_LEVEL", self.PATHWAY_LOG_LEVEL)

        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL)
        self.MAX_CONTEXT_LENGTH = int(
            os.getenv("MAX_CONTEXT_LENGTH", str(self.MAX_CONTEXT_LENGTH))
        )
        self.ARTICLE_RETENTION_DAYS = int(
            os.getenv("ARTICLE_RETENTION_DAYS", str(self.ARTICLE_RETENTION_DAYS))
        )
        self.NEWS_POLLING_INTERVAL = int(
            os.getenv("NEWS_POLLING_INTERVAL", str(self.NEWS_POLLING_INTERVAL))
        )
        self.NEWS_BATCH_SIZE = int(os.getenv("NEWS_BATCH_SIZE", str(self.NEWS_BATCH_SIZE)))
        self.NEWS_LANGUAGE = os.getenv("NEWS_LANGUAGE", self.NEWS_LANGUAGE)
        self.NEWS_SORT_BY = os.getenv("NEWS_SORT_BY", self.NEWS_SORT_BY)
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", self.EMBEDDING_MODEL)
        self.BATCH_EMBEDDING_SIZE = int(
            os.getenv("BATCH_EMBEDDING_SIZE", str(self.BATCH_EMBEDDING_SIZE))
        )
        self.TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", str(self.TOP_K_RESULTS)))
        self.SIMILARITY_THRESHOLD = float(
            os.getenv("SIMILARITY_THRESHOLD", str(self.SIMILARITY_THRESHOLD))
        )
        # Default to a currently supported model; allow override via env.
        self.LLM_MODEL = _normalize_llm_model(os.getenv("LLM_MODEL", "gpt-4o-mini"))
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", str(self.LLM_TEMPERATURE)))
        self.LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", str(self.LLM_MAX_TOKENS)))

        if not self.NEWS_API_KEY:
            logger.warning("NEWS_API_KEY not set. News ingestion will fail.")

        if not self.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. Embeddings and LLM will fail.")

        # Create persistence directory
        os.makedirs(self.PATHWAY_PERSISTENCE_PATH, exist_ok=True)

    def to_dict(self):
        """Convert configuration to dictionary."""
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }


# Global config instance
config = Config()
