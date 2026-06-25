"""舆论监测 HTML 报告生成器。

复用 report/renderers/html.py 的 render_framework + _wrap_html + CSS 变量体系。
不修改 report/generator.py 或 report/renderers/html.py 中任何既有代码。
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from src.main.python.fact_check.report.renderers.html import HTMLRenderer
from .schemas import OpinionPortrait, StanceCluster

logger = logging.getLogger("opinion.generator")

# 立场/情感 → 中文标签映射
STANCE_LABELS = {
    "support": "支持",
    "oppose": "反对",
    "neutral": "中立",
    "mixed": "混合",
}
SENTIMENT_LABELS = {
    "positive": "正面",
    "negative": "负面",
    "neutral": "中性",
}
SENTIMENT_ICONS = {
    "positive": "😊",
    "negative": "😡",
    "neutral": "😐",
}
RISK_LABELS = {
    "low": "🟢 低风险",
    "medium": "🟡 中等风险",
    "high": "🟠 高风险",
    "critical": "🔴 严重风险",
}


class OpinionReportGenerator:
    """舆论监测 HTML 报告生成器。

    复用现有 HTMLRenderer 的 CSS 体系 + 新增 opinion-card 样式。
    """

    def __init__(self, portrait: OpinionPortrait):
        self.portrait = portrait
        self.renderer = HTMLRenderer()

    def generate(self) -> str:
        """生成完整 HTML 报告。"""
        # 阶段①：渲染 HTML 骨架（复用 render_framework 的 Hero + CSS）
        framework = self._render_framework()

        # 阶段②：渲染内容卡片
        content = self._render_content()

        # 阶段③：组装
        return framework.replace("{claim_sections}", content)

    def _render_framework(self) -> str:
        """渲染 HTML 骨架（Hero + KPI + CSS）。"""
        p = self.portrait

        # 构建 KPIs
        total = p.totalOpinions
        support_pct = int(p.stanceDistribution.get("support", 0) * 100)
        oppose_pct = int(p.stanceDistribution.get("oppose", 0) * 100)

        kpis = [
            {"label": "收集观点", "value": f"{total} 条", "tone": "neutral"},
            {"label": "覆盖来源", "value": f"{p.totalSources} 个", "tone": "neutral"},
            {"label": "支持占比", "value": f"{support_pct}%", "tone": "good" if support_pct >= oppose_pct else "neutral"},
            {"label": "反对占比", "value": f"{oppose_pct}%", "tone": "bad" if oppose_pct > support_pct else "neutral"},
        ]

        # 风险等级 KPI
        risk_tone = {"low": "good", "medium": "neutral", "high": "bad", "critical": "bad"}.get(
            p.riskLevel, "neutral"
        )
        kpis.append({"label": "风险等级", "value": RISK_LABELS.get(p.riskLevel, p.riskLevel), "tone": risk_tone})

        layout = {
            "title": f"舆论监测报告 — {p.eventName}",
            "summary": p.narrativeSummary.split("\n")[0] if p.narrativeSummary else f"共收集 {total} 条观点，覆盖 {p.totalSources} 个来源",
            "keyFindings": [],
            "kpis": kpis,
        }

        # 构建假 result（复用 verdict-banner 展示风险）
        class FakeResult:
            resultLabel = RISK_LABELS.get(p.riskLevel, p.riskLevel)
            confidenceScore = None
            conclusion = f"情感分布：正面 {int(p.sentimentDistribution.get('positive', 0) * 100)}% / 负面 {int(p.sentimentDistribution.get('negative', 0) * 100)}% / 中性 {int(p.sentimentDistribution.get('neutral', 0) * 100)}%"

        # 声明拆解 → 舆论关键发现
        key_findings = []
        if p.clusters:
            for c in p.clusters[:3]:
                key_findings.append({"label": c.label, "detail": f"{c.summary[:120]}（{c.opinionCount}条观点）"})
        layout["keyFindings"] = key_findings

        # claim_texts → 搜索维度说明
        claim_texts = [
            f"事件：{p.eventName}",
            f"收集观点：{p.totalOpinions} 条",
            f"立场分布：支持 {support_pct}% / 反对 {oppose_pct}% / 中立 {100 - support_pct - oppose_pct}%",
        ]

        return self.renderer.render_framework(layout, result=FakeResult(), claim_texts=claim_texts)

    def _render_content(self) -> str:
        """渲染报告正文（舆论画像 + 立场簇卡片）。"""
        p = self.portrait
        parts: List[str] = []

        # ================================================================
        # 舆论画像叙事
        # ================================================================
        if p.narrativeSummary:
            parts.append('<div class="section section-narrative">')
            parts.append('<h2 class="section-title">📝 舆论画像</h2>')
            for para in p.narrativeSummary.split("\n"):
                para = para.strip()
                if para:
                    parts.append(f'<p>{self._escape(para)}</p>')
            parts.append("</div>")

        # ================================================================
        # 立场分布统计
        # ================================================================
        parts.append('<div class="section section-distribution">')
        parts.append('<h2 class="section-title">📊 立场分布</h2>')
        parts.append(self._render_distribution_bars(p))
        parts.append("</div>")

        # ================================================================
        # 立场簇卡片
        # ================================================================
        if p.clusters:
            parts.append('<div class="section section-clusters">')
            parts.append('<h2 class="section-title">🗂️ 观点聚类分析</h2>')
            parts.append('<p class="section-desc">以下为基于收集到的观点进行立场聚类后的分析结果：</p>')
            for c in p.clusters:
                parts.append(self._render_cluster_card(c))
            parts.append("</div>")

        # ================================================================
        # 风险预警
        # ================================================================
        if p.riskLevel != "low" and p.riskNotes:
            parts.append('<div class="section section-risk">')
            parts.append('<h2 class="section-title">⚠️ 风险预警</h2>')
            parts.append('<div class="callout callout-warning">')
            parts.append(f'<div class="callout-title">{RISK_LABELS.get(p.riskLevel, p.riskLevel)}</div>')
            parts.append('<div class="callout-body"><ul>')
            for note in p.riskNotes:
                parts.append(f'<li>{self._escape(note)}</li>')
            parts.append("</ul></div></div></div>")

        return "\n".join(parts)

    def _render_distribution_bars(self, p: OpinionPortrait) -> str:
        """渲染立场分布条。"""
        support = int(p.stanceDistribution.get("support", 0) * 100)
        oppose = int(p.stanceDistribution.get("oppose", 0) * 100)
        neutral = 100 - support - oppose

        pos_sent = int(p.sentimentDistribution.get("positive", 0) * 100)
        neg_sent = int(p.sentimentDistribution.get("negative", 0) * 100)
        neu_sent = 100 - pos_sent - neg_sent

        return f"""
