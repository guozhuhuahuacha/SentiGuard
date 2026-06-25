"""BERTopic 主题建模模块 — 离线热点挖掘。

topic_model/ 是独立的中文新闻主题建模工具包，基于 BERTopic 端到端管道：

    Embedding (SentenceTransformer) → UMAP 降维 → HDBSCAN 聚类 → c-TF-IDF 主题表示

模块组成：
    config.py          路径 + 数据目录配置
    model_config.py    预设配置（test/small/medium/large/full）+ 停用词
    trainer.py         TopicModelTrainer 训练 API
    preprocessing/     Jieba 分词 + 中文文本清洗
    modeling/          BERTopic 管道（build/train/save/load）
    storage/           CSV 增量写入
    visualization/     Plotly 交互式可视化
    scripts/           CLI 脚本（fetch / train / demo）
    tests/             单元测试（GDELT / THUCNews）

依赖的外部服务（通过 providers/ 获取数据）：
    from src.main.python.providers.data import THUCNewsLoader, GDELTClient
"""
