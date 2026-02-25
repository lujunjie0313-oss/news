import yaml
import json
import logging
import os
from openai import OpenAI
from typing import List, Dict

logger = logging.getLogger(__name__)

class NewsAnalyst:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/") # 默认 Gemini OpenAI 兼容地址
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = self.config['ai']['model']

    def analyze_news_batch(self, news_items: List[Dict]) -> Dict:
        """
        批量分析新闻列表，并按类别整理
        """
        if not news_items:
            return {}
            
        # 1. 准备输入给AI的文本块
        prompt_input = ""
        for idx, item in enumerate(news_items):
            prompt_input += f"""
            新闻ID: {idx}
            标题: {item['title']}
            来源: {item['source']}
            摘要: {item['summary'][:300]} 
            链接: {item['link']}
            -------------------
            """
            
        # 2. 构建 Prompt
        system_prompt = """
        你是激光雷达和商业航天领域的资深分析师。你的任务是从一系列新闻摘要中提取关键信息。
        
        请仔细分析每条新闻，并按以下三个类别进行分类整理：
        
        1. 【技术突破】(Technology Breakthroughs): 涉及具体技术参数提升(如探测距离、分辨率)、新产品发布、技术方案创新(如FMCW、固态)。
           -必须提取具体数字/参数。
        2. 【市场与融资】(Market & Funding): 涉及融资金额(Series A/B/C)、IPO、大额订单、定点合作、市场规模预测(CAGR)、收购。
           -必须提取金额、公司名、具体数字。
        3. 【行业动态】(Industry News): 其他重要的人事变动、政策发布、一般性新闻。

        请输出严格的 JSON 格式，不要包含Markdown代码块标记。
        格式如下：
        {
          "tech": [
             {"title": "新闻标题", "summary": "一句话总结(包含关键参数)", "source": "来源", "link": "原始链接", "metrics": "提取的关键数据(如: 500m探测距离)"}
          ],
          "market": [
             {"title": "新闻标题", "summary": "一句话总结(包含金额/规模)", "source": "来源", "link": "原始链接", "amount": "提取的金额/规模(如: $100M融资)"}
          ],
          "general": [
             {"title": "新闻标题", "summary": "一句话总结", "source": "来源", "link": "原始链接"}
          ]
        }
        
        如果某条新闻完全无关或广告，请忽略。
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请分析以下新闻列表:\n{prompt_input}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            logger.info("AI分析完成")
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return {}
