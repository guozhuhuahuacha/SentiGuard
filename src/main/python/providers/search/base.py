#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络搜索基类 - 定义搜索接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    url: str
    snippet: str
    content: Optional[str] = None
    source: Optional[str] = None
    published_date: Optional[str] = None
    score: Optional[float] = None


@dataclass
class SearchQuery:
    """搜索查询数据类"""
    query: str
    num_results: int = 10
    time_range: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None


class BaseSearchEngine(ABC):
    """
    网络搜索引擎基类

    所有具体的搜索引擎实现都需要继承此类，
    并实现以下抽象方法。
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化搜索引擎

        Args:
            config: 配置字典，包含 API Key 等配置项
        """
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """
        验证配置是否有效

        Raises:
            ValueError: 配置无效时抛出异常
        """
        pass

    @abstractmethod
    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        执行搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        pass

    @abstractmethod
    def search_advanced(self, search_query: SearchQuery) -> List[SearchResult]:
        """
        高级搜索 - 支持更多参数

        Args:
            search_query: 搜索查询对象

        Returns:
            搜索结果列表
        """
        pass

    @abstractmethod
    def fetch_content(self, url: str) -> Optional[str]:
        """
        获取 URL 的完整内容

        Args:
            url: 网页地址

        Returns:
            网页内容，失败返回 None
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查搜索引擎是否可用

        Returns:
            True 表示可用，False 表示不可用
        """
        pass

    def batch_search(self, queries: List[str], num_results: int = 10) -> Dict[str, List[SearchResult]]:
        """
        批量搜索 - 默认实现，子类可以覆盖优化

        Args:
            queries: 搜索关键词列表
            num_results: 每个查询的结果数量

        Returns:
            {查询: 结果列表} 的字典
        """
        results = {}
        for query in queries:
            try:
                results[query] = self.search(query, num_results)
            except Exception as e:
                print(f"搜索 '{query}' 失败: {e}")
                results[query] = []
        return results

    def extract_relevant_content(self, results: List[SearchResult], keyword: str) -> List[SearchResult]:
        """
        从搜索结果中提取与关键词相关的内容 - 默认实现

        Args:
            results: 搜索结果列表
            keyword: 关键词

        Returns:
            过滤后的结果列表
        """
        relevant = []
        keyword_lower = keyword.lower()

        for result in results:
            text = (result.title + " " + result.snippet + " " + (result.content or "")).lower()
            if keyword_lower in text:
                relevant.append(result)

        return relevant

    def merge_results(self, results_list: List[List[SearchResult]]) -> List[SearchResult]:
        """
        合并多个搜索结果 - 默认实现

        Args:
            results_list: 搜索结果列表的列表

        Returns:
            合并后的结果列表
        """
        seen_urls = set()
        merged = []

        for results in results_list:
            for result in results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    merged.append(result)

        return merged


class SearchEngineRegistry:
    """
    搜索引擎注册器 - 用于管理多个搜索引擎

    使用示例:
        registry = SearchEngineRegistry()
        registry.register("anspire", AnspireSearchEngine)
        registry.register("serper", SerperSearchEngine)

        engine = registry.get("anspire", config={...})
    """

    def __init__(self):
        self._engines = {}

    def register(self, name: str, engine_class: type) -> None:
        """
        注册搜索引擎

        Args:
            name: 引擎名称
            engine_class: 引擎类（需要继承 BaseSearchEngine）
        """
        if not issubclass(engine_class, BaseSearchEngine):
            raise ValueError(f"{engine_class.__name__} 必须继承 BaseSearchEngine")
        self._engines[name] = engine_class

    def get(self, name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseSearchEngine]:
        """
        获取搜索引擎实例

        Args:
            name: 引擎名称
            config: 配置字典

        Returns:
            搜索引擎实例，如果未注册返回 None
        """
        engine_class = self._engines.get(name)
        if engine_class:
            return engine_class(config)
        return None

    def list_available(self) -> List[str]:
        """
        列出所有可用的搜索引擎名称

        Returns:
            搜索引擎名称列表
        """
        return list(self._engines.keys())


# 全局注册器实例
_search_registry = SearchEngineRegistry()


def register_search_engine(name: str, engine_class: type) -> None:
    """全局注册搜索引擎的便捷函数"""
    _search_registry.register(name, engine_class)


def get_search_engine(name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseSearchEngine]:
    """全局获取搜索引擎的便捷函数"""
    return _search_registry.get(name, config)


def list_search_engines() -> List[str]:
    """列出所有可用的搜索引擎"""
    return _search_registry.list_available()
