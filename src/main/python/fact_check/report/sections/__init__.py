"""章节模块入口 — 确保所有章节类被注册"""
from .header import HeaderSection
from .claims import ClaimsSection
from .evidence import EvidenceSection
from .verdict import VerdictSection
from .metadata import MetadataSection

__all__ = [
    "HeaderSection",
    "ClaimsSection",
    "EvidenceSection",
    "VerdictSection",
    "MetadataSection",
]
