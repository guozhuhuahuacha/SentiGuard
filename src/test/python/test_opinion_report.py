"""
本地测试：运行舆论监测 → 生成 HTML 报告 → 保存到文件

用法：
    python src/test/python/test_opinion_report.py
    python src/test/python/test_opinion_report.py --event "武汉大学图书馆事件"
    python src/test/python/test_opinion_report.py --event "武汉大学图书馆事件" --description "补充描述"
    python src/test/python/test_opinion_report.py --event "武汉大学图书馆事件" --output-dir result/
"""
import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from dotenv import load_dotenv
load_dotenv()

from src.main.python.opinion import OpinionMonitorAgent

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../result/test_opinion"))


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _save_report(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ 报告已保存: {os.path.abspath(path)} ({len(content)} 字节)")


def _save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"✅ 数据已保存: {os.path.abspath(path)}")


def run_opinion(event: str, description: str = "", model: str = "doubao/doubao-seed-2-0-mini-260428", output_dir: str = ""):
    print(f"🔍 舆论监测: {event}")
    if description:
        print(f"   补充描述: {description}")

    agent = OpinionMonitorAgent(model_name=model)
    result = agent.analyze(event, description=description)
    portrait = result["portrait"]
    html = result["html"]

    print(f"\n📊 舆论画像:")
    print(f"   收集观点: {portrait.totalOpinions} 条")
    print(f"   覆盖来源: {portrait.totalSources} 个")
    print(f"   立场分布: 支持 {int(portrait.stanceDistribution.get('support', 0) * 100)}% / "
          f"反对 {int(portrait.stanceDistribution.get('oppose', 0) * 100)}% / "
          f"中立 {int(portrait.stanceDistribution.get('neutral', 0) * 100)}%")
    print(f"   情感分布: 正面 {int(portrait.sentimentDistribution.get('positive', 0) * 100)}% / "
          f"负面 {int(portrait.sentimentDistribution.get('negative', 0) * 100)}% / "
          f"中性 {int(portrait.sentimentDistribution.get('neutral', 0) * 100)}%")
    print(f"   风险等级: {portrait.riskLevel}")
    print(f"   立场簇: {len(portrait.clusters)} 个")

    # 保存 HTML 报告
    _save_report(
        os.path.join(output_dir, "opinion_report.html") if output_dir else f"opinion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        html,
    )

    # 保存结构化数据
    portrait_dict = portrait.model_dump()
    _save_json(
        os.path.join(output_dir, "opinion_portrait.json") if output_dir else f"opinion_portrait_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        portrait_dict,
    )

    # 打印各簇详情
    print(f"\n📋 立场簇详情:")
    for c in portrait.clusters:
        stance_labels = {"support": "支持方", "oppose": "反对方", "neutral": "中立"}
        print(f"   [{stance_labels.get(c.stance, c.stance)}] {c.label}（{c.opinionCount}条）")
        for arg in c.representativeArguments[:2]:
            print(f"      • {arg}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="舆论监测 HTML 报告生成")
    parser.add_argument("--event", default="武汉大学图书馆事件", help="事件名称或关键词")
    parser.add_argument("--description", default="", help="事件补充描述（可选）")
    parser.add_argument("--model", default="doubao/doubao-seed-2-0-mini-260428", help="LLM 模型")
    parser.add_argument("--output-dir", default="", help="输出目录（默认为 result/test_opinion/）")
    args = parser.parse_args()

    if args.output_dir:
        out_dir = os.path.abspath(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(RESULTS_DIR, f"opinion_{timestamp}")

    _ensure_dir(out_dir)
    print(f"📁 输出目录: {out_dir}")

    run_opinion(args.event, description=args.description, model=args.model, output_dir=out_dir)
