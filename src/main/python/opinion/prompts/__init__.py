"""舆论监测模块 — Prompts。

不修改 prompts/ 目录下任何既有文件。
"""
from .opinion_search import SYSTEM_PROMPT_OPINION_SEARCH
from .opinion_extraction import SYSTEM_PROMPT_OPINION_EXTRACTION
from .opinion_clustering import (
    SYSTEM_PROMPT_OPINION_CLUSTERING,
    SYSTEM_PROMPT_OPINION_SUMMARY,
)

__all__ = [
    "SYSTEM_PROMPT_OPINION_SEARCH",
    "SYSTEM_PROMPT_OPINION_EXTRACTION",
    "SYSTEM_PROMPT_OPINION_CLUSTERING",
    "SYSTEM_PROMPT_OPINION_SUMMARY",
]
