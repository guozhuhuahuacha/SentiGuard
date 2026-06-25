#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anspire 搜索引擎测试
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from dotenv import load_dotenv
load_dotenv()


def test_anspire_search():
    """测试 Anspire 搜索引擎"""
    print("=" * 60)
    print("Anspire 搜索引擎测试")
    print("=" * 60)

    # 先导入工具模块以注册搜索引擎
    from src.main.python.tools import search_anspire
    from src.main.python.providers.search import get_search_engine, list_search_engines

    # 1. 检查可用的搜索引擎
    print(f"\n📋 可用搜索引擎: {list_search_engines()}")

    # 2. 获取 Anspire 引擎
    engine = get_search_engine("anspire")

    if not engine:
        print("\n❌ 未找到 Anspire 搜索引擎")
        return False

    print(f"\n✅ 获取引擎: {engine.__class__.__name__}")

    # 3. 检查是否可用
    if not engine.is_available():
        print("\n❌ Anspire 引擎不可用")
        print("💡 请检查环境变量: ANSPIRE_API_KEY")
        return False

    print(f"✅ Anspire 引擎可用")

    # 4. 测试搜索
    test_queries = [
        "中国",
    ]

    for query in test_queries:
        print(f"\n🔍 搜索: {query}")
        print("-" * 60)

        try:
            results = engine.search(query, num_results=5)

            if results:
                print(f"✅ 找到 {len(results)} 条结果")
                for i, result in enumerate(results):
                    print(f"\n   {i+1}. {result.title}")
                    print(f"      {result.url}")
                    snippet = result.snippet[:100] + "..." if len(result.snippet) > 100 else result.snippet
                    print(f"      {snippet}")
            else:
                print(f"⚠️  未找到结果")

        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_anspire_search()
