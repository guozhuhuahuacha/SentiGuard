"""舆论监测主 Agent — 5 步流水线。

流程：
  ① 观点搜索查询生成（LLM 生成多角度搜索词）
  ② 批量搜索（复用 search_service / search_retrieve_news）
  ③ 逐条观点抽取（LLM 从搜索结果提取 stance/sentiment/coreArgument）
  ④ 观点聚类与去重（LLM 归并相似观点为立场簇）
  ⑤ 舆论画像 + HTML 报告生成

开闭原则：
- 不修改 main_agent.py / reflective_fact_agent.py 等既有 Agent
- 复用 search_service（搜索）、create_chat_model（LLM）、HTMLRenderer（报告框架）
- 所有 LLM prompt 独立在 opinion/prompts/ 中
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.main.python.llms import create_chat_model
from src.main.python.tools.retrieve import search_retrieve_news
from .schemas import (
    OpinionItem,
    StanceCluster,
    OpinionPortrait,
)

logger = logging.getLogger("opinion.monitor")


# ============================================================
# 鲁棒 JSON 解析（内联，避免循环导入）
# ============================================================
def _robust_json_loads(raw: str, context: str = "JSON") -> Optional[Dict[str, Any]]:
    if not raw or not raw.strip():
        return None
    text = raw.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        text = m.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        text = text[start:end + 1]
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return None


# ============================================================
# OpinionMonitorAgent
# ============================================================
class OpinionMonitorAgent:
    """舆论监测主 Agent。

    用法:
        agent = OpinionMonitorAgent()
        result = agent.analyze("武汉大学图书馆事件", description="补充描述（可选）")
        # result.portrait  -> OpinionPortrait
        # result.html      -> str (完整 HTML 报告)
    """

    def __init__(
        self,
        model_name: str = "doubao/doubao-seed-2-0-mini-260428",
        temperature: float = 0.3,
    ):
        self.model_name = model_name
        self.llm = create_chat_model(
            model_name=model_name,
            temperature=temperature,
        )

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM 并返回文本响应。"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.llm.invoke(messages)
        return response.content

    # ================================================================
    # 步骤 ①：观点搜索查询生成
    # ================================================================
    def _generate_search_queries(self, event: str, description: str = "") -> List[Dict[str, str]]:
        """LLM 生成多角度搜索查询。"""
        from .prompts.opinion_search import SYSTEM_PROMPT_OPINION_SEARCH

        user_input = json.dumps({
            "event": event,
            "description": description or "",
        }, ensure_ascii=False)

        try:
            response = self._call_llm(SYSTEM_PROMPT_OPINION_SEARCH, user_input)
            result = _robust_json_loads(response, "观点搜索查询")
            if result:
                queries = result.get("searchQueries", [])
                logger.info("搜索查询生成: %d 个", len(queries))
                return queries
        except Exception as e:
            logger.warning("搜索查询生成失败: %s", e)

        # 降级：简单模板
        return [
            {"query": f"{event} 网友 看法", "dimension": "直接看法", "reasoning": "降级生成"},
            {"query": f"{event} 评论 争议", "dimension": "反对方", "reasoning": "降级生成"},
            {"query": f"{event} 分析 观点", "dimension": "中立分析", "reasoning": "降级生成"},
            {"query": f"{event} 支持", "dimension": "支持方", "reasoning": "降级生成"},
        ]

    # ================================================================
    # 步骤 ②：批量搜索
    # ================================================================
    def _batch_search(self, queries: List[Dict[str, str]], dataset: str = "fever") -> List[Dict[str, Any]]:
        """对每个查询调用搜索工具，合并去重。"""
        seen_urls = set()
        all_results = []

        for q in queries[:6]:  # 最多 6 个查询
            query_text = q.get("query", "")
            if not query_text:
                continue
            try:
                results = search_retrieve_news.invoke({
                    "query": query_text,
                    "dataset": dataset,
                })
                if isinstance(results, str):
                    results = json.loads(results)
                if isinstance(results, list):
                    for item in results:
                        url = item.get("url", "")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            all_results.append(item)
                logger.info("搜索 '%s': %d 条结果（去重后累计 %d 条）",
                            query_text[:30], len(results) if isinstance(results, list) else 0, len(all_results))
            except Exception as e:
                logger.warning("搜索 '%s' 失败: %s", query_text[:30], e)

        return all_results

    # ================================================================
    # 步骤 ③：逐条观点抽取
    # ================================================================
    def _extract_opinions(self, search_results: List[Dict[str, Any]]) -> List[OpinionItem]:
        """对每条搜索结果调用 LLM 抽取观点立场。"""
        from .prompts.opinion_extraction import SYSTEM_PROMPT_OPINION_EXTRACTION

        opinions = []
        total = len(search_results)

        for i, item in enumerate(search_results, 1):
            data_packet = {
                "sourceTitle": item.get("title", ""),
                "sourceUrl": item.get("url", ""),
                "sourceDomain": item.get("source", ""),
                "snippet": item.get("snippet", ""),
                "fullContent": item.get("content", "")[:1500],
            }

            user_prompt = json.dumps(data_packet, ensure_ascii=False)

            try:
                response = self._call_llm(SYSTEM_PROMPT_OPINION_EXTRACTION, user_prompt)
                result = _robust_json_loads(response, f"观点抽取 #{i}")
                if result:
                    opinions.append(OpinionItem(
                        sourceTitle=data_packet["sourceTitle"],
                        sourceUrl=data_packet["sourceUrl"],
                        sourceDomain=data_packet["sourceDomain"],
                        stance=result.get("stance", "neutral"),
                        sentiment=result.get("sentiment", "neutral"),
                        coreArgument=result.get("coreArgument", ""),
                        keywords=result.get("keywords", []),
                        speakerType=result.get("speakerType", "普通网友"),
                        excerptText=result.get("excerptText", ""),
                    ))
                    logger.info("观点抽取 %d/%d: stance=%s sentiment=%s",
                                i, total, result.get("stance"), result.get("sentiment"))
            except Exception as e:
                logger.warning("观点抽取 %d/%d 失败: %s", i, total, e)

        return opinions

    # ================================================================
    # 步骤 ④：观点聚类
    # ================================================================
    def _cluster_opinions(
        self, event: str, opinions: List[OpinionItem]
    ) -> Dict[str, Any]:
        """LLM 聚类归并观点为立场簇。"""
        from .prompts.opinion_clustering import SYSTEM_PROMPT_OPINION_CLUSTERING

        if len(opinions) < 2:
            return {
                "clusters": [],
                "stanceDistribution": {"support": 0, "oppose": 0, "neutral": 1.0},
                "sentimentDistribution": {"positive": 0, "negative": 0, "neutral": 1.0},
                "riskLevel": "low",
                "riskNotes": ["观点数量不足，无法有效聚类"],
            }

        opinions_json = [
            {
                "stance": o.stance,
                "sentiment": o.sentiment,
                "coreArgument": o.coreArgument,
                "keywords": o.keywords,
                "speakerType": o.speakerType,
                "sourceTitle": o.sourceTitle,
                "excerptText": o.excerptText,
            }
            for o in opinions
        ]

        user_prompt = json.dumps({
            "eventName": event,
            "opinions": opinions_json,
        }, ensure_ascii=False, indent=2)

        try:
            response = self._call_llm(SYSTEM_PROMPT_OPINION_CLUSTERING, user_prompt)
            result = _robust_json_loads(response, "观点聚类")
            if result:
                return result
        except Exception as e:
            logger.warning("观点聚类失败: %s", e)

        return {
            "clusters": [],
            "stanceDistribution": {"support": 0, "oppose": 0, "neutral": 1.0},
            "sentimentDistribution": {"positive": 0, "negative": 0, "neutral": 1.0},
            "riskLevel": "low",
            "riskNotes": ["聚类失败"],
        }

    # ================================================================
    # 步骤 ⑤：舆论画像汇总
    # ================================================================
    def _build_portrait(
        self, event: str, opinions: List[OpinionItem], clustering: Dict[str, Any]
    ) -> OpinionPortrait:
        """组装 OpinionPortrait + LLM 生成叙事总结。"""
        from .prompts.opinion_clustering import SYSTEM_PROMPT_OPINION_SUMMARY

        # 统计
        total = len(opinions)
        unique_sources = len(set(o.sourceDomain for o in opinions if o.sourceDomain))

        # 聚类结果
        clusters_raw = clustering.get("clusters", [])
        clusters = [
            StanceCluster(
                clusterId=c.get("clusterId", i + 1),
                stance=c.get("stance", "neutral"),
                label=c.get("label", ""),
                summary=c.get("summary", ""),
                representativeArguments=c.get("representativeArguments", []),
                opinionCount=c.get("opinionCount", 0),
                speakerBreakdown=c.get("speakerBreakdown", {}),
                sentimentRatio=c.get("sentimentRatio", {}),
                sampleExcerpts=c.get("sampleExcerpts", []),
            )
            for i, c in enumerate(clusters_raw)
        ]

        # LLM 叙事总结
        narrative_summary = ""
        if clusters:
            try:
                summary_input = json.dumps({
                    "eventName": event,
                    "stanceDistribution": clustering.get("stanceDistribution", {}),
                    "sentimentDistribution": clustering.get("sentimentDistribution", {}),
                    "clusters": [
                        {
                            "label": c.label,
                            "summary": c.summary,
                            "representativeArguments": c.representativeArguments,
                            "opinionCount": c.opinionCount,
                        }
                        for c in clusters
                    ],
                    "riskLevel": clustering.get("riskLevel", "low"),
                    "riskNotes": clustering.get("riskNotes", []),
                }, ensure_ascii=False, indent=2)

                response = self._call_llm(SYSTEM_PROMPT_OPINION_SUMMARY, summary_input)
                narrative_summary = response.strip()
            except Exception as e:
                logger.warning("舆论总结生成失败: %s", e)

        return OpinionPortrait(
            eventName=event,
            generatedAt=datetime.now(timezone.utc).isoformat(),
            totalOpinions=total,
            totalSources=unique_sources,
            stanceDistribution=clustering.get("stanceDistribution", {}),
            sentimentDistribution=clustering.get("sentimentDistribution", {}),
            clusters=clusters,
            riskLevel=clustering.get("riskLevel", "low"),
            riskNotes=clustering.get("riskNotes", []),
            narrativeSummary=narrative_summary,
        )

    # ================================================================
    # 主编排
    # ================================================================
    def analyze(self, event: str, description: str = "") -> Dict[str, Any]:
        """执行完整舆论监测流水线。

        Returns:
            {"portrait": OpinionPortrait, "html": str}
        """
        logger.info("=== 舆论监测开始: %s ===", event)

        # ① 搜索查询生成
        queries = self._generate_search_queries(event, description)
        logger.info("步骤①: 生成 %d 个搜索查询", len(queries))

        # ② 批量搜索
        search_results = self._batch_search(queries)
        logger.info("步骤②: 搜索得到 %d 条结果", len(search_results))

        # ③ 观点抽取
        opinions = self._extract_opinions(search_results)
        logger.info("步骤③: 抽取 %d 条观点", len(opinions))

        # ④ 观点聚类
        clustering = self._cluster_opinions(event, opinions)
        logger.info("步骤④: 聚类得到 %d 个立场簇", len(clustering.get("clusters", [])))

        # ⑤ 构建画像
        portrait = self._build_portrait(event, opinions, clustering)

        # ⑥ 生成 HTML 报告
        from .generator import OpinionReportGenerator
        report_gen = OpinionReportGenerator(portrait)
        html = report_gen.generate()

        logger.info("=== 舆论监测完成: %s（风险: %s）===", event, portrait.riskLevel)
        return {"portrait": portrait, "html": html}


__all__ = ["OpinionMonitorAgent"]
