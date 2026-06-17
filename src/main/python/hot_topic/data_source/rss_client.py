"""RSS/Atom feed client.

Usage:
    client = RSSClient()
    df = client.to_dataframe(urls=[
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ])
"""
from __future__ import annotations

import logging
import hashlib
from datetime import datetime, timezone
from typing import Iterator, List, Optional
from urllib.parse import urlparse

import requests

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

from .. import config
from .base import BaseDataSource

logger = logging.getLogger(__name__)

# Default RSS feeds - some popular Chinese/English news sources
DEFAULT_FEEDS = [
    # Chinese news
    "https://news.qq.com/news/rss/news.xml",
    "https://rss.sina.com.cn/news/tech.xml",
    # English news
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]


def _parse_feed_time(entry) -> str:
    """Parse feed entry time to ISO 8601 UTC."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()
    return ""


def _get_id(url: str, entry) -> str:
    """Generate a stable doc_id from feed entry."""
    content = f"{url}:{getattr(entry, 'id', '')}:{getattr(entry, 'link', '')}:{getattr(entry, 'title', '')}"
    return f"rss_{hashlib.md5(content.encode()).hexdigest()[:12]}"


def _get_content(entry) -> str:
    """Extract best available content from entry."""
    if hasattr(entry, "summary") and entry.summary:
        return entry.summary
    if hasattr(entry, "description") and entry.description:
        return entry.description
    if hasattr(entry, "title") and entry.title:
        return entry.title
    return ""


def _guess_language(entry, feed_url: str) -> str:
    """Guess language from entry or feed URL."""
    # First check feed URL for known sources
    url_lower = feed_url.lower()
    if "bbc.co.uk" in url_lower or "nytimes.com" in url_lower or "reuters.com" in url_lower:
        return "en"
    if "qq.com" in url_lower or "sina.com.cn" in url_lower or "ifeng.com" in url_lower or "xinhuanet.com" in url_lower:
        return "zh"

    # Then check entry language
    if hasattr(entry, "language") and entry.language:
        lang = entry.language.lower()
        if "zh" in lang or "cn" in lang or "chinese" in lang:
            return "zh"
        if "en" in lang or "english" in lang:
            return "en"

    # Try to guess from title/content (simple check for Chinese characters)
    sample = ""
    if hasattr(entry, "title"):
        sample = entry.title
    if not sample and hasattr(entry, "summary"):
        sample = entry.summary

    # Check for Chinese Unicode range
    if sample:
        for char in sample[:100]:
            if '一' <= char <= '鿿':
                return "zh"
        return "en"

    return "zh"  # default to Chinese


class RSSClient(BaseDataSource):
    """RSS/Atom feed client."""

    name = "rss"

    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "SentiGuard-RSS/0.1 (+research)",
    ):
        if not HAS_FEEDPARSER:
            raise ImportError(
                "feedparser is required for RSSClient. "
                "Install with: pip install feedparser"
            )
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch_feed(self, url: str) -> List[dict]:
        """Fetch and parse a single RSS/Atom feed."""
        logger.info(f"Fetching feed: {url}")
        try:
            # First try using feedparser directly
            d = feedparser.parse(url)
            if d.bozo and d.bozo_exception:
                logger.warning(f"Feed parse warning for {url}: {d.bozo_exception}")

            entries = d.entries
            logger.info(f"Got {len(entries)} entries from {url}")
            return entries

        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return []

    def iter_docs(
        self,
        urls: Optional[List[str]] = None,
        max_per_feed: int = 50,
        **kwargs,
    ) -> Iterator[dict]:
        """Iterate over documents from RSS feeds."""
        if urls is None:
            urls = DEFAULT_FEEDS

        for url in urls:
            entries = self.fetch_feed(url)
            for i, entry in enumerate(entries[:max_per_feed]):
                doc_id = _get_id(url, entry)
                title = getattr(entry, "title", "").strip()
                content = _get_content(entry)
                publish_time = _parse_feed_time(entry)
                link = getattr(entry, "link", "")
                lang = _guess_language(entry, url)

                # Try to get category/source
                category = ""
                if hasattr(entry, "tags") and entry.tags:
                    category = entry.tags[0].get("term", "")

                yield {
                    "doc_id": doc_id,
                    "title": title,
                    "content": content,
                    "publish_time": publish_time,
                    "source": "rss",
                    "url": link,
                    "lang": lang,
                    "category": category,
                }
