#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anspire 搜索引擎实现

使用 Anspire 服务进行网络搜索
环境变量配置: ANSPIRE_API_KEY, ANSPIRE_BASE_URL
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

from src.main.python.tools.search_base import (
    BaseSearchEngine,
    SearchResult,
    SearchQuery,
    register_search_engine,
)


class AnspireSearchEngine(BaseSearchEngine):
    """
    Anspire 搜索引擎实现

    配置项（在 config 中或环境变量中设置）:
        - api_key: Anspire API Key (环境变量: ANSPIRE_API_KEY)
        - base_url: Anspire API 地址 (环境变量: ANSPIRE_BASE_URL, 默认: https://api.anspire.com/v1)
        - timeout: 请求超时时间（秒）
    """

    # 环境变量名称
    ENV_API_KEY = "ANSPIRE_API_KEY"
    ENV_BASE_URL = "ANSPIRE_BASE_URL"

    # 默认配置
    DEFAULT_BASE_URL = "https://api.anspire.com/v1"
    DEFAULT_TIMEOUT = 30

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # 从配置或环境变量中读取参数
        self.api_key = self.config.get("api_key") or os.getenv(self.ENV_API_KEY)
        self.base_url = self.config.get("base_url") or os.getenv(self.ENV_BASE_URL) or self.DEFAULT_BASE_URL
        self.timeout = self.config.get("timeout") or self.DEFAULT_TIMEOUT

    def _validate_config(self) -> None:
        """
        验证配置是否有效

        Raises:
            ValueError: API Key 未设置时抛出异常
        """
        api_key = self.config.get("api_key") or os.getenv(self.ENV_API_KEY)
        if not api_key:
            raise ValueError(f"Anspire API Key 未设置，请在配置中或环境变量 {self.ENV_API_KEY} 中设置")

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        使用 Anspire 执行搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.is_available():
            return []

        try:
            # 构建 API 请求
            api_endpoint = f"{self.base_url.rstrip('/')}/search"

            payload = {
                "query": query,
                "num_results": num_results,
            }

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            }

            # 发送请求
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data)
            else:
                print(f"⚠️  Anspire API 错误: {response.status_code}")
                print(f"   {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Anspire 请求失败: {e}")
            return []
        except Exception as e:
            print(f"⚠️  Anspire 搜索出错: {e}")
            return []

    def search_advanced(self, search_query: SearchQuery) -> List[SearchResult]:
        """
        高级搜索 - 支持更多参数

        Args:
            search_query: 搜索查询对象

        Returns:
            搜索结果列表
        """
        if not self.is_available():
            return []

        try:
            # 构建 API 请求
            api_endpoint = f"{self.base_url.rstrip('/')}/search"

            payload = {
                "query": search_query.query,
                "num_results": search_query.num_results,
            }

            # 添加可选参数
            if search_query.language:
                payload["language"] = search_query.language
            if search_query.region:
                payload["region"] = search_query.region
            if search_query.time_range:
                payload["time_range"] = search_query.time_range

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            }

            # 发送请求
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data)
            else:
                print(f"⚠️  Anspire API 错误: {response.status_code}")
                return []

        except Exception as e:
            print(f"⚠️  Anspire 高级搜索出错: {e}")
            return []

    def fetch_content(self, url: str) -> Optional[str]:
        """
        获取 URL 的完整内容

        Args:
            url: 网页地址

        Returns:
            网页内容，失败返回 None
        """
        if not self.is_available():
            return None

        try:
            # 使用 Anspire 的内容获取 API（如果有）
            api_endpoint = f"{self.base_url.rstrip('/')}/fetch"

            payload = {"url": url}
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            }

            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("content")
            else:
                print(f"⚠️  Anspire 内容获取失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠️  Anspire 内容获取出错: {e}")
            return None

    def is_available(self) -> bool:
        """
        检查 Anspire 服务是否可用

        Returns:
            True 表示可用，False 表示不可用
        """
        return bool(self.api_key)

    def _parse_response(self, data: Dict[str, Any]) -> List[SearchResult]:
        """
        解析 Anspire API 响应

        Args:
            data: API 返回的 JSON 数据

        Returns:
            搜索结果列表

        注意: 根据 Anspire API 的实际响应格式调整解析逻辑
        """
        results = []

        # 根据 Anspire 的响应格式解析
        # 这里假设响应格式为 {"results": [...]}
        # 请根据实际的 Anspire API 文档调整
        items = data.get("results", data.get("items", []))

        for item in items:
            # 根据 Anspire 的实际字段名解析
            result = SearchResult(
                title=item.get("title", ""),
                url=item.get("url", item.get("link", "")),
                snippet=item.get("snippet", item.get("description", "")),
                source=item.get("source", item.get("domain", None)),
                published_date=item.get("published_date", item.get("date", None)),
                score=item.get("score", item.get("relevance", None)),
            )
            results.append(result)

        return results


# 注册 Anspire 搜索引擎
register_search_engine("anspire", AnspireSearchEngine)


if __name__ == "__main__":
    # 测试 Anspire 搜索引擎
    print("=" * 60)
    print("Anspire 搜索引擎测试")
    print("=" * 60)

    load_dotenv()

    from src.main.python.tools.search_base import get_search_engine

    # 获取搜索引擎实例
    engine = get_search_engine("anspire")

    if engine and engine.is_available():
        print(f"\n✅ Anspire 引擎可用")

        # 测试搜索
        query = "Python 编程"
        print(f"\n🔍 搜索: {query}")
        results = engine.search(query, num_results=5)

        if results:
            print(f"   找到 {len(results)} 条结果:")
            for i, result in enumerate(results):
                print(f"\n   {i+1}. {result.title}")
                print(f"      {result.url}")
                print(f"      {result.snippet[:100]}...")
        else:
            print(f"   未找到结果")
    else:
        print(f"\n❌ Anspire 引擎不可用")
        print(f"💡 请检查环境变量: ANSPIRE_API_KEY")

    print("\n" + "=" * 60)
