"""LLM 提供商适配层

支持的提供商：
    - OpenAI（GPT-4o / GPT-4o-mini 等）
    - Ollama（本地部署，如 qwen2.5）
    - 豆包（字节跳动/火山引擎方舟）

新增提供商：继承 BaseLLM 并在 get_llm_provider 注册表中追加即可。
"""

from src.main.python.providers.llm.base import (
    BaseLLM,
    LLMProvider,
    detect_provider,
    get_llm_provider,
    create_chat_model,
    invoke_with_json,
)

__all__ = [
    "BaseLLM",
    "LLMProvider",
    "detect_provider",
    "get_llm_provider",
    "create_chat_model",
    "invoke_with_json",
]
