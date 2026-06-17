"""Data source registry."""
from .base import BaseDataSource, merge_sources
from .gdelt_client import GDELTClient
from .thucnews_loader import THUCNewsLoader
from .rss_client import RSSClient

__all__ = ["BaseDataSource", "GDELTClient", "THUCNewsLoader", "RSSClient", "merge_sources"]
