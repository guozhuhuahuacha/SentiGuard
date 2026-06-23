"""标准事实核查模板"""
from __future__ import annotations

from typing import ClassVar, List

from .base import BaseTemplate, register_template


class StandardTemplate(BaseTemplate):
    """标准模板：包含所有章节"""

    name: ClassVar[str] = "standard"
    description: ClassVar[str] = "标准事实核查报告，包含声明拆解、证据分析、判定结论"

    def get_section_names(self) -> List[str]:
        return ["header", "claims", "evidence", "verdict", "metadata"]


register_template("standard", StandardTemplate)
