"""报告模块 LLM 客户端 — 复用项目已有的 LLM 抽象层"""
from __future__ import annotations

from typing import Optional

from src.main.python.llms import create_chat_model


class ReportLLMClient:
    """报告模块专用的 LLM 客户端封装"""

    def __init__(
        self,
        model_name: str = "doubao/doubao-seed-2-0-mini-260428",
        temperature: float = 0.3,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = create_chat_model(
                model_name=self.model_name,
                temperature=self.temperature,
            )
        return self._llm

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM 生成文本"""
        llm = self._get_llm()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = llm.invoke(messages)
        return response.content


# 全局单例
_global_llm: Optional[ReportLLMClient] = None


def get_report_llm() -> ReportLLMClient:
    global _global_llm
    if _global_llm is None:
        _global_llm = ReportLLMClient()
    return _global_llm
