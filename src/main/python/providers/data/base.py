"""外部数据源适配器 — 基础类 + 统一文档 Schema

providers/data/ 收纳所有获取新闻语料的外部 API 调用：
    - thucnews.py    THUCNews（HuggingFace datasets）
    - gdelt.py       GDELT DOC 2.0 API
    - rss.py         RSS/Atom Feed 抓取

统一文档 Schema（DOC_COLUMNS — 8 列）适用于所有数据源，
由 BaseDataSource.to_dataframe() 强制执行。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Iterator

import pandas as pd

# ---------------------------------------------------------------------------
# 统一文档 schema（所有数据源输出必须符合这 8 列）
# ---------------------------------------------------------------------------
DOC_COLUMNS = [
    "doc_id",       # unique id (source-prefixed)
    "title",        # headline / first sentence
    "content",      # body text (may equal title for sources without body)
    "publish_time", # ISO 8601 string in UTC
    "source",       # data source name: "thucnews" / "gdelt" / "rss"
    "url",          # original url ("" for offline corpora)
    "lang",         # ISO 639-1 code, e.g. "zh"
    "category",     # optional source-provided label ("" if absent)
]


class BaseDataSource(ABC):
    """Every data source produces an iterable of dicts conforming to DOC_COLUMNS."""

    name: str = "base"

    @abstractmethod
    def iter_docs(self, **kwargs) -> Iterator[dict]:
        """Yield documents one by one as dicts with keys = DOC_COLUMNS."""
        raise NotImplementedError

    def to_dataframe(self, **kwargs) -> pd.DataFrame:
        """Convenience: collect all docs into a normalized DataFrame."""
        df = pd.DataFrame(list(self.iter_docs(**kwargs)))
        if df.empty:
            return pd.DataFrame(columns=DOC_COLUMNS)
        return _normalize(df)


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Force schema, fill missing columns, deduplicate on doc_id."""
    for col in DOC_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    # Keep only DOC_COLUMNS columns
    df = df[DOC_COLUMNS]
    df = df.drop_duplicates(subset="doc_id", keep="first")
    df = df.reset_index(drop=True)
    return df


def merge_sources(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate multiple DataFrames and normalize."""
    if not frames:
        return pd.DataFrame(columns=DOC_COLUMNS)
    merged = pd.concat(frames, ignore_index=True)
    return _normalize(merged)
