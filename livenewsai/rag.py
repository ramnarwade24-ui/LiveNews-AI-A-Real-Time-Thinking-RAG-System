"""
RAG (Retrieval Augmented Generation) engine for LiveNewsAI.
Handles document retrieval and LLM-based answer generation.
"""

import logging
import json
from typing import Optional
from datetime import datetime
from openai import OpenAI, OpenAIError
from .config import config

logger = logging.getLogger(__name__)


def _is_openai_rate_limited_error(exc: Exception) -> bool:
    """Return True when OpenAI is rate limited or quota-blocked.

    We keep this intentionally defensive because OpenAI SDK exception shapes can vary
    by version.
    """
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True

    message = str(exc).lower()
    if "error code: 429" in message or "http/1.1 429" in message:
        return True
    if "insufficient_quota" in message:
        return True
    if "exceeded your current quota" in message:
        return True

    return False

def _get_openai_client() -> Optional[OpenAI]:
    if not config.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=config.OPENAI_API_KEY)


class RAGEngine:
    """RAG engine for retrieving articles and generating answers."""

    def __init__(
        self,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        max_context_length: int = 3000,
    ):
        """
        Initialize RAG engine.

        Args:
            top_k: Number of top results to retrieve
            similarity_threshold: Minimum similarity score
            max_context_length: Maximum context length in characters
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.max_context_length = max_context_length

    def build_context(self, documents: list[dict]) -> tuple[str, list[str]]:
        """
        Build context from retrieved documents.

        Args:
            documents: List of retrieved document dictionaries

        Returns:
            Tuple of (context_text, source_urls)
        """
        context_parts = []
        source_urls = []
        current_length = 0

        for doc in documents:
            # Extract content
            content = doc.get("content") or doc.get("description") or ""
            title = doc.get("title", "Unknown")
            source = doc.get("source", "Unknown")
            published_at = doc.get("published_at", "")
            url = doc.get("url", "")

            # Format document
            doc_text = f"[{source} - {published_at}] {title}\n{content}"

            # Check length
            if current_length + len(doc_text) <= self.max_context_length:
                context_parts.append(doc_text)
                source_urls.append(url)
                current_length += len(doc_text)
            else:
                break

        context = "\n\n---\n\n".join(context_parts)
        return context, source_urls

    def extract_article_summaries(self, documents: list[dict]) -> list[str]:
        """Extract compact, human-readable summaries from retrieved documents."""
        summaries: list[str] = []
        for doc in documents:
            title = (doc.get("title") or "").strip() or "(untitled)"
            source = (doc.get("source") or "").strip() or "Unknown"
            published_at = (doc.get("published_at") or "").strip()
            description = (doc.get("description") or doc.get("content") or "").strip()

            description = " ".join(description.split())
            if len(description) > 240:
                description = description[:237] + "..."

            prefix = f"[{source}{' - ' + published_at if published_at else ''}] {title}"
            summaries.append(f"{prefix} — {description}" if description else prefix)
        return summaries

    def generate_answer(
        self,
        question: str,
        context: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate answer using LLM with RAG context.

        Args:
            question: User question
            context: Retrieved context from documents
            model: LLM model to use
            temperature: LLM temperature parameter
            max_tokens: Maximum tokens in response

        Returns:
            Generated answer
        """
        if not context:
            return "No relevant articles found to answer your question."

        system_prompt = """You are a helpful news assistant. Answer user questions based on the provided news articles.
Always cite the sources and dates of the articles you reference.
If you cannot answer based on the provided articles, say so clearly.
Keep your answer concise but informative."""

        user_prompt = f"""Based on the following news articles, please answer the question.

News Articles:
{context}

Question: {question}

Please provide a well-reasoned answer citing specific articles when relevant."""

        try:
            logger.info(f"Generating answer for question: {question}")

            client = _get_openai_client()
            if client is None:
                return "OpenAI API key is not configured. Set OPENAI_API_KEY to enable answer generation."

            response = client.chat.completions.create(
                model=(model or config.LLM_MODEL),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            answer = (response.choices[0].message.content or "").strip()
            logger.info("Answer generated successfully")
            return answer

        except OpenAIError as e:
            # Let the caller decide whether to fallback or surface an error.
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in answer generation: {e}")
            raise

    def answer_question(
        self,
        question: str,
        retrieved_documents: list[dict],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> dict:
        """
        Answer a user question using retrieved documents.

        Args:
            question: User question
            retrieved_documents: List of retrieved documents from vector index
            model: Optional model override
            temperature: Optional temperature override

        Returns:
            Dictionary with answer, sources, and metadata
        """
        model = model or config.LLM_MODEL
        temperature = temperature or config.LLM_TEMPERATURE

        # Build context from documents
        context, source_urls = self.build_context(retrieved_documents)

        note = "AI model temporarily unavailable — showing retrieved news context."

        try:
            # Generate answer
            answer = self.generate_answer(
                question=question,
                context=context,
                model=model,
                temperature=temperature,
                max_tokens=config.LLM_MAX_TOKENS,
            )

            result = {
                "question": question,
                "answer": answer,
                "sources": source_urls,
                "num_documents": len(retrieved_documents),
                "timestamp": datetime.utcnow().isoformat(),
            }

            return result
        except OpenAIError as e:
            if not _is_openai_rate_limited_error(e):
                # Preserve existing behavior shape (still return answer string)
                return {
                    "question": question,
                    "answer": f"Error generating answer: {str(e)}",
                    "sources": source_urls,
                    "num_documents": len(retrieved_documents),
                    "timestamp": datetime.utcnow().isoformat(),
                }

            summaries = self.extract_article_summaries(retrieved_documents)
            return {
                "question": question,
                "answer": note,
                "article_summaries": summaries,
                "sources": source_urls,
                "num_documents": len(retrieved_documents),
                "timestamp": datetime.utcnow().isoformat(),
                "ai_status": "rate_limited",
                "note": note,
            }

        except Exception as e:
            return {
                "question": question,
                "answer": f"Error generating answer: {str(e)}",
                "sources": source_urls,
                "num_documents": len(retrieved_documents),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global RAG engine instance
rag_engine = RAGEngine(
    top_k=config.TOP_K_RESULTS,
    similarity_threshold=config.SIMILARITY_THRESHOLD,
    max_context_length=config.MAX_CONTEXT_LENGTH,
)
