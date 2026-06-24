"""
本地测试：运行事实核查 → 生成 HTML 报告 → 保存到文件

用法：
    python src/test/python/test_report_html.py                           # 默认 quick 模式
    python src/test/python/test_report_html.py --mode deep               # 深度核查
    python src/test/python/test_report_html.py --mode quick --claim "声明"
    python src/test/python/test_report_html.py --mode deep --claim "声明" --output report.html
"""
import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv
load_dotenv()

from src.main.python.main_agent import FactAgent
from src.main.python.reflective_fact_agent import ReflectiveFactAgent
from src.main.python.report import ReportGenerator, LLMReportGenerator
from src.main.python.report.models import ReportData as ReportModuleData
from src.main.python.api.schemas import F3Result
from src.main.python.api.routers.fact_check import (
    _extract_claims_from_trace,
    _extract_evidence_items_from_trace,
    parse_verdict_from_results,
    _build_result_conclusion,
)


def run_quick(claim: str, model: str, output: str = ""):
    print(f"🔵 快速核查: {claim}")
    agent = FactAgent(dataset="fever", model_name=model)
    results = agent.process_claim(claim.strip(), recursion_limit=300, verbose=False)

    verdict = parse_verdict_from_results(results)
    label = verdict.get("label", "insufficient_evidence")
    explanation = verdict.get("explanation", "")
    confidence_score = verdict.get("confidenceScore")

    events = agent.trace.events
    claims = _extract_claims_from_trace(events, claim.strip())
    evidence_items = _extract_evidence_items_from_trace(events, claims, label)
    result_label, conclusion = _build_result_conclusion(label, evidence_items)

    f3_result = F3Result(
        resultLabel=result_label,
        confidenceScore=confidence_score,
        conclusion=conclusion,
        analysisDetail=explanation or "经多智能体系统分析完成事实核查。",
        supportCount=sum(1 for ev in evidence_items if ev.relationType == "support"),
        attackCount=sum(1 for ev in evidence_items if ev.relationType == "attack"),
    )

    f3_like = type("F3Like", (), {})()
    f3_like.claims = claims
    f3_like.evidences = evidence_items
    f3_like.result = f3_result
    report_data = ReportModuleData.from_f3_data(
        f3_like,
        run_id=agent.trace.run_id if agent.trace else "",
        generated_at=datetime.now().isoformat(timespec="seconds"),
    )
    report_data.claim = claim.strip()

    print(">>> 生成 HTML 报告...")
    report_result = ReportGenerator(report_data).generate(renderer_name="html")

    _save_report(output or f"quick_report_{agent.trace.run_id}.html", report_result.content)
    _print_summary(result_label, confidence_score, evidence_items)


def run_deep(claim: str, model: str, output: str = ""):
    print(f"🔴 深度核查: {claim}")
    agent = ReflectiveFactAgent(dataset="fever", model_name=model)
    result = agent.process_claim(claim.strip(), recursion_limit=300, verbose=False)

    verdict = result["final_verdict"]
    label = verdict.get("label", "insufficient_evidence")
    explanation = verdict.get("explanation", "")
    confidence_score = verdict.get("confidenceScore")

    events = agent.trace.events
    claims = _extract_claims_from_trace(events, claim.strip())
    trace_evidence = _extract_evidence_items_from_trace(events, claims, label)

    # 合并反思补充证据（去重）
    seen = {(ev.evidenceContent, ev.evidenceUrl) for ev in trace_evidence}
    for ev in result.get("all_evidences", []):
        key = (getattr(ev, "evidenceContent", "") or "", getattr(ev, "evidenceUrl", "") or "")
        if key not in seen:
            seen.add(key)
            trace_evidence.append(ev)

    evidence_items = trace_evidence
    result_label, conclusion = _build_result_conclusion(label, evidence_items)

    f3_result = F3Result(
        resultLabel=result_label,
        confidenceScore=confidence_score,
        conclusion=conclusion,
        analysisDetail=explanation or "经多智能体系统分析完成事实核查。",
        supportCount=sum(1 for ev in evidence_items if ev.relationType == "support"),
        attackCount=sum(1 for ev in evidence_items if ev.relationType == "attack"),
    )

    f3_like = type("F3Like", (), {})()
    f3_like.claims = claims
    f3_like.evidences = evidence_items
    f3_like.result = f3_result
    report_data = ReportModuleData.from_f3_data(
        f3_like,
        run_id=agent.trace.run_id if agent.trace else "",
        generated_at=datetime.now().isoformat(timespec="seconds"),
    )
    report_data.claim = claim.strip()

    print(">>> 生成 LLM 叙事 HTML 报告（约 30-40s）...")
    try:
        report_result = LLMReportGenerator(report_data).generate(renderer_name="html")
    except Exception as e:
        print(f"  LLM 模式失败: {e}")
        print(">>> 降级为数据驱动 HTML 报告...")
        report_result = ReportGenerator(report_data).generate(renderer_name="html")

    _save_report(output or f"deep_report_{agent.trace.run_id}.html", report_result.content)
    _print_summary(result_label, confidence_score, evidence_items)


def _save_report(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告已保存: {os.path.abspath(path)} ({len(content)} 字节)")
    print(f"用浏览器打开该文件查看效果")


def _print_summary(label: str, confidence: int, evidence_items: list):
    support = sum(1 for ev in evidence_items if ev.relationType == "support")
    attack = sum(1 for ev in evidence_items if ev.relationType == "attack")
    print(f"  判定: {label}")
    print(f"  置信度: {confidence}")
    print(f"  证据: {len(evidence_items)} 条（支持 {support} / 反驳 {attack}）")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成 HTML 事实核查报告")
    parser.add_argument("--mode", choices=["quick", "deep"], default="quick",
                        help="quick=快速核查(默认), deep=深度核查")
    parser.add_argument("--claim", default="2024年巴黎奥运会是第33届夏季奥林匹克运动会。")
    parser.add_argument("--model", default="doubao/doubao-seed-2-0-mini-260428")
    parser.add_argument("--output", default="", help="输出文件路径")
    args = parser.parse_args()

    if args.mode == "quick":
        run_quick(args.claim, args.model, args.output)
    else:
        run_deep(args.claim, args.model, args.output)
