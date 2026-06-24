"""舆论监测模块数据模型。

设计原则：
- 不修改 api/schemas.py 或 report/models.py 中任何既有类
- 本模块所有类自包含，通过 adapter 函数转换（如需对接既有结构）
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================
# 观点项 — 单条搜索结果提取出的观点
# ============================================================
class OpinionItem(BaseModel):
    """从单条搜索结果中抽取的观点"""
    sourceTitle: str = Field(default="", description="来源标题")
    sourceUrl: str = Field(default="", description="来源链接")
    sourceDomain: str = Field(default="", description="来源域名/平台名")
    stance: str = Field(
        default="neutral",
        description="立场：support(支持当事人/事件正面) / oppose(反对) / neutral(中立) / mixed(混合)"
    )
    sentiment: str = Field(
        default="neutral",
        description="情感倾向：positive / negative / neutral"
    )
    coreArgument: str = Field(default="", description="核心论点，一句话概括")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    speakerType: str = Field(
        default="普通网友",
        description="发言者类型：普通网友 / 媒体 / 专家 / 官方 / 当事人"
    )
    excerptText: str = Field(default="", description="原文摘录（支持观点的关键句）")


# ============================================================
# 立场簇 — 聚类后的观点组
# ============================================================
class StanceCluster(BaseModel):
    """归并后的立场簇（一组相似观点）"""
    clusterId: int = Field(..., ge=1, description="簇编号")
    stance: str = Field(..., description="support / oppose / neutral")
    label: str = Field(default="", description="该簇的简短标签，如'认为法院判决公正'")
    summary: str = Field(default="", description="该立场簇的核心观点总结（2-3句话）")
    representativeArguments: List[str] = Field(
        default_factory=list,
        description="该簇的代表性论点（Top 2-3）"
    )
    opinionCount: int = Field(default=0, ge=0, description="该簇包含的原始观点数")
    speakerBreakdown: dict = Field(
        default_factory=dict,
        description="发言者类型分布，如 {'普通网友': 15, '媒体': 5}"
    )
    sentimentRatio: dict = Field(
        default_factory=dict,
        description="情感分布，如 {'positive': 0.6, 'negative': 0.2, 'neutral': 0.2}"
    )
    sampleExcerpts: List[str] = Field(
        default_factory=list,
        description="代表性原文摘录（2-3条）"
    )


# ============================================================
# 舆论画像 — 最终输出
# ============================================================
class OpinionPortrait(BaseModel):
    """舆论画像（最终分析结果）"""
    eventName: str = Field(..., description="事件名称")
    generatedAt: str = Field(default="", description="生成时间 ISO8601")

    # 整体统计
    totalOpinions: int = Field(default=0, description="收集到的总观点数")
    totalSources: int = Field(default=0, description="不重复来源数")

    # 立场分布
    stanceDistribution: dict = Field(
        default_factory=dict,
        description="立场分布，如 {'support': 0.45, 'oppose': 0.30, 'neutral': 0.25}"
    )

    # 情感分布
    sentimentDistribution: dict = Field(
        default_factory=dict,
        description="情感分布，如 {'positive': 0.4, 'negative': 0.35, 'neutral': 0.25}"
    )

    # 立场簇
    clusters: List[StanceCluster] = Field(default_factory=list, description="归并后的立场簇")

    # 风险预警
    riskLevel: str = Field(default="low", description="风险等级：low / medium / high / critical")
    riskNotes: List[str] = Field(default_factory=list, description="风险提示说明")

    # 舆论总结（叙事文本）
    narrativeSummary: str = Field(default="", description="舆论画像叙事总结（2-3段）")


# ============================================================
# API 请求/响应
# ============================================================
class OpinionAnalyzeRequest(BaseModel):
    event: str = Field(..., min_length=1, max_length=500, description="事件名称或关键词")
    description: str = Field(default="", max_length=2000, description="事件补充描述（可选）")


class OpinionReportData(BaseModel):
    """API 响应 data 字段"""
    portrait: OpinionPortrait
    report: dict = Field(default_factory=dict, description="HTML 报告，含 title/content/format")


__all__ = [
    "OpinionItem",
    "StanceCluster",
    "OpinionPortrait",
    "OpinionAnalyzeRequest",
    "OpinionReportData",
]
