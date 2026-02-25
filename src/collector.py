import feedparser
import yaml
import re
from datetime import datetime, timedelta
import logging
from typing import List, Dict
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.seen_hashes = set()  # 简单去重

    def _load_config(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _hash_content(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _is_relevant(self, title, summary):
        """
        根据关键词判断是否保留
        """
        text = (title + " " + summary).lower()
        
        # 排除关键词
        for exclude_kw in self.config.get('keywords', {}).get('exclude', []):
            if exclude_kw.lower() in text:
                return False
                
        # 包含关键词
        for include_kw in self.config.get('keywords', {}).get('include', []):
            if include_kw.lower() in text:
                return True
                
        return False

    def fetch_feeds(self, hours_back=24) -> List[Dict]:
        """
        抓取所有源的新闻，并根据时间过滤
        """
        all_news = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # 遍历所有分类
        for category, feeds in self.config.get('feeds', {}).items():
            for feed in feeds:
                try:
                    logger.info(f"正在抓取: {feed['name']} ({feed['url']})")
                    parsed = feedparser.parse(feed['url'])
                    
                    if parsed.bozo:
                        logger.warning(f"解析RSS源出错: {feed['name']} - {parsed.bozo_exception}")
                        continue

                    for entry in parsed.entries:
                        # 获取发布时间 (尝试多种格式)
                        published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                        if not published_parsed:
                            continue
                            
                        pub_date = datetime(*published_parsed[:6])
                        
                        # 仅保留过去24小时的新闻
                        if pub_date < cutoff_time:
                            continue

                        title = entry.get('title', '')
                        link = entry.get('link', '')
                        summary = entry.get('summary', '') or entry.get('description', '')

                        # 去重检查
                        content_hash = self._hash_content(title)
                        if content_hash in self.seen_hashes:
                            continue
                            
                        # 关键词过滤
                        if not self._is_relevant(title, summary):
                            continue

                        self.seen_hashes.add(content_hash)
                        
                        all_news.append({
                            'title': title,
                            'link': link,
                            'summary': summary, # 原始摘要，稍后交给AI处理
                            'source': feed['name'],
                            'category': category,
                            'pub_date': pub_date.strftime('%Y-%m-%d %H:%M')
                        })
                        
                except Exception as e:
                    logger.error(f"抓取失败 {feed['name']}: {str(e)}")
                    
        logger.info(f"共收集到 {len(all_news)} 条相关新闻")
        return all_news

if __name__ == "__main__":
    collector = NewsCollector()
    news = collector.fetch_feeds()
    for item in news:
        print(f"[{item['category']}] {item['title']} - {item['source']}")
