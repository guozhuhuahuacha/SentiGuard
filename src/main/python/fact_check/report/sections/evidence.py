"""证据分析章节"""
from __future__ import annotations

from ..models import ReportData, SectionOutput
from .base import BaseSection, register_section


class EvidenceSection(BaseSection):
    """展示每条证据及其与声明的论辩关系"""

    def render(self) -> SectionOutput:
        lines: list[str] = []
        lines.append("## 证据分析\n")

        if not self.data.evidences:
            lines.append("（未检索到有效证据）\n")
            return SectionOutput(title="证据分析", content="".join(lines), order=3)

        for ev in self.data.evidences:
            rel_icon = self._relation_icon(ev.relationType)
            lines.append(f"### {rel_icon} 声明 {ev.claimOrder} 相关证据\n")

            if ev.evidenceTitle:
                lines.append(f"- **标题**：{ev.evidenceTitle}\n")
            if ev.sourceName:
                lines.append(f"- **来源**：{ev.sourceName}\n")
            if ev.evidenceUrl:
                lines.append(f"- **链接**：{ev.evidenceUrl}\n")
            if ev.evidenceContent:
                content_preview = (
                    ev.evidenceContent[:300] + "..."
                    if len(ev.evidenceContent) > 300
                    else ev.evidenceContent
                )
                lines.append(f"- **摘要**：{content_preview}\n")
            lines.append(f"- **关系**：{ev.relationType}\n")
            if ev.credibilityScore is not None:
                lines.append(f"- **可信度**：{ev.credibilityScore}/100\n")
            if ev.publishTime:
                lines.append(f"- **发布时间**：{ev.publishTime}\n")
            lines.append("\n")

        lines.append("---\n")
        return SectionOutput(title="证据分析", content="".join(lines), order=3)

    @staticmethod
    def _relation_icon(relation: str) -> str:
        icons = {"support": "✅", "attack": "❌", "neutral": "➖"}
        return icons.get(relation, "📄")


register_section("evidence", EvidenceSection)
