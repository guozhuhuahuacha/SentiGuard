"""热点聚类器 — 基于 TF-IDF + 余弦相似度的简单新闻聚类"""
from __future__ import annotations

from typing import List, Set, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class HotEventCluster:
    """一个聚类结果：一个热点事件包含多篇新闻"""

    def __init__(self, event_name: str, news_indices: List[int]):
        self.event_name = event_name
        self.news_indices = news_indices  # 在原始新闻列表中的索引
        self.keywords: List[Tuple[str, float]] = []

    def __repr__(self) -> str:
        return f"HotEvent({self.event_name}, {len(self.news_indices)}篇新闻)"


class Clusterer:
    """
    基于 TF-IDF + 余弦相似度的新闻标题聚类器。

    将多篇新闻标题按相似度聚类为热点事件。
    """

    def __init__(self, similarity_threshold: float = 0.35):
        self.threshold = similarity_threshold

    def cluster(self, titles: List[str], contents: List[str] = None) -> List[HotEventCluster]:
        """
        对标题列表进行聚类，返回热点事件列表。

        Args:
            titles: 新闻标题列表
            contents: 新闻摘要列表（可选，用于增强聚类效果）

        Returns:
            聚类后的热点事件列表
        """
        n = len(titles)
        if n == 0:
            return []
        if n == 1:
            cluster = HotEventCluster(titles[0], [0])
            return [cluster]

        # 合并标题和摘要进行向量化
        texts = titles.copy()
        if contents:
            texts = [f"{t} {c[:200]}" if c else t for t, c in zip(titles, contents)]

        try:
            vectorizer = TfidfVectorizer(
                max_features=500,
                token_pattern=r'(?u)\b\w+\b',
                stop_words=None,
            )
            tfidf = vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf)
        except ValueError:
            # 如果所有文本都是单字或无法分词，每条新闻各自为一个聚类
            return [HotEventCluster(titles[i], [i]) for i in range(n)]

        # 贪心聚类
        visited: Set[int] = set()
        clusters: List[HotEventCluster] = []

        for i in range(n):
            if i in visited:
                continue
            cluster_indices = [i]
            visited.add(i)
            for j in range(i + 1, n):
                if j in visited:
                    continue
                if sim_matrix[i][j] >= self.threshold:
                    cluster_indices.append(j)
                    visited.add(j)
            # 用第一个标题作为事件名
            clusters.append(HotEventCluster(titles[i], cluster_indices))

        # 按新闻数量降序（热度越高的事件排前面）
        clusters.sort(key=lambda c: len(c.news_indices), reverse=True)
        return clusters

    def extract_keywords(
        self, titles: List[str], top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """从标题列表中提取关键词（基于 TF-IDF 权重）"""
        if not titles:
            return []

        try:
            vectorizer = TfidfVectorizer(
                max_features=100,
                token_pattern=r'(?u)\b\w+\b',
            )
            tfidf = vectorizer.fit_transform(titles)
            feature_names = vectorizer.get_feature_names_out()

            # 取平均 TF-IDF 权重最高的 top_k 词
            avg_scores = np.asarray(tfidf.mean(axis=0)).flatten()
            top_indices = avg_scores.argsort()[-top_k:][::-1]

            keywords = []
            for idx in top_indices:
                word = feature_names[idx]
                weight = float(avg_scores[idx])
                # 归一化到 0~1
                max_w = float(avg_scores.max()) if avg_scores.max() > 0 else 1.0
                keywords.append((word, round(weight / max_w, 4)))
            return keywords
        except ValueError:
            # TF-IDF 失败时返回简单的词频统计
            from collections import Counter
            words = " ".join(titles).split()
            counter = Counter(words)
            total = sum(counter.values()) or 1
            return [(w, round(c / total, 4)) for w, c in counter.most_common(top_k)]
