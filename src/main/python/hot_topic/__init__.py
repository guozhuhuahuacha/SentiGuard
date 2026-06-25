"""向后兼容层 — 热点挖掘模块已拆分。

数据源获取 → providers/data/
    THUCNewsLoader, GDELTClient, RSSClient, BaseDataSource, DOC_COLUMNS, merge_sources

BERTopic 建模 → topic_model/
    config, model_config, trainer, preprocessing, modeling, storage, visualization

新代码请使用：
    from src.main.python.providers.data import THUCNewsLoader, GDELTClient
    from src.main.python.topic_model.modeling import build_chinese_bertopic
"""
__version__ = "0.1.0"

from src.main.python.providers.data import (  # noqa: F401
    BaseDataSource, DOC_COLUMNS, merge_sources,
    GDELTClient, RSSClient, THUCNewsLoader,
)
from src.main.python.topic_model import config  # noqa: F401
from src.main.python.topic_model.modeling import (  # noqa: F401
    build_chinese_bertopic, train_topic_model,
    save_topic_model, load_topic_model,
    get_topic_summary, get_topic_table,
)
from src.main.python.topic_model.storage import write_csv  # noqa: F401
