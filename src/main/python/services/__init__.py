"""SentiGuard 数据服务模块

数据采集 → 聚类 → 情感分析 → 存储管道
"""
from .pipeline import HotspotPipeline

__all__ = ["HotspotPipeline"]
