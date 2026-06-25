#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""百度热搜采集器测试

运行方式：
    python src/test/python/test_trending_baidu.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv
load_dotenv()


def test_baidu_collect():
    from src.main.python.providers.trending.baidu import BaiduCollector

    print("=" * 60)
    print("百度热搜采集器测试（limit=100）")
    print("=" * 60)

    collector = BaiduCollector()

    try:
        items = collector.fetch(limit=100)
    except Exception as e:
        print(f"\n❌ 采集失败: {e}")
        return False

    if not items:
        print("\n❌ 未获取到任何热搜数据")
        return False

    print(f"\n✅ 成功获取 {len(items)} 条热搜\n")
    print(f"前 20 条：")
    print("-" * 60)
    for item in items[:20]:
        print(f"  #{item.rank:<3} {item.title[:35]:<35} 热度:{item.heat:>6.1f}")
    print("-" * 60)

    avg_heat = sum(it.heat for it in items) / len(items)
    print(f"\n统计: 总数={len(items)}, 平均热度={avg_heat:.1f}, 最高={max(it.heat for it in items):.1f}, 最低={min(it.heat for it in items):.1f}")

    return True


if __name__ == "__main__":
    ok = test_baidu_collect()
    print(f"\n{'=' * 60}")
    print(f"结果: {'✅ 测试通过' if ok else '❌ 测试失败'}")
