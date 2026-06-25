"""事实核查报告 IR Schema — 结构化中间表示。

定义报告内容的结构化 block 类型体系，借鉴 BettaFish 的设计思路，
但针对事实核查场景做了定制（如 evidenceCard 类型）。
"""

from __future__ import annotations

from typing import Any, Dict, List

# ====== Block 类型常量 ======

BLOCK_HEADING = "heading"
BLOCK_PARAGRAPH = "paragraph"
BLOCK_LIST = "list"
BLOCK_TABLE = "table"
BLOCK_CALLOUT = "callout"
BLOCK_KPI_GRID = "kpiGrid"
BLOCK_BLOCKQUOTE = "blockquote"
BLOCK_EVIDENCE_CARD = "evidenceCard"
BLOCK_HR = "hr"

# 所有合法的 block 类型
ALL_BLOCK_TYPES = [
    BLOCK_HEADING,
    BLOCK_PARAGRAPH,
    BLOCK_LIST,
    BLOCK_TABLE,
    BLOCK_CALLOUT,
    BLOCK_KPI_GRID,
    BLOCK_BLOCKQUOTE,
    BLOCK_EVIDENCE_CARD,
    BLOCK_HR,
]

# 每个 block 类型必需的字段
BLOCK_REQUIRED_FIELDS: Dict[str, List[str]] = {
    BLOCK_HEADING:     ["level", "text", "anchor"],
    BLOCK_PARAGRAPH:   ["inlines"],       # inlines: [{text, marks?[{type}]}]
    BLOCK_LIST:        ["listType", "items"],  # ordered/bullet
    BLOCK_TABLE:       ["rows"],          # rows: [{cells: [{text}]}]
    BLOCK_CALLOUT:     ["tone", "blocks"],    # info/warning/success/danger
    BLOCK_KPI_GRID:    ["items"],         # items: [{label, value, tone?}]
    BLOCK_BLOCKQUOTE:  ["text"],
    BLOCK_EVIDENCE_CARD: ["claimOrder", "title", "content", "source", "relationType"],
    BLOCK_HR:          [],
}

# 合法 callout tone 值
CALLOUT_TONES = ["info", "warning", "success", "danger"]

# 合法 list 类型
LIST_TYPES = ["ordered", "bullet"]

# KPI tone 值
KPI_TONES = ["good", "bad", "neutral"]

# 证据论辩关系
RELATION_TYPES = ["support", "attack", "neutral"]

# ====== 辅助验证函数 ======


def validate_block(block: Any) -> List[str]:
    """校验单个 block 是否合法，返回错误列表（空 = 合法）。"""
    errors: List[str] = []
    if not isinstance(block, dict):
        return ["block 必须是 dict"]
    block_type = block.get("type")
    if not block_type:
        return ["block 缺少 type 字段"]
    if block_type not in ALL_BLOCK_TYPES:
        return [f"未知 block type: {block_type}"]
    required = BLOCK_REQUIRED_FIELDS.get(block_type, [])
    for field in required:
        if field not in block or block.get(field) is None:
            errors.append(f"{block_type} 缺少必需字段: {field}")
    return errors


def validate_chapter_ir(chapter: Any) -> List[str]:
    """校验整章 IR 是否合法。"""
    errors: List[str] = []
    if not isinstance(chapter, dict):
        return ["章节必须是 dict"]
    for key in ("chapterId", "title", "anchor", "blocks"):
        if key not in chapter:
            errors.append(f"章节缺少字段: {key}")
    blocks = chapter.get("blocks", [])
    if not isinstance(blocks, list):
        errors.append("blocks 必须是 list")
    else:
        for i, block in enumerate(blocks):
            block_errors = validate_block(block)
            for e in block_errors:
                errors.append(f"blocks[{i}]: {e}")
    return errors


def build_document_ir(
    title: str,
    summary: str,
    kpis: List[Dict[str, Any]],
    key_findings: List[Dict[str, str]],
    chapters: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """组装完整的文档 IR。"""
    return {
        "title": title,
        "summary": summary,
        "kpis": kpis,
        "keyFindings": key_findings,
        "chapters": chapters,
    }


__all__ = [
    "ALL_BLOCK_TYPES",
    "BLOCK_HEADING",
    "BLOCK_PARAGRAPH",
    "BLOCK_LIST",
    "BLOCK_TABLE",
    "BLOCK_CALLOUT",
    "BLOCK_KPI_GRID",
    "BLOCK_BLOCKQUOTE",
    "BLOCK_EVIDENCE_CARD",
    "BLOCK_HR",
    "CALLOUT_TONES",
    "LIST_TYPES",
    "KPI_TONES",
    "RELATION_TYPES",
    "validate_block",
    "validate_chapter_ir",
    "build_document_ir",
]
