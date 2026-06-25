"""外部数据源适配层 — 新闻语料获取 API。

providers/data/ 收纳所有获取新闻语料的外部 API 调用，统一输出 DOC_COLUMNS schema。

数据源：
    - THUCNewsLoader  HuggingFace datasets
    - GDELTClient     GDELT DOC 2.0 API
    - RSSClient       RSS/Atom Feed

使用方式：
    from src.main.python.providers.data import THUCNewsLoader, GDELTClient

    loader = THUCNewsLoader()
    df = loader.to_dataframe(sample_size=10000)
"""

from .base import BaseDataSource, DOC_COLUMNS, merge_sources
from .gdelt import GDELTClient
from .rss import RSSClient
from .thucnews import THUCNewsLoader

__all__ = [
    "BaseDataSource",
    "DOC_COLUMNS",
    "merge_sources",
    "GDELTClient",
    "RSSClient",
    "THUCNewsLoader",
]
