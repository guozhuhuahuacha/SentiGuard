"""搜索业务逻辑模块 — 构建在 providers/search/ API 之上的网页抓取与搜索策略。

providers/search/   ← 搜索引擎 API 适配层（纯粹的外部接口）
search/             ← 本模块：Selenium 网页抓取 + LLM 内容抽取 + 搜索策略

模块组成：
    retriever.py    SearchEngineRetriever — Selenium + LLM 网页内容抽取
    service.py      搜索策略 — search_summary() / search_fulltext()
"""

from src.main.python.search.retriever import SearchEngineRetriever, search_retrieve_news
from src.main.python.search.service import search_summary, search_fulltext

__all__ = [
    "SearchEngineRetriever",
    "search_retrieve_news",
    "search_summary",
    "search_fulltext",
]
