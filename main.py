import logging
import os
import sys
from src.collector import NewsCollector
from src.llm import NewsAnalyst
from src.mailer import DailyDigestMailer
from dotenv import load_dotenv

# 加载 .env 变量 (本地测试用)
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

def main():
    try:
        # 1. 初始化收集器并抓取新闻
        logger.info("启动新闻采集...")
        collector = NewsCollector()
        raw_news = collector.fetch_feeds(hours_back=24)
        
        if not raw_news:
            logger.info("今日无符合条件的新闻，结束运行。")
            return

        # 2. 初始化AI分析师并处理数据
        logger.info(f"开始AI分析 {len(raw_news)} 条新闻...")
        analyst = NewsAnalyst()
        analyzed_data = analyst.analyze_news_batch(raw_news)
        
        if not analyzed_data:
            logger.warning("AI分析未能生成有效结果")
            return

        # 3. 生成并发送邮件
        logger.info("生成邮件内容...")
        mailer = DailyDigestMailer()
        html_content = mailer.render_email(analyzed_data)
        
        subject_suffix = ""
        # 动态标题后缀 (例如: "包含重大技术突破!")
        if analyzed_data.get('tech'):
            subject_suffix += "🔥技术突破 "
        if analyzed_data.get('market'):
            subject_suffix += "💰大额融资 "
            
        logger.info("发送邮件...")
        mailer.send_email(html_content, subject_suffix)
        logger.info("全流程执行完毕！")

    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
