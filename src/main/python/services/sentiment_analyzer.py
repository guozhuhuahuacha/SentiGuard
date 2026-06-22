"""SnowNLP 中文情感分析器"""
from __future__ import annotations

from typing import Dict

from snownlp import SnowNLP


class SentimentAnalyzer:
    """基于 SnowNLP 的中文情感分析器"""

    def analyze(self, text: str) -> Dict[str, object]:
        """
        分析单条文本的情感倾向。

        SnowNLP 返回 0~1 之间的分数，>0.6 为正面，<0.4 为负面，中间为中性。
        将该分数映射为 pos/neg/neu 标签和 -1~1 之间的分数。
        """
        if not text or not text.strip():
            return {"label": "neu", "score": 0.0}

        s = SnowNLP(text.strip())
        raw = s.sentiments

        if raw > 0.6:
            label = "pos"
            score = (raw - 0.6) / 0.4  # 映射到 0~1
        elif raw < 0.4:
            label = "neg"
            score = (raw - 0.4) / 0.4  # 映射到 -1~0
        else:
            label = "neu"
            score = (raw - 0.5) * 2.0  # 映射到 -0.2~0.2 之间

        return {"label": label, "score": round(score, 4)}

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        """批量分析，返回标签列表"""
        return [self.analyze(t) for t in texts]
