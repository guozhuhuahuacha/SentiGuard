#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 FactAgent 的网络搜索功能
"""
import os
import sys
import json
from dotenv import load_dotenv

# 把项目根目录加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# 加载环境变量
load_dotenv()

print("=" * 60)
print("FactAgent Web Search Test")
print("=" * 60)

# 1. 检查 API Keys
print("\n[1] Checking API Keys...")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

status_serper = "OK - Set" if SERPER_API_KEY else "ERROR - Not Set"
status_google = "OK - Set" if GOOGLE_API_KEY else "ERROR - Not Set"
print(f"  SERPER_API_KEY: {status_serper}")
print(f"  GOOGLE_API_KEY: {status_google}")

if not SERPER_API_KEY or not GOOGLE_API_KEY:
    print("\nERROR: Missing required API Keys, please set in .env file")
    sys.exit(1)

print("\nOK: API Keys check passed")

# 2. 测试媒体偏见数据库
print("\n[2] Checking media bias database...")
try:
    from src.main.python.tools.retrieve import MEDIA_BIAS_DICT, MEDIA_DATA
    print(f"  OK: Media bias database loaded, total {len(MEDIA_DATA)} records")

    # 查看数据库中的一些样本
    print("\n  Sample entries from database:")
    for i, entry in enumerate(MEDIA_DATA[:5]):
        url = entry.get('url', 'N/A')
        bias = entry.get('bias', 'N/A')
        factual = entry.get('factual', 'N/A')
        print(f"    {i+1}. {url} - bias={bias}, factual={factual}")

except Exception as e:
    print(f"  ERROR: Media bias database check failed: {e}")
    import traceback
    traceback.print_exc()

# 3. 测试 URL 检查逻辑
print("\n[3] Testing URL validation logic...")
try:
    from src.main.python.tools.retrieve import SearchEngineRetriever

    # 创建检索器但不启动浏览器
    retriever = SearchEngineRetriever(dataset="feverous", headless=True)

    # 清理浏览器（我们不需要它）
    if hasattr(retriever, 'driver'):
        retriever.driver.quit()
        del retriever.driver

    # 测试一些 URL
    test_urls = [
        "https://www.bbc.com/news/world",
        "https://en.wikipedia.org/wiki/Science",
        "https://www.nih.gov/health",
        "https://www.nature.com/articles",
    ]

    print("\n  Testing URL validity:")
    for url in test_urls:
        is_valid = retriever._check_valid_url(url)
        status = "OK - Valid" if is_valid else "SKIP - Not valid"

        import urllib.parse
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]

        print(f"    {domain}: {status}")

except Exception as e:
    print(f"  ERROR: URL validation test failed: {e}")
    import traceback
    traceback.print_exc()

# 4. 展示搜索流程图
print("\n" + "=" * 60)
print("How FactAgent Search Works")
print("=" * 60)
print("""
1. Serper API Search
   - Calls https://google.serper.dev/search
   - Returns 10 search results per query
   - Applies dataset-specific date limits

2. URL Legitimacy Check
   - Checks media bias database (5714 sources)
   - Checks domain suffix (.edu, .gov, .org)
   - Checks domain age (WHOIS lookup >5 years)
   - Checks scientific domains

3. Selenium Content Crawling
   - Launches Chrome browser (headless by default)
   - Visits valid URLs
   - Extracts all <p> paragraph content
   - Detects bot detection pages

4. Gemini Content Extraction
   - Uses Gemini 1.5 Flash model
   - Extracts only query-relevant sentences
   - Filters out irrelevant information
""")

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)

print("\nSummary:")
print("- Media Bias DB: OK - Loaded", len(MEDIA_DATA), "records")
print("- Serper API:", "OK - Set" if SERPER_API_KEY else "ERROR - Not Set")
print("- Gemini API:", "OK - Set" if GOOGLE_API_KEY else "ERROR - Not Set")
print("\nNote: Full search test requires internet connection and proper API keys")
print("      You can run 'python -m pytest src/test/python/test_factagent.py' for end-to-end testing")
