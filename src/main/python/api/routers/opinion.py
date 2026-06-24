"""舆论监测 API 路由。

POST /internal/v1/opinion/analyze — 舆论监测分析

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
    OpinionReportData,
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
    response_model=ApiResponse[OpinionReportData],
    summary="舆论监测分析 — 搜索公众观点、立场聚类、生成 HTML 报告",
)
def analyze_opinion(req: OpinionAnalyzeRequest) -> ApiResponse[OpinionReportData]:
    """对指定事件进行舆论监测分析。

    流程：
    ① 生成多角度搜索查询
    ② 批量搜索（复用 search_retrieve_news）
    ③ 逐条观点抽取（stance/sentiment/coreArgument）
    ④ 观点聚类（归并为立场簇）
    ⑤ 生成 HTML 报告

    返回：
    - portrait: 完整的舆论画像数据（OpinionPortrait）
    - report: HTML 报告（title/content/format）
    """
    agent = _get_agent()
    result = agent.analyze(req.event, description=req.description or "")
    portrait = result["portrait"]

    data = OpinionReportData(
        portrait=portrait,
        report={
            "title": f"舆论监测报告 — {req.event}",
            "content": result["html"],
            "format": "html",
        },
    )
    return ApiResponse[OpinionReportData](data=data)


__all__ = ["router"]
