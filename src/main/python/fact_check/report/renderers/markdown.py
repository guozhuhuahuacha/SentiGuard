"""Markdown 渲染器"""
from __future__ import annotations

from typing import List

from ..models import SectionOutput
from .base import BaseRenderer, register_renderer


class MarkdownRenderer(BaseRenderer):
    """将章节输出渲染为 Markdown"""

    def render(self, sections: List[SectionOutput], title: str) -> str:
        parts: list[str] = []

        # 按 order 排序
        sorted_sections = sorted(sections, key=lambda s: s.order)

        for sec in sorted_sections:
            parts.append(sec.content)

        full = "\n".join(parts)

        # 如果第一个章节没有包含 # 标题，在前面加一个
        if not full.lstrip().startswith("#"):
            full = f"# {title}\n\n{full}"

        return full.strip()


register_renderer("markdown", MarkdownRenderer)
