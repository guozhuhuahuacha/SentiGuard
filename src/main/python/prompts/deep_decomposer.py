"""向后兼容层 — 重导出到 fact_check.decomposer。

DeepClaimDecomposer 已迁移至 fact_check/decomposer.py。
新代码请使用：
    from src.main.python.fact_check.decomposer import DeepClaimDecomposer
"""
from src.main.python.fact_check.decomposer import (  # noqa: F401
    DeepClaimDecomposer,
    DEFAULT_DEEP_REFLECTION_COUNT,
)
