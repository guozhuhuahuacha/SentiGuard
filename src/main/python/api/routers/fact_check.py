"""F1 POST /internal/v1/fact-check — 事实核查（简易版，当前为 mock 实现）。

响应体仅包含三个字段：isTrue / conclusion / explanation。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from src.main.python.api.deps import verify_internal_token
from src.main.python.api.schemas import (
    ApiResponse,
    FactCheckData,
    FactCheckRequest,
)

router = APIRouter(
    prefix="/internal/v1",
    tags=["fact-check"],
    dependencies=[Depends(verify_internal_token)],
)


@router.post(
    "/fact-check",
    response_model=ApiResponse[FactCheckData],
    summary="事实核查（简易版，仅返回真假/结论/解释）",
)
def fact_check(req: FactCheckRequest) -> ApiResponse[FactCheckData]:
    # ----- mock 逻辑 -----
    # 为了便于后端联调，根据 claim 中的关键词返回不同的预设结果。
    # 真实实现应当调用 FactAgent，并将结果归并为 isTrue 布尔 + 文本字段。
    is_true, conclusion, explanation = _mock_verdict(req.claim.strip())

    data = FactCheckData(
        isTrue=is_true,
        conclusion=conclusion,
        explanation=explanation,
    )
    return ApiResponse[FactCheckData](data=data)


def _mock_verdict(claim: str) -> tuple[bool, str, str]:
    lowered = claim.lower()
    if "假" in claim or "谣言" in claim or "false" in lowered:
        return (
            False,
            "声明虚假：与多方权威信息不符。",
            "经检索权威媒体与官方公告，未发现支持该声明的证据，且存在多条直接反驳的报道，因此判定该声明为虚假。",
        )
    if "部分" in claim or "partly" in lowered:
        return (
            False,
            "声明部分属实，但存在与事实不符的细节，整体归并为虚假。",
            "声明的主要事件部分属实，但其中关于时间或人物的描述与官方通报存在出入。当前简易版以最接近的布尔值表达，因此判定为 false。",
        )
    if "不确定" in claim or "未知" in claim:
        return (
            False,
            "证据不足，无法支持该声明，归并为虚假。",
            "在可用的检索结果与新闻数据库中未能找到充分证据支持该声明，建议持续关注后续报道。当前简易版以最接近的布尔值表达，因此判定为 false。",
        )
    return (
        True,
        "声明真实：多个权威来源相互印证。",
        "经检索多个权威来源（如官方通告、主流媒体），均确认该声明所描述的内容真实存在，未发现反驳证据，因此判定为真实。",
    )
