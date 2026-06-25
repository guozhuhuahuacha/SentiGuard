"""渲染器 — 抽象基类与注册表。

渲染器负责将多个 SectionOutput 拼装为最终报告字符串。
新增渲染器方式：
    1. 继承 BaseRenderer
    2. 实现 render() 和/或 render_llm() 方法
    3. 在 renderers/__init__.py 中注册
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from ..models import SectionOutput


_renderer_registry: Dict[str, Type["BaseRenderer"]] = {}


def register_renderer(name: str, cls: Type["BaseRenderer"]) -> None:
    _renderer_registry[name] = cls


def get_renderer(name: str) -> Type["BaseRenderer"]:
    if name not in _renderer_registry:
        raise KeyError(f"未知渲染器: {name}，可用: {list(_renderer_registry.keys())}")
    return _renderer_registry[name]


def list_renderers() -> List[str]:
    return list(_renderer_registry.keys())


class BaseRenderer(ABC):
    """渲染器抽象基类"""

    @abstractmethod
    def render(self, sections: List[SectionOutput], title: str) -> str:
        """将章节列表渲染为最终字符串（数据驱动模式）"""
        ...

    def render_llm(self, content: str, layout: Dict[str, Any]) -> str:
        """将 LLM 生成的内容渲染为最终字符串（LLM 叙事模式降级路径）

        默认实现直接返回 content，子类可覆写（如 HTML 渲染器做 Markdown→HTML 转换）
        """
        return content

    def render_ir(self, document_ir: Dict[str, Any]) -> str:
        """将结构化 IR 渲染为最终字符串（IR 模式）

        默认实现将 document_ir 序列化为 JSON，子类可覆写。
        """
        import json
        return json.dumps(document_ir, ensure_ascii=False, indent=2)
