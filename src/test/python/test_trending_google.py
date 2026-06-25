#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Google Trends 热搜采集器测试 -- 多区域对比

运行方式：
    python src/test/python/test_trending_google.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv
load_dotenv()


def test_google_all():
    from src.main.python.providers.trending.google_trends import GoogleTrendsCollector

    limit = 100

    regions = [
        ("HK", "香港"),
        ("TW", "台湾"),
        ("JP", "日本"),
        ("KR", "韩国"),
        ("US", "美国"),
        ("GB", "英国"),
        ("CN", "中国(自动回退US)"),
    ]

    print("=" * 60)
    print(f"Google Trends 多区域对比测试 (limit={limit})")
    print("=" * 60)

    results = {}
    for geo, label in regions:
        print(f"\n{'─' * 60}")
        print(f"  {label} (geo={geo}): ", end="", flush=True)
        try:
            collector = GoogleTrendsCollector(geo=geo)
            actual_geo = collector.geo
            if actual_geo != geo:
                print(f"geo={geo}不支持, 回退到 geo={actual_geo}")

            items = collector.fetch(limit=limit)
            results[geo] = items
            print(f"    {len(items)} 条热搜", end="")
            if items:
                print(" [OK]")
                for it in items[:5]:
                    print(f"      #{it.rank} {it.title[:35]:<35} heat={it.heat:.1f}")
            else:
                print(" [空 -- Google 无此区域热搜数据]")
        except Exception as e:
            print(f"    [FAIL] {e}")

    # 汇总
    print(f"\n{'=' * 60}")
    print("汇总")
    print(f"{'=' * 60}")
    for geo, label in regions:
        if geo in results:
            items = results[geo]
            print(f"  {label:10} (geo={geo:4}): {len(items):>3} 条")
        else:
            print(f"  {label:10} (geo={geo:4}): 请求失败")
    return True


if __name__ == "__main__":
    ok = test_google_all()
    print(f"\n{'=' * 60}")
    print(f"结果: {'OK' if ok else 'FAIL'}")
