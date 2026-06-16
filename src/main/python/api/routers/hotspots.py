"""H1 GET /internal/v1/hotspots — 热点列表接口（当前为 mock 实现）。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.main.python.api.deps import verify_internal_token
from src.main.python.api.schemas import (
    ApiResponse,
    Hotspot,
    HotspotData,
    Keyword,
    Sentiment,
    SentimentDistribution,
)

router = APIRouter(
    prefix="/internal/v1",
    tags=["hotspots"],
    dependencies=[Depends(verify_internal_token)],
)


def _iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Mock 数据
# ---------------------------------------------------------------------------
_MOCK_HOTSPOTS: list[Hotspot] = [
    Hotspot(
        rank=1,
        name="某某事件",
        heat=87.4,
        keywords=[
            Keyword(word="事件", weight=0.42),
            Keyword(word="官方", weight=0.31),
            Keyword(word="通报", weight=0.27),
            Keyword(word="调查", weight=0.21),
            Keyword(word="回应", weight=0.18),
        ],
        sentiment=Sentiment(
            label="neg",
            score=-0.62,
            distribution=SentimentDistribution(pos=0.15, neg=0.70, neu=0.15),
        ),
    ),
    Hotspot(
        rank=2,
        name="另一个热点",
        heat=72.1,
        keywords=[
            Keyword(word="政策", weight=0.38),
            Keyword(word="改革", weight=0.29),
            Keyword(word="试点", weight=0.22),
            Keyword(word="推进", weight=0.17),
            Keyword(word="落地", weight=0.12),
        ],
        sentiment=Sentiment(
            label="neu",
            score=0.05,
            distribution=SentimentDistribution(pos=0.30, neg=0.25, neu=0.45),
        ),
    ),
    Hotspot(
        rank=3,
        name="科技动态",
        heat=65.8,
        keywords=[
            Keyword(word="AI", weight=0.45),
            Keyword(word="模型", weight=0.33),
            Keyword(word="发布", weight=0.25),
            Keyword(word="开源", weight=0.20),
            Keyword(word="性能", weight=0.15),
        ],
        sentiment=Sentiment(
            label="pos",
            score=0.48,
            distribution=SentimentDistribution(pos=0.60, neg=0.10, neu=0.30),
        ),
    ),
]


@router.get(
    "/hotspots",
    response_model=ApiResponse[HotspotData],
    summary="获取热点列表（按热度排序）",
)
def list_hotspots(
    limit: int = Query(20, ge=1, le=100, description="返回热点数量上限"),
    from_: str | None = Query(None, alias="from", description="时间窗口起点 ISO8601"),
    to: str | None = Query(None, description="时间窗口终点 ISO8601"),
    topK: int = Query(5, ge=1, le=20, description="每个热点返回前 K 个关键词"),
) -> ApiResponse[HotspotData]:
    now = datetime.now(timezone.utc)
    window_to = _parse_iso(to) if to else now
    window_from = _parse_iso(from_) if from_ else window_to - timedelta(hours=24)

    if window_from >= window_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 40001, "message": "`from` must be earlier than `to`"},
        )

    # 按 heat 排序后截取 limit；并对每条热点截取 topK 个关键词
    sorted_hotspots = sorted(_MOCK_HOTSPOTS, key=lambda h: h.heat, reverse=True)
    truncated = []
    for idx, h in enumerate(sorted_hotspots[:limit], start=1):
        truncated.append(
            h.model_copy(update={"rank": idx, "keywords": h.keywords[:topK]})
        )

    data = HotspotData(
        generatedAt=_iso_utc(now),
        windowFrom=_iso_utc(window_from),
        windowTo=_iso_utc(window_to),
        hotspots=truncated,
    )
    return ApiResponse[HotspotData](data=data)


def _parse_iso(value: str) -> datetime:
    try:
        # 兼容 "Z" 后缀
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 40001, "message": f"invalid datetime: {value}"},
        ) from exc
