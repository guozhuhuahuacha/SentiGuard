"""向后兼容层 — 重导出到 providers.llm。

自 2025 年起 LLM 抽象层已迁移至 providers/llm/，
此文件仅为保持旧 import 路径兼容而存在。
新代码请使用：
    from src.main.python.providers.llm import create_chat_model
"""
from src.main.python.providers.llm import (
    BaseLLM,
    LLMProvider,
    get_llm_provider,
    create_chat_model,
    invoke_with_json,
)

__all__ = ["BaseLLM", "LLMProvider", "get_llm_provider", "create_chat_model", "invoke_with_json"]
