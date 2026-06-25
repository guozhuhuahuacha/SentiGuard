"""GDELT DOC 2.0 client.

The DOC API is a free, key-less endpoint that returns JSON metadata for
articles indexed by GDELT.  Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

Quirks worth knowing:
  * `maxrecords` is hard-capped at 250 per call.
  * `timespan` accepts e.g. "15min", "24h", "3d" (max ~7d for ArtList).
  * The endpoint returns 200 with HTML on bad queries, so we always parse JSON
    defensively and surface a clear error.
  * Dates returned as `seendate` are formatted "YYYYMMDDTHHMMSSZ".
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Iterator, List, Optional

import requests

from .base import BaseDataSource

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GDELT DOC 2.0 配置（支持环境变量覆盖）
# ---------------------------------------------------------------------------
GDELT_DOC_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_DEFAULT_QUERY = os.environ.get("GDELT_DEFAULT_QUERY", "sourcelang:chinese")
GDELT_DEFAULT_TIMESPAN = os.environ.get("GDELT_DEFAULT_TIMESPAN", "24h")
GDELT_MAX_RECORDS_PER_CALL = 250  # API hard cap
GDELT_REQUEST_TIMEOUT = 30
GDELT_RETRY_ATTEMPTS = 3
GDELT_RETRY_BACKOFF = 2.0  # seconds, exponential
GDELT_MIN_INTERVAL = float(os.environ.get("GDELT_MIN_INTERVAL", "5.5"))
GDELT_USER_AGENT = "SentiGuard-HotTopic/0.1 (+research)"


def _parse_seendate(s: str) -> str:
    """GDELT 'YYYYMMDDTHHMMSSZ' -> ISO 8601 UTC, or '' on failure."""
    if not s:
        return ""
    try:
        dt = datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except ValueError:
        return s  # keep raw if format unexpected


class GDELTClient(BaseDataSource):
    """Client for the GDELT DOC 2.0 ArtList endpoint."""

    name = "gdelt"

    def __init__(
        self,
        endpoint: str = GDELT_DOC_ENDPOINT,
        timeout: int = GDELT_REQUEST_TIMEOUT,
        retry_attempts: int = GDELT_RETRY_ATTEMPTS,
        retry_backoff: float = GDELT_RETRY_BACKOFF,
        min_interval: float = GDELT_MIN_INTERVAL,
        user_agent: str = GDELT_USER_AGENT,
    ):
        self.endpoint = endpoint
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_backoff = retry_backoff
        self.min_interval = min_interval
        self._last_request_ts: float = 0.0
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    # ------------------------------------------------------------------
    # low-level
    # ------------------------------------------------------------------
    def _throttle(self) -> None:
        """Sleep so consecutive requests respect GDELT's ~1 req / 5 s limit."""
        if self.min_interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request_ts
        wait = self.min_interval - elapsed
        if wait > 0:
            logger.debug("throttle: sleeping %.2fs to respect rate limit", wait)
            time.sleep(wait)

    def _request(self, params: dict) -> dict:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retry_attempts + 1):
            self._throttle()
            try:
                r = self.session.get(self.endpoint, params=params, timeout=self.timeout)
                self._last_request_ts = time.monotonic()
                if r.status_code == 429:
                    wait = max(self.min_interval * 2, self.retry_backoff * (2 ** attempt))
                    logger.warning(
                        "GDELT 429 rate-limited (attempt %d/%d); sleeping %.1fs",
                        attempt, self.retry_attempts, wait,
                    )
                    last_exc = RuntimeError("HTTP 429 Too Many Requests")
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                ctype = r.headers.get("content-type", "")
                if "json" not in ctype.lower():
                    snippet = r.text[:200].replace("\n", " ")
                    raise ValueError(
                        f"GDELT returned non-JSON (content-type={ctype}): {snippet}"
                    )
                return r.json()
            except (requests.RequestException, ValueError, json.JSONDecodeError) as e:
                self._last_request_ts = time.monotonic()
                last_exc = e
                wait = self.retry_backoff * (2 ** (attempt - 1))
                logger.warning(
                    "GDELT request failed (attempt %d/%d): %s; retrying in %.1fs",
                    attempt, self.retry_attempts, e, wait,
                )
                time.sleep(wait)
        raise RuntimeError(f"GDELT request failed after retries: {last_exc}")

    def fetch_articles(
        self,
        query: str = GDELT_DEFAULT_QUERY,
        timespan: str = GDELT_DEFAULT_TIMESPAN,
        max_records: int = GDELT_MAX_RECORDS_PER_CALL,
        sort: str = "datedesc",
    ) -> List[dict]:
        """Single ArtList call.  Returns the raw `articles` list (possibly empty)."""
        max_records = min(max_records, GDELT_MAX_RECORDS_PER_CALL)
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "timespan": timespan,
            "maxrecords": max_records,
            "sort": sort,
        }
        data = self._request(params)
        articles = data.get("articles", []) or []
        logger.info(
            "GDELT query=%r timespan=%s -> %d articles",
            query, timespan, len(articles),
        )
        return articles

    # ------------------------------------------------------------------
    # BaseDataSource
    # ------------------------------------------------------------------
    def iter_docs(
        self,
        query: str = GDELT_DEFAULT_QUERY,
        timespan: str = GDELT_DEFAULT_TIMESPAN,
        max_records: int = GDELT_MAX_RECORDS_PER_CALL,
        sort: str = "datedesc",
    ) -> Iterator[dict]:
        articles = self.fetch_articles(
            query=query,
            timespan=timespan,
            max_records=max_records,
            sort=sort,
        )
        for i, art in enumerate(articles):
            url = art.get("url", "")
            title = (art.get("title") or "").strip()
            if not title and not url:
                continue
            yield {
                "doc_id": f"gdelt-{art.get('seendate', '')}-{i:04d}",
                "title": title,
                "content": title,  # placeholder = title; enrich pipeline can fill
                "publish_time": _parse_seendate(art.get("seendate", "")),
                "source": "gdelt",
                "url": url,
                "lang": (art.get("language") or "").lower()[:2] or "zh",
                "category": art.get("sourcecountry", ""),
            }
