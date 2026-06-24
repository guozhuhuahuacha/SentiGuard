"""舆论监测 API 路由。

POST /internal/v1/opinion/analyze — 舆论监测分析

返回结构（对应 FactCheckDetailDBData 的设计层级）：
    {
      code: 0,
      message: "ok",
      data: {
        portrait: {           // 舆论画像（核心结果）
          eventName, generatedAt, totalOpinions, totalSources,
          stanceDistribution, sentimentDistribution, clusters,
          riskLevel, riskNotes, narrativeSummary
        },
        opinions: [...],       // 所有抽取的原始观点
        clusters: [...],       // 归并后的立场簇
        report: {              // HTML 报告
          reportTitle, reportContent, reportFormat
        },
        searchMeta: {          // 搜索过程元信息
          queriesGenerated, resultsFound, opinionsExtracted, sourcesUnique
        }
      }
    }

开闭原则：不修改 fact_check.py / hotspots.py 等既有路由。
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from src.main.python.api.deps import verify_internal_token
from src.main.python.api.schemas import ApiResponse
from src.main.python.opinion import (
    OpinionMonitorAgent,
    OpinionAnalyzeRequest,
    OpinionDetailData,
    OpinionReport,
    OpinionSearchMeta,
)

router = APIRouter(
    prefix="/internal/v1",
    tags=["opinion"],
    dependencies=[Depends(verify_internal_token)],
)

# 全局单例（避免重复初始化 LLM 客户端）
_opinion_agent: OpinionMonitorAgent | None = None


def _get_agent() -> OpinionMonitorAgent:
    global _opinion_agent
    if _opinion_agent is None:
        _opinion_agent = OpinionMonitorAgent()
    return _opinion_agent


@router.post(
    "/opinion/analyze",
    response_model=ApiResponse[OpinionDetailData],
    summary="舆论监测分析 — 搜索公众观点、立场聚类、生成 HTML 报告",
)
def analyze_opinion(req: OpinionAnalyzeRequest) -> ApiResponse[OpinionDetailData]:
    """对指定事件进行舆论监测分析。

    流程：
    ① 生成多角度搜索查询（支持方/反对方/中立/情感/后续）
    ② 批量搜索（复用 search_retrieve_news）
    ③ 逐条观点抽取（stance/sentiment/coreArgument/speakerType）
    ④ 观点聚类（归并为立场簇，去重+统计分布）
    ⑤ 构建舆论画像 + 生成 HTML 报告

    返回完整的结构化数据（portrait + opinions + clusters + report + searchMeta），
    与事实核查接口 FactCheckDetailDBData 保持相同设计层级。
    """
    agent = _get_agent()
    result = agent.analyze(req.event, description=req.description or "")

    data = OpinionDetailData(
        portrait=result["portrait"],
        opinions=result["opinions"],
        clusters=result["clusters"],
        report=OpinionReport(
            reportTitle=f"舆论监测报告 — {req.event}",
            reportContent=result["html"],
            reportFormat="html",
        ),
        searchMeta=OpinionSearchMeta(**result["searchMeta"]),
    )
    return ApiResponse[OpinionDetailData](data=data)


__all__ = ["router"]
