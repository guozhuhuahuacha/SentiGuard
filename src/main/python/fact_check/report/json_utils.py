"""鲁棒的 JSON 解析工具 — 修复 LLM 输出中常见的 JSON 格式问题。

借鉴 BettaFish RobustJSONParser 的设计思路，提供：
1. 自动清理 markdown 代码块标记
2. 移除尾随逗号
3. 转义字符串中的控制字符
4. 平衡括号（补齐缺失的闭合括号）
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional


def robust_json_loads(raw: str, context: str = "JSON") -> Optional[Dict[str, Any]]:
    """尝试多种策略解析 LLM 返回的 JSON 文本。

    返回 dict 或 None（全部策略失败时）。
    """
    if not raw or not raw.strip():
        return None

    candidates = _build_candidates(raw)

    for i, candidate in enumerate(candidates):
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue

    return None


def _build_candidates(raw: str):
    """构造多个候选 JSON 字符串，覆盖不同清理策略。"""
    cleaned = _clean_response(raw)
    candidates = [cleaned]

    # 本地修复版本
    repaired = _apply_local_repairs(cleaned)
    if repaired != cleaned:
        candidates.append(repaired)

    return candidates


def _clean_response(raw: str) -> str:
    """清理 LLM 响应：去除 markdown 代码块标记。"""
    text = raw.strip()

    # 提取 ```json ... ``` 包裹的内容
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()

    # 移除首尾的 ``` 标记
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    # 尝试提取第一个 { ... } 完整结构
    return _extract_first_object(text.strip())


def _extract_first_object(text: str) -> str:
    """从文本中提取第一个完整的 JSON 对象。"""
    start = text.find("{")
    if start == -1:
        return text

    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    return text[start:] if start < len(text) else text


def _apply_local_repairs(text: str) -> str:
    """应用本地修复策略。"""
    repaired = text

    # 1. 移除尾随逗号（,后面紧跟着 } 或 ]）
    repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)

    # 2. 转义字符串中的控制字符
    repaired = _escape_control_chars(repaired)

    # 3. 平衡括号
    repaired = _balance_brackets(repaired)

    return repaired


def _escape_control_chars(text: str) -> str:
    """将字符串字面量中的裸换行/制表符转义。"""
    result = []
    in_string = False
    escaped = False
    control_map = {"\n": "\\n", "\r": "\\r", "\t": "\\t"}

    for ch in text:
        if escaped:
            result.append(ch)
            escaped = False
            continue
        if ch == "\\":
            result.append(ch)
            escaped = True
            continue
        if ch == '"':
            result.append(ch)
            in_string = not in_string
            continue
        if in_string and ch in control_map:
            result.append(control_map[ch])
            continue
        result.append(ch)

    return "".join(result)


def _balance_brackets(text: str) -> str:
    """补齐缺失的闭合括号。"""
    stack = []
    result = []
    in_string = False
    escaped = False
    opener_map = {"{": "}", "[": "]"}

    for ch in text:
        if escaped:
            result.append(ch)
            escaped = False
            continue
        if ch == "\\":
            result.append(ch)
            escaped = True
            continue
        if ch == '"':
            result.append(ch)
            in_string = not in_string
            continue
        if in_string:
            result.append(ch)
            continue
        if ch in "{[":
            stack.append(ch)
            result.append(ch)
        elif ch in "}]":
            if stack and ((ch == "}" and stack[-1] == "{") or (ch == "]" and stack[-1] == "[")):
                stack.pop()
                result.append(ch)
            # 不匹配的闭括号直接丢弃
        else:
            result.append(ch)

    # 补齐未闭合的括号
    while stack:
        result.append(opener_map[stack.pop()])

    return "".join(result)


__all__ = ["robust_json_loads"]
