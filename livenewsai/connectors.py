"""
News API connector for Pathway.
Implements a custom Pathway connector to stream articles from NewsAPI.
"""

import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Any, Iterator, Optional
from dataclasses import dataclass
from .config import config

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Article data structure."""

    source: str
    author: Optional[str]
    title: str
    description: Optional[str]
    content: Optional[str]
    url: str
    image_url: Optional[str]
    published_at: str
    fetched_at: str


class NewsAPIConnector:
    """
    Custom connector to stream news articles from NewsAPI.
    Polls the API at regular intervals and yields new articles.
    """

    def __init__(
        self,
        api_key: str,
        polling_interval: int = 60,
        batch_size: int = 20,
        language: str = "en",
        sort_by: str = "publishedAt",
    ):
        """
        Initialize NewsAPIConnector.

        Args:
            api_key: NewsAPI API key
            polling_interval: Polling interval in seconds
            batch_size: Number of articles per API call
            language: News language code
            sort_by: Sort articles by 'publishedAt', 'popularity', or 'relevancy'
        """
        self.api_key = api_key
        self.polling_interval = polling_interval
        self.batch_size = batch_size
        self.language = language
        self.sort_by = sort_by
        self.base_url = config.NEWS_API_BASE_URL
        self.seen_urls = set()
        self.last_fetch_time = None

    def _fetch_articles(self, search_query: str = "technology") -> list[dict]:
        """
        Fetch articles from NewsAPI.

        Args:
            search_query: Search query for articles

        Returns:
            List of article dictionaries
        """
        url = f"{self.base_url}/everything"

        # Calculate time range
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=config.ARTICLE_RETENTION_DAYS)

        params = {
            "q": search_query,
            "sortBy": self.sort_by,
            "language": self.language,
            "pageSize": self.batch_size,
            "apiKey": self.api_key,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }

        try:
            logger.info(f"Fetching articles with query: {search_query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []

            articles = data.get("articles", [])
            logger.info(f"Fetched {len(articles)} articles")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch articles: {e}")
            return []

    def _parse_article(self, article_dict: dict) -> Optional[Article]:
        """
        Parse article dictionary to Article object.

        Args:
            article_dict: Article dictionary from NewsAPI

        Returns:
            Article object or None if invalid
        """
        try:
            # Skip if URL already processed
            url = article_dict.get("url", "")
            if url in self.seen_urls:
                return None
            self.seen_urls.add(url)

            article = Article(
                source=article_dict.get("source", {}).get("name", "Unknown"),
                author=article_dict.get("author"),
                title=article_dict.get("title", ""),
                description=article_dict.get("description"),
                content=article_dict.get("content"),
                url=url,
                image_url=article_dict.get("urlToImage"),
                published_at=article_dict.get("publishedAt", ""),
                fetched_at=datetime.utcnow().isoformat(),
            )

            return article if article.title else None

        except Exception as e:
            logger.error(f"Failed to parse article: {e}")
            return None

    def stream(
        self, search_queries: Optional[list[str]] = None
    ) -> Iterator[tuple[str, Any]]:
        """
        Stream articles continuously from NewsAPI.

        Args:
            search_queries: List of search queries to rotate through

        Yields:
            Tuples of (article_id, article_data)
        """
        if search_queries is None:
            search_queries = [
                "technology",
                "business",
                "health",
                "science",
                "entertainment",
            ]

        query_index = 0
        article_id = 0

        logger.info("Starting NewsAPI stream")

        while True:
            try:
                # Rotate through search queries
                query = search_queries[query_index % len(search_queries)]
                query_index += 1

                # Fetch articles
                articles_data = self._fetch_articles(query)

                # Parse and yield articles
                new_articles_count = 0
                for article_dict in articles_data:
                    article = self._parse_article(article_dict)
                    if article:
                        article_id += 1
                        yield (str(article_id), article.__dict__)
                        new_articles_count += 1

                if new_articles_count > 0:
                    logger.info(f"Streamed {new_articles_count} new articles")

                # Wait before next poll
                logger.debug(f"Waiting {self.polling_interval}s before next poll")
                time.sleep(self.polling_interval)

            except KeyboardInterrupt:
                logger.info("Stream interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in stream: {e}")
                time.sleep(self.polling_interval)


def create_news_connector(
    api_key: Optional[str] = None,
) -> NewsAPIConnector:
    """
    Factory function to create NewsAPIConnector.

    Args:
        api_key: Optional API key override

    Returns:
        NewsAPIConnector instance
    """
    api_key = api_key or config.NEWS_API_KEY
    if not api_key:
        raise ValueError("NEWS_API_KEY not set in environment or config")

    return NewsAPIConnector(
        api_key=api_key,
        polling_interval=config.NEWS_POLLING_INTERVAL,
        batch_size=config.NEWS_BATCH_SIZE,
        language=config.NEWS_LANGUAGE,
        sort_by=config.NEWS_SORT_BY,
    )
