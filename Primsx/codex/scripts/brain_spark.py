"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: brain_spark.py                                                        ║
║  Generated: 2025-12-26T10:00:42.455094                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

#!/usr/bin/env python3
# ==============================================================================
# PRIMSX CODEX - BRAIN_SPARK.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import requests, datetime, feedparser

def fetch_latest_arxiv_ai():
    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=lastUpdatedDate&max_results=5"
    feed = feedparser.parse(url)
    return [(entry.title, entry.link) for entry in feed.entries]

def fetch_ai_tech_news():
    sources = [
        "https://ai.googleblog.com/atom.xml",
        "https://www.ubuntu.com/blog/feed",
        "https://news.ycombinator.com/rss"
    ]
    all_items = []
    for src in sources:
        feed = feedparser.parse(src)
        all_items += [(entry.title, entry.link) for entry in feed.entries[:5]]
    return all_items

if __name__ == "__main__":
    print("=== AI Math Tech News ===")
    for title, url in fetch_latest_arxiv_ai():
        print(f"[arxiv] {title}: {url}")
    for title, url in fetch_ai_tech_news():
        print(f"[news] {title}: {url}")
