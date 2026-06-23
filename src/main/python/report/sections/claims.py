"""声明拆解章节"""
from __future__ import annotations

from ..models import ReportData, SectionOutput
from .base import BaseSection, register_section


class ClaimsSection(BaseSection):
    """展示声明拆解结果"""

    def render(self) -> SectionOutput:
        lines: list[str] = []
        lines.append("## 声明拆解\n")

        if not self.data.claims:
            lines.append("（未拆解出可核查声明）\n")
            return SectionOutput(title="声明拆解", content="".join(lines), order=2)

        for c in self.data.claims:
            type_tag = f"[{c.claimType}]" if c.claimType != "verifiable" else ""
            lines.append(f"- **声明 {c.claimOrder}** {type_tag}：{c.claimText}\n")

        lines.append("\n---\n")
        return SectionOutput(title="声明拆解", content="".join(lines), order=2)


register_section("claims", ClaimsSection)
