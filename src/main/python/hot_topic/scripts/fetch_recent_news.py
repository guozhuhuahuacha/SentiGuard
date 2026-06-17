#!/usr/bin/env python3
"""Fetch recent news from multiple sources and save to CSV.

Usage:
    python -m hot_topic.scripts.fetch_recent_news
    python -m hot_topic.scripts.fetch_recent_news --output my_news.csv
    python -m hot_topic.scripts.fetch_recent_news --hours 48
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from hot_topic import config
from hot_topic.data_source import RSSClient, GDELTClient, merge_sources
from hot_topic.storage import write_csv


# Default RSS feeds to fetch
DEFAULT_RSS_FEEDS = [
    # English news
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    # Chinese news - if available
    # "https://rss.sina.com.cn/news/tech.xml",
]


def fetch_all_sources(hours: int = 24, use_gdelt: bool = True, use_rss: bool = True) -> pd.DataFrame:
    """Fetch news from all sources."""
    frames = []

    if use_gdelt:
        logging.info("Fetching from GDELT...")
        try:
            gdelt_client = GDELTClient()
            # GDELT uses timespan string like "24h"
            gdelt_df = gdelt_client.to_dataframe(
                query="sourcelang:chinese OR sourcelang:english",
                timespan=f"{hours}h",
                max_records=250,
            )
            if not gdelt_df.empty:
                gdelt_df['source'] = 'gdelt'
                frames.append(gdelt_df)
                logging.info(f"Got {len(gdelt_df)} articles from GDELT")
        except Exception as e:
            logging.warning(f"Failed to fetch from GDELT: {e}")

    if use_rss:
        logging.info("Fetching from RSS feeds...")
        try:
            rss_client = RSSClient()
            rss_df = rss_client.to_dataframe(
                urls=DEFAULT_RSS_FEEDS,
                max_per_feed=100,
            )
            if not rss_df.empty:
                rss_df['source'] = 'rss'
                frames.append(rss_df)
                logging.info(f"Got {len(rss_df)} articles from RSS")
        except Exception as e:
            logging.warning(f"Failed to fetch from RSS: {e}")

    if not frames:
        logging.warning("No data fetched from any source")
        return pd.DataFrame(columns=['doc_id', 'title', 'publish_time', 'source', 'url', 'lang', 'category', 'content'])

    # Merge all sources
    df = merge_sources(frames)
    logging.info(f"Total articles after merge: {len(df)}")

    # Select and reorder columns for cleaner output
    output_cols = ['title', 'publish_time', 'source', 'url', 'lang', 'category', 'doc_id', 'content']
    df = df[output_cols].copy()

    return df


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Fetch recent news to CSV")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours back to fetch (default: 24)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output CSV path (default: auto-generated with timestamp)",
    )
    parser.add_argument(
        "--no-gdelt",
        action="store_true",
        help="Disable GDELT source",
    )
    parser.add_argument(
        "--no-rss",
        action="store_true",
        help="Disable RSS source",
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # Generate output path if not provided
    if args.output is None:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        args.output = str(config.DATA_DIR / f"news_{timestamp}.csv")

    logging.info(f"Fetching news from last {args.hours} hours...")

    df = fetch_all_sources(
        hours=args.hours,
        use_gdelt=not args.no_gdelt,
        use_rss=not args.no_rss,
    )

    if df.empty:
        logging.error("No news fetched, exiting")
        return 1

    logging.info("\n" + "="*80)
    logging.info(f"Successfully fetched {len(df)} articles")
    logging.info("="*80)

    # Show summary by source
    source_counts = df['source'].value_counts()
    logging.info("\nArticles by source:")
    for src, cnt in source_counts.items():
        logging.info(f"  {src}: {cnt}")

    # Show sample
    logging.info("\nSample articles:")
    for i, row in df.head(5).iterrows():
        logging.info(f"  [{row['source']}] {row['title'][:60]}...")

    write_csv(df, args.output)
    logging.info(f"\nSaved to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
