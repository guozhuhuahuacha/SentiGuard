import json
import requests
from dotenv import load_dotenv
import os
from typing import Dict, Optional

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# LLM 调用已经迁移到 src/llms 抽象层（开闭原则）：
#   BaseLLM        -> 抽象基类
#   OpenAILLM      -> OpenAI 实现
#   OllamaLLM      -> Ollama 实现
#   DoubaoLLM      -> 豆包（火山引擎方舟）实现
# 使用统一入口：
#   from src.llms import get_llm_provider, create_chat_model, invoke_with_json
from src.main.python.providers.llm import invoke_with_json


def google_top_snippet(question: str) -> str:
    """调用 Serper 获取首个 snippet 文本。"""
    url = "https://google.serper.dev/search"
    try:
        payload = json.dumps({"q": question, "num": 1})
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, data=payload)
        result = response.json()
        if "organic" in result and result["organic"]:
            snippet = result["organic"][0].get("snippet")
            if snippet:
                return snippet
    except requests.RequestException:
        raise Exception("SERPER_API_KEY exhausted. No results retrieved.")
    return ""


# ----------------------------------------------------------------------
# 兼容封装：为了不破坏 experiments 与 evaluate 的既有调用方式，
# 保留 use_gpt / use_ollama 作为薄包装，内部统一走 LLM 抽象层。
# 新增模型（例如豆包）时直接调用 invoke_with_json 即可。
# ----------------------------------------------------------------------
def _chat_json_via_llm(model: str, prompt: str, format_output: Optional[Dict] = None) -> Dict:
    return invoke_with_json(
        model_name=model,
        prompt=prompt,
        json_schema=format_output if format_output else None,
        provider=None,  # 让工厂按模型名自动推断
    )


def use_ollama(model: str, prompt: str, format_output: Optional[Dict] = None) -> Dict:
    """对 Ollama 的向后兼容包装；实际通过 BaseLLM 抽象调用。"""
    raw_model = model
    if not raw_model.lower().startswith("ollama/") and "ollama" not in raw_model.lower():
        raw_model = f"ollama/{model}"
    return _chat_json_via_llm(raw_model, prompt, format_output)


def use_gpt(model: str, prompt: str, format_output: Optional[Dict] = None) -> Dict:
    """对 OpenAI 的向后兼容包装；实际通过 BaseLLM 抽象调用。"""
    return _chat_json_via_llm(model, prompt, format_output)
