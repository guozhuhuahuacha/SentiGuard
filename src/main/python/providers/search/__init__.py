"""搜索引擎适配层

支持的搜索引擎：
    - Anspire

新增引擎：继承 BaseSearchEngine 并调用 register_search_engine 注册即可。
"""

from src.main.python.providers.search.base import (
    BaseSearchEngine,
    SearchResult,
    SearchQuery,
    SearchEngineRegistry,
    register_search_engine,
    get_search_engine,
    list_search_engines,
)

# 导入搜索引擎实现以触发注册
from src.main.python.providers.search import anspire  # noqa: F401

__all__ = [
    "BaseSearchEngine",
    "SearchResult",
    "SearchQuery",
    "SearchEngineRegistry",
    "register_search_engine",
    "get_search_engine",
    "list_search_engines",
]
