"""热点采集与分析管道 — 编排采集→存储→聚类→情感分析的完整流程"""
from __future__ import annotations

import datetime
import logging
from typing import Dict, List

from src.main.python.services.baidu_collector import BaiduCollector
from src.main.python.services.clusterer import Clusterer
from src.main.python.services.db_writer import DbWriter
from src.main.python.services.sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class HotspotPipeline:
    """一站式热点采集与分析管道"""

    def __init__(self):
        self.collector = BaiduCollector()
        self.clusterer = Clusterer(similarity_threshold=0.35)
        self.analyzer = SentimentAnalyzer()
        self.writer = DbWriter()

    def run(self, source: str = "BAIDU") -> Dict:
        """
        执行一次完整的采集→分析→存储流程。

        返回统计信息：
            {
                "task_id": int,
                "news_saved": int,
                "news_skipped": int,
                "hot_events": int,
                "hotspots": [...]
            }
        """
        logger.info(f"========== 开始 {source} 采集 ==========")
        task_id = self.writer.create_collect_task(source.upper())

        # ---- 1. 采集新闻 ----
        try:
            items = self.collector.fetch()
            logger.info(f"采集到 {len(items)} 条百度热搜")
        except Exception as e:
            self.writer.finish_collect_task(task_id, "failed", 0, 0, 0, str(e))
            raise RuntimeError(f"采集失败: {e}")

        # ---- 2. 新闻入库 ----
        saved = 0
        skipped = 0
        saved_news_ids: List[int] = []
        saved_news_titles: List[str] = []
        saved_news_summaries: List[str] = []

        for item in items:
            nid = self.writer.insert_news(
                collect_task_id=task_id,
                title=item.title,
                summary=item.summary or item.title,
                source_name=f"百度热搜-{source}",
                source_url=item.url or f"https://www.baidu.com/s?wd={item.title}",
            )
            if nid:
                saved += 1
                saved_news_ids.append(nid)
                saved_news_titles.append(item.title)
                saved_news_summaries.append(item.summary or "")
            else:
                skipped += 1

        logger.info(f"新闻入库: 新增 {saved} 条, 跳过(重复) {skipped} 条")
        self.writer.finish_collect_task(task_id, "success", len(items), saved, skipped)

        # ---- 3. 热点聚类 ----
        clusters = self.clusterer.cluster(saved_news_titles, saved_news_summaries)
        logger.info(f"聚类结果: {len(clusters)} 个热点事件")

        # ---- 4. 情感分析 + 入库 ----
        hotspots = []
        for cluster in clusters:
            cluster_titles = [saved_news_titles[i] for i in cluster.news_indices]
            combined_text = " ".join(cluster_titles)

            # 情感分析
            sentiments = [self.analyzer.analyze(t) for t in cluster_titles]
            pos_c = sum(1 for s in sentiments if s["label"] == "pos")
            neg_c = sum(1 for s in sentiments if s["label"] == "neg")
            neu_c = sum(1 for s in sentiments if s["label"] == "neu")
            overall = "neg" if neg_c > pos_c else ("pos" if pos_c > neg_c else "neu")

            # 热度（基于相关新闻数量，映射到 0-100）
            heat_score = min(100.0, len(cluster.news_indices) * 8.0 + 20.0)

            # 关键词提取
            keywords = self.clusterer.extract_keywords(cluster_titles, top_k=5)

            # 获取关联的 news_id
            cluster_news_ids = [saved_news_ids[i] for i in cluster.news_indices]

            # 写入热点事件
            event_id = self.writer.insert_hot_event(
                event_title=cluster.event_name,
                heat_score=heat_score,
                sentiment_label=overall,
                news_count=len(cluster.news_indices),
                news_ids=cluster_news_ids,
            )

            # 写入情感分析
            self.writer.insert_sentiment(event_id, pos_c, neu_c, neg_c, overall)

            # 写入关键词
            self.writer.insert_keywords(event_id, keywords)

            hotspots.append({
                "rank": len(hotspots) + 1,
                "name": cluster.event_name,
                "heat": round(heat_score, 1),
                "news_count": len(cluster.news_indices),
                "sentiment": {
                    "label": overall,
                    "pos_count": pos_c,
                    "neg_count": neg_c,
                    "neu_count": neu_c,
                },
                "keywords": [{"word": w, "weight": wt} for w, wt in keywords],
            })

        logger.info(f"========== 采集完成: {len(hotspots)} 个热点 ==========")
        return {
            "task_id": task_id,
            "source": source,
            "news_collected": len(items),
            "news_saved": saved,
            "news_skipped": skipped,
            "hot_events": len(hotspots),
            "hotspots": hotspots,
            "generated_at": datetime.datetime.now().isoformat(),
        }
