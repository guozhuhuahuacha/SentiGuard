"""元信息章节：运行 ID、生成时间等"""
from __future__ import annotations

from ..models import ReportData, SectionOutput
from .base import BaseSection, register_section


class MetadataSection(BaseSection):
    """报告元信息"""

    def render(self) -> SectionOutput:
        lines: list[str] = []
        lines.append("---\n")
        lines.append("## 报告信息\n")
        if self.data.run_id:
            lines.append(f"- **追踪 ID**：`{self.data.run_id}`\n")
        if self.data.generated_at:
            lines.append(f"- **生成时间**：{self.data.generated_at}\n")
        if self.data.claim:
            lines.append(f"- **原始声明**：{self.data.claim[:100]}\n")

        return SectionOutput(title="报告信息", content="".join(lines), order=99)


register_section("metadata", MetadataSection)
