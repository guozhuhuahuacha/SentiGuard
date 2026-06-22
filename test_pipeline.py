"""临时测试脚本：测试热点采集管道"""
import sys
sys.path.insert(0, '.')

from src.main.python.services.pipeline import HotspotPipeline

pipeline = HotspotPipeline()
result = pipeline.run(source='BAIDU')

print('=== RESULT ===')
print(f"Task ID: {result['task_id']}")
print(f"News collected: {result['news_collected']}")
print(f"News saved: {result['news_saved']}")
print(f"News skipped (dup): {result['news_skipped']}")
print(f"Hot events: {result['hot_events']}")
print()

for h in result['hotspots']:
    print(f"  #{h['rank']} {h['name'][:50]} | heat:{h['heat']} | sentiment:{h['sentiment']['label']} | news:{h['news_count']}")
    print(f"    keywords: {', '.join(k['word'] for k in h['keywords'])}")
