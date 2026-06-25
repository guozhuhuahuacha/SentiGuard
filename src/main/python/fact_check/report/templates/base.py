"""模板 — 抽象基类与注册表。

模板决定报告包含哪些章节及其顺序。
新增模板方式：
    1. 继承 BaseTemplate
    2. 实现 get_section_names() 返回章节名列表
    3. 在 templates/__init__.py 中注册
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Dict, List, Type

from ..models import ReportData


_template_registry: Dict[str, Type["BaseTemplate"]] = {}


def register_template(name: str, cls: Type["BaseTemplate"]) -> None:
    _template_registry[name] = cls


def get_template(name: str) -> Type["BaseTemplate"]:
    if name not in _template_registry:
        raise KeyError(f"未知模板: {name}，可用: {list(_template_registry.keys())}")
    return _template_registry[name]


def list_templates() -> List[str]:
    return list(_template_registry.keys())


class BaseTemplate(ABC):
    """报告模板抽象基类"""

    name: ClassVar[str] = ""
    description: ClassVar[str] = ""

    def __init__(self, data: ReportData):
        self.data = data

    @abstractmethod
    def get_section_names(self) -> List[str]:
        """返回要包含的章节名称列表（顺序决定报告中的顺序）"""
        ...

    def get_title(self) -> str:
        """报告标题"""
        claim = (self.data.claim or "").strip()
        if claim:
            return f"事实核查报告 — {claim[:50]}"
        return "事实核查报告"