<div class="distro-section">
  <h4>立场</h4>
  <div class="distro-bar">
    <div class="distro-seg seg-support" style="width:{support}%">
      <span>支持 {support}%</span>
    </div>
    <div class="distro-seg seg-oppose" style="width:{oppose}%">
      <span>反对 {oppose}%</span>
    </div>
    <div class="distro-seg seg-neutral" style="width:{neutral}%">
      <span>中立 {neutral}%</span>
    </div>
  </div>
  <h4 style="margin-top:24px">情感</h4>
  <div class="distro-bar">
    <div class="distro-seg seg-positive" style="width:{pos_sent}%">
      <span>{SENTIMENT_ICONS['positive']} 正面 {pos_sent}%</span>
    </div>
    <div class="distro-seg seg-negative" style="width:{neg_sent}%">
      <span>{SENTIMENT_ICONS['negative']} 负面 {neg_sent}%</span>
    </div>
    <div class="distro-seg seg-neutral" style="width:{neu_sent}%">
      <span>{SENTIMENT_ICONS['neutral']} 中性 {neu_sent}%</span>
    </div>
  </div>
</div>"""

    def _render_cluster_card(self, c: StanceCluster) -> str:
        """渲染单个立场簇卡片。"""
        stance_label = STANCE_LABELS.get(c.stance, c.stance)
        stance_class = c.stance
        speaker_info = ", ".join(f"{k}:{v}" for k, v in sorted(c.speakerBreakdown.items(), key=lambda x: -x[1])[:3])

        parts = [
            '<div class="opinion-cluster-card">',
            '<div class="cluster-header">',
            f'<span class="cluster-stance {stance_class}">{stance_label}</span>',
            f'<span class="cluster-label">{self._escape(c.label)}</span>',
            f'<span class="cluster-count">{c.opinionCount} 条观点</span>',
            "</div>",
            '<div class="cluster-body">',
            f'<p class="cluster-summary">{self._escape(c.summary)}</p>',
        ]

        # 代表论点
        if c.representativeArguments:
            parts.append('<ul class="cluster-args">')
            for arg in c.representativeArguments:
                parts.append(f'<li>{self._escape(arg)}</li>')
            parts.append("</ul>")

        # 发言者分布
        if speaker_info:
            parts.append(f'<p class="cluster-meta">🗣️ 发言者：{self._escape(speaker_info)}</p>')

        # 情感分布
        if c.sentimentRatio:
            pos = int(c.sentimentRatio.get("positive", 0) * 100)
            neg = int(c.sentimentRatio.get("negative", 0) * 100)
            parts.append(f'<p class="cluster-meta">情感：😊{pos}% 😡{neg}% 😐{100 - pos - neg}%</p>')

        # 原文摘录
        if c.sampleExcerpts:
            parts.append('<div class="cluster-excerpts">')
            parts.append('<p class="cluster-meta"><strong>原文摘录：</strong></p>')
            for ex in c.sampleExcerpts[:3]:
                parts.append(f'<blockquote class="excerpt">{self._escape(ex)}</blockquote>')
            parts.append("</div>")

        parts.append("</div>")  # cluster-body
        parts.append("</div>")  # opinion-cluster-card
        return "\n".join(parts)

    @staticmethod
    def _escape(text: str) -> str:
        """HTML 转义。"""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )


__all__ = ["OpinionReportGenerator"]
