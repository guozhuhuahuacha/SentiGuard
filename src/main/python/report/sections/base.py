"""章节 — 抽象基类与注册表。

新增章节方式（开闭原则）：
    1. 继承 BaseSection
    2. 实现 render() 方法
    3. 在 sections/__init__.py 中调用 register_section()
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from ..models import ReportData, SectionOutput


# ---------------------------------------------------------------------------
# 注册表
# ---------------------------------------------------------------------------
_section_registry: Dict[str, Type["BaseSection"]] = {}


def register_section(name: str, cls: Type["BaseSection"]) -> None:
    """注册一个章节类"""
    _section_registry[name] = cls


def get_section(name: str) -> Type["BaseSection"]:
    """按名称获取章节类；不存在时抛 KeyError"""
    if name not in _section_registry:
        raise KeyError(f"未知的章节类型: {name}，可用: {list(_section_registry.keys())}")
    return _section_registry[name]


def list_sections() -> List[str]:
    """列出所有已注册的章节名称"""
    return list(_section_registry.keys())


# ---------------------------------------------------------------------------
# 基类
# ---------------------------------------------------------------------------
class BaseSection(ABC):
    """报告章节抽象基类"""

    def __init__(self, data: ReportData):
        self.data = data

    @abstractmethod
    def render(self) -> SectionOutput:
        """渲染章节，返回结构化的输出"""
        ...

    def _safe(self, value: Any, default: str = "") -> str:
        """安全取值，None → default"""
        return str(value) if value is not None else default
