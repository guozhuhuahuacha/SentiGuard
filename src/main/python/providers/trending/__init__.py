"""热搜平台适配层

支持的热搜来源：
    - 百度热搜（BaiduCollector）
    - Google Trends（GoogleTrendsCollector）

新增热搜平台：参照已有 Collector 实现 fetch(limit) 方法，在此 __init__.py 中导出即可。
"""

from src.main.python.providers.trending.baidu import BaiduCollector, BaiduHotItem
from src.main.python.providers.trending.google_trends import GoogleTrendsCollector, GoogleTrendsHotItem

__all__ = [
    "BaiduCollector", "BaiduHotItem",
    "GoogleTrendsCollector", "GoogleTrendsHotItem",
]
