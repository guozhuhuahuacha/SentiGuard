#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块 — FactAgent 使用的 LangChain @tool 封装。

向后兼容层：搜索逻辑已迁移至 search/，此模块保留重导出。
新代码请使用：
    from src.main.python.search import search_retrieve_news, search_summary, search_fulltext
"""
from src.main.python.search.retriever import search_retrieve_news

# 搜索引擎接口（从 providers 重导出，保持兼容）
from src.main.python.providers.search import (
    BaseSearchEngine,
    SearchResult,
    SearchQuery,
    SearchEngineRegistry,
    register_search_engine,
    get_search_engine,
    list_search_engines,
)

# 触发搜索引擎注册
from src.main.python.providers.search import anspire as _anspire  # noqa: F401

# 搜索服务模块（两种策略）
from src.main.python.search import service as search_service
