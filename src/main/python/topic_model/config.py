"""Configuration for topic_model module.

Centralizes all paths and parameters so they can be overridden via
environment variables without touching code.

Note: data source API configs are now self-contained in providers/data/.
This file retains them as convenience re-exports for scripts backward compat.
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# repo root: SentiGuard/  (topic_model -> python -> main -> src -> SentiGuard)
_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parents[4]
DATA_DIR = Path(os.environ.get("HOTTOPIC_DATA_DIR", REPO_ROOT / "data" / "hot_topic"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Unified document schema (re-exported for backward compat)
# ---------------------------------------------------------------------------
from src.main.python.providers.data.base import DOC_COLUMNS  # noqa: E402
DOC_COLUMNS = DOC_COLUMNS  # re-export

# ---------------------------------------------------------------------------
# THUCNews (HuggingFace datasets) — convenience re-exports
# ---------------------------------------------------------------------------
THUCNEWS_HF_REPO = os.environ.get("THUCNEWS_HF_REPO", "madao33/new-title-chinese")
THUCNEWS_HF_SPLIT = os.environ.get("THUCNEWS_HF_SPLIT", "train")
THUCNEWS_DEFAULT_SAMPLE = int(os.environ.get("THUCNEWS_DEFAULT_SAMPLE", "10000"))
THUCNEWS_OUTPUT = DATA_DIR / "thucnews_sample.csv"

# ---------------------------------------------------------------------------
# GDELT DOC 2.0 — convenience re-exports
# ---------------------------------------------------------------------------
GDELT_DOC_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_DEFAULT_QUERY = os.environ.get("GDELT_DEFAULT_QUERY", "sourcelang:chinese")
GDELT_DEFAULT_TIMESPAN = os.environ.get("GDELT_DEFAULT_TIMESPAN", "24h")
GDELT_MAX_RECORDS_PER_CALL = 250
GDELT_REQUEST_TIMEOUT = 30
GDELT_RETRY_ATTEMPTS = 3
GDELT_RETRY_BACKOFF = 2.0
GDELT_MIN_INTERVAL = float(os.environ.get("GDELT_MIN_INTERVAL", "5.5"))
GDELT_USER_AGENT = "SentiGuard-HotTopic/0.1 (+research)"

# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------
CSV_ENCODING = "utf-8-sig"
