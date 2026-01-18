"""
Pathway streaming pipeline for LiveNewsAI.
Handles real-time ingestion, embeddings, and vector indexing.
"""

import logging
import asyncio
import numpy as np
from datetime import datetime
from typing import Optional, Any
from openai import OpenAI, OpenAIError
import pathway as pw
from .config import config
from .connectors import create_news_connector

logger = logging.getLogger(__name__)

def _get_openai_client() -> Optional[OpenAI]:
    if not config.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=config.OPENAI_API_KEY)


class EmbeddingProcessor:
    """Handles embedding generation for articles."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        batch_size: int = 100,
    ):
        """
        Initialize embedding processor.

        Args:
            model: Embedding model name
            batch_size: Batch size for embedding requests
        """
        self.model = model
        self.batch_size = batch_size
        self.cache = {}  # Simple cache for embeddings
        self._client: Optional[OpenAI] = None

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        # Check cache
        text_hash = hash(text)
        if text_hash in self.cache:
            return self.cache[text_hash]

        try:
            if self._client is None:
                self._client = _get_openai_client()
            if self._client is None:
                raise RuntimeError("OPENAI_API_KEY is not configured")

            # Prepare text
            text = text.replace("\n", " ")[:8191]  # OpenAI max length

            # Get embedding
            response = self._client.embeddings.create(input=text, model=self.model)
            embedding = response.data[0].embedding

            # Cache result
            self.cache[text_hash] = embedding

            return embedding

        except OpenAIError as e:
            logger.error(f"Failed to get embedding: {e}")
            # Return zero vector on error
            return [0.0] * config.EMBEDDING_DIMENSION
        except Exception as e:
            logger.error(f"Unexpected error in embedding: {e}")
            return [0.0] * config.EMBEDDING_DIMENSION

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text))
        return embeddings


class VectorIndex:
    """In-memory vector index for KNN search."""

    def __init__(self, dimension: int = 1536):
        """
        Initialize vector index.

        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        self.vectors = {}  # id -> embedding vector
        self.documents = {}  # id -> document data
        self.ids = []  # ordered list of IDs

    def add(self, doc_id: str, embedding: list[float], document: dict):
        """
        Add document to index.

        Args:
            doc_id: Document ID
            embedding: Embedding vector
            document: Document data
        """
        self.vectors[doc_id] = np.array(embedding)
        self.documents[doc_id] = document
        if doc_id not in self.ids:
            self.ids.append(doc_id)
        logger.debug(f"Added document {doc_id} to vector index")

    def search(self, query_embedding: list[float], k: int = 5) -> list[tuple[str, float]]:
        """
        Search for similar documents using KNN.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return

        Returns:
            List of (doc_id, similarity_score) tuples
        """
        if not self.vectors:
            return []

        query_vector = np.array(query_embedding)

        # Compute similarities
        similarities = []
        for doc_id in self.ids:
            doc_vector = self.vectors[doc_id]
            # Cosine similarity
            similarity = np.dot(query_vector, doc_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(doc_vector) + 1e-10
            )
            similarities.append((doc_id, similarity))

        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def get_documents(self, doc_ids: list[str]) -> list[dict]:
        """
        Get documents by IDs.

        Args:
            doc_ids: List of document IDs

        Returns:
            List of documents
        """
        return [self.documents[doc_id] for doc_id in doc_ids if doc_id in self.documents]

    def size(self) -> int:
        """Get number of documents in index."""
        return len(self.vectors)


# Global instances
embedding_processor = EmbeddingProcessor(
    model=config.EMBEDDING_MODEL,
    batch_size=config.BATCH_EMBEDDING_SIZE,
)

vector_index = VectorIndex(dimension=config.EMBEDDING_DIMENSION)


def create_pathway_pipeline():
    """
    Create and configure Pathway streaming pipeline.

    Returns:
        Configured Pathway schema and processing logic
    """

    class Article(pw.Schema):
        """Pathway schema for articles."""

        source: str
        author: Optional[str]
        title: str
        description: Optional[str]
        content: Optional[str]
        url: str
        image_url: Optional[str]
        published_at: str
        fetched_at: str

    class ProcessedArticle(pw.Schema):
        """Schema for processed articles (used for retrieval and context)."""

        source: str
        title: str
        url: str
        published_at: str
        description: Optional[str]
        content: Optional[str]
        content_text: str

    try:
        logger.info("Initializing NewsAPI connector")
        connector = create_news_connector()

        class NewsAPISubject(pw.io.python.ConnectorSubject):
            def run(self) -> None:
                for _, article in connector.stream():
                    # Article dict is already normalized in connectors.py
                    self.next(**article)

            @property
            def _deletions_enabled(self) -> bool:
                return False

        # Create Pathway table from streaming connector
        logger.info("Creating Pathway table from news stream")
        articles = pw.io.python.read(
            NewsAPISubject(),
            schema=Article,
            name="articles",
        )

        processed = articles.select(
            source=pw.this.source,
            title=pw.this.title,
            url=pw.this.url,
            published_at=pw.this.published_at,
            description=pw.this.description,
            content=pw.this.content,
            content_text=pw.apply(
                lambda title, description, content: (
                    f"{title}. {(description or '')} {(content or '')}".replace("\n", " ")
                )[:1000],
                pw.this.title,
                pw.this.description,
                pw.this.content,
            ),
        )

        # Add embeddings (this would be called for each new article)
        def add_embeddings_callback(key, row, time, is_addition):
            """Callback to add embeddings when articles arrive."""
            if not is_addition:
                return
            try:
                embedding = embedding_processor.get_embedding(row["content_text"])
                doc_id = row.get("url") or str(key)
                vector_index.add(doc_id, embedding, row)
                logger.info(f"Added article {doc_id} with embedding to vector index")
            except Exception as e:
                logger.error(f"Error adding embedding for article {key}: {e}")

        # Subscribe to processed articles
        pw.io.subscribe(processed, add_embeddings_callback)

        logger.info("Pathway pipeline created successfully")
        return processed

    except Exception as e:
        logger.error(f"Failed to create Pathway pipeline: {e}")
        raise


def run_pathway_pipeline():
    """
    Run the Pathway pipeline.
    This is a blocking call that continuously processes incoming articles.
    """
    try:
        logger.info("Starting Pathway pipeline")
        pipeline = create_pathway_pipeline()

        # Run the pipeline
        pw.run(monitoring_level=pw.MonitoringLevel.NONE)

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        raise


async def query_vector_index(query_text: str, k: int = 5) -> list[dict]:
    """
    Query the vector index for similar documents.

    Args:
        query_text: Query text
        k: Number of results to return

    Returns:
        List of matching documents
    """
    try:
        # Get embedding for query
        query_embedding = embedding_processor.get_embedding(query_text)

        # Search vector index
        results = vector_index.search(query_embedding, k=k)

        # Get documents
        doc_ids = [doc_id for doc_id, _ in results]
        documents = vector_index.get_documents(doc_ids)

        logger.info(f"Vector index search returned {len(documents)} documents")
        return documents

    except Exception as e:
        logger.error(f"Error querying vector index: {e}")
        return []


def get_index_stats() -> dict:
    """
    Get statistics about the vector index.

    Returns:
        Dictionary with index statistics
    """
    return {
        "total_documents": vector_index.size(),
        "embedding_dimension": config.EMBEDDING_DIMENSION,
        "embedding_model": config.EMBEDDING_MODEL,
    }
