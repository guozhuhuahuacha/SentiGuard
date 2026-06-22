"""数据库写入器 — 将采集和分析结果写入 MySQL"""
from __future__ import annotations

import datetime
from typing import List, Optional, Tuple

from src.main.python.services.baidu_collector import BaiduHotItem
from src.main.python.services.clusterer import HotEventCluster
from src.main.python.services.db import get_connection


class DbWriter:
    """将采集/分析结果写入 sentiguard 数据库"""

    def __init__(self):
        pass

    # ---------- 采集任务 ----------

    def create_collect_task(self, source_type: str, keyword: str = None) -> int:
        """创建一条采集任务记录，返回任务 ID"""
        sql = """INSERT INTO news_collect_task
                 (task_name, source_type, keyword, status, start_time, total_count, success_count, fail_count)
                 VALUES (%s, %s, %s, 'running', NOW(), 0, 0, 0)"""
        task_name = f"{source_type}-{datetime.datetime.now():%Y%m%d-%H%M%S}"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (task_name, source_type, keyword))
                conn.commit()
                return cur.lastrowid

    def finish_collect_task(self, task_id: int, status: str, total: int, success: int, fail: int, error: str = None):
        """更新采集任务状态"""
        sql = """UPDATE news_collect_task
                 SET status=%s, end_time=NOW(), total_count=%s, success_count=%s, fail_count=%s, error_message=%s
                 WHERE id=%s"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (status, total, success, fail, error, task_id))
                conn.commit()

    # ---------- 新闻入库 ----------

    def insert_news(
        self,
        collect_task_id: int,
        title: str,
        summary: str,
        source_name: str,
        source_url: str,
    ) -> Optional[int]:
        """
        插入一条新闻（跳过重复 URL），返回新闻 ID。
        如果 URL 已存在则返回 None。
        """
        sql = """INSERT IGNORE INTO news
                 (collect_task_id, title, summary, source_name, source_url, publish_time)
                 VALUES (%s, %s, %s, %s, %s, NOW())"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (collect_task_id, title, summary, source_name, source_url))
                conn.commit()
                if cur.lastrowid == 0:
                    return None
                return cur.lastrowid

    # ---------- 热点事件 ----------

    def insert_hot_event(
        self,
        event_title: str,
        heat_score: float,
        sentiment_label: str,
        news_count: int,
        news_ids: List[int],
    ) -> int:
        """创建热点事件并关联新闻，返回热点 ID"""
        risk = "low"
        if sentiment_label == "neg":
            risk = "high" if news_count >= 5 else "medium"
        elif sentiment_label == "neu" and news_count >= 10:
            risk = "medium"

        sql_event = """INSERT INTO hot_event
                       (event_title, event_summary, heat_score, risk_level, sentiment_label, news_count, start_time)
                       VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql_event,
                    (event_title, f"{event_title}（共{news_count}条相关新闻）", heat_score, risk, sentiment_label, news_count),
                )
                conn.commit()
                event_id = cur.lastrowid

                # 关联新闻
                if news_ids:
                    sql_link = """INSERT IGNORE INTO hot_event_news (hot_event_id, news_id, relevance_score)
                                  VALUES (%s, %s, %s)"""
                    for nid in news_ids:
                        cur.execute(sql_link, (event_id, nid, 1.0))
                    conn.commit()
                return event_id

    # ---------- 情感分析 ----------

    def insert_sentiment(
        self,
        hot_event_id: int,
        pos_count: int,
        neu_count: int,
        neg_count: int,
        label: str,
    ):
        """写入热点情感分析结果"""
        total = max(pos_count + neu_count + neg_count, 1)
        sql = """INSERT INTO sentiment_analysis
                 (hot_event_id, positive_count, neutral_count, negative_count,
                  positive_ratio, neutral_ratio, negative_ratio, sentiment_label, analysis_time)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        hot_event_id,
                        pos_count, neu_count, neg_count,
                        round(pos_count / total * 100, 2),
                        round(neu_count / total * 100, 2),
                        round(neg_count / total * 100, 2),
                        label,
                    ),
                )
                conn.commit()

    # ---------- 关键词 ----------

    def insert_keywords(self, hot_event_id: int, keywords: List[Tuple[str, float]]):
        """写入热点关键词"""
        sql = """INSERT INTO topic_keyword (hot_event_id, keyword, weight, rank_no)
                 VALUES (%s, %s, %s, %s)"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                for rank, (word, weight) in enumerate(keywords, start=1):
                    cur.execute(sql, (hot_event_id, word, round(weight, 4), rank))
                conn.commit()

    # ---------- 查询 ----------

    def get_recent_news_ids(self, limit: int = 100) -> List[int]:
        """获取最近入库的新闻 ID 列表"""
        sql = "SELECT id FROM news WHERE is_deleted=0 ORDER BY create_time DESC LIMIT %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (limit,))
                return [row[0] for row in cur.fetchall()]

    def get_news_titles_summaries(self, ids: List[int]) -> List[Tuple[int, str, str]]:
        """批量获取新闻标题和摘要"""
        if not ids:
            return []
        placeholders = ",".join(["%s"] * len(ids))
        sql = f"SELECT id, title, summary FROM news WHERE id IN ({placeholders})"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, ids)
                return [(row[0], row[1], row[2] or "") for row in cur.fetchall()]
