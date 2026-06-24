"""舆论监测模块。

不修改 api/schemas.py、report/generator.py、report/renderers/html.py 中任何既有代码。
"""
from .monitor_agent import OpinionMonitorAgent
from .generator import OpinionReportGenerator
from .schemas import (
    OpinionItem,
    StanceCluster,
    OpinionPortrait,
    OpinionAnalyzeRequest,
    OpinionReportData,
)

__all__ = [
    "OpinionMonitorAgent",
    "OpinionReportGenerator",
    "OpinionItem",
    "StanceCluster",
    "OpinionPortrait",
    "OpinionAnalyzeRequest",
    "OpinionReportData",
]
