import smtplib
import yaml
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DailyDigestMailer:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        self.sender = os.getenv("EMAIL_SENDER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.recipient = os.getenv("EMAIL_RECIPIENT")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.qq.com") # 默认 QQ 邮箱
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))

    def render_email(self, analysis_result: dict) -> str:
        """
        使用 Jinja2 渲染 HTML 邮件
        """
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 30px; }
                .item { margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }
                .title { font-weight: bold; font-size: 16px; color: #0366d6; text-decoration: none; }
                .meta { font-size: 12px; color: #666; margin-top: 5px; }
                .metric { color: #d73a49; font-weight: bold; background: #ffeef0; padding: 2px 5px; border-radius: 3px; font-size: 12px; }
                .tag { display: inline-block; padding: 2px 6px; font-size: 11px; font-weight: 600; line-height: 1; color: #fff; text-align: center; white-space: nowrap; vertical-align: baseline; border-radius: 0.25em; }
                .bg-tech { background-color: #28a745; }
                .bg-market { background-color: #ffc107; color: #333; }
                .bg-info { background-color: #17a2b8; }
                .footer { margin-top: 40px; font-size: 12px; color: #999; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 每日行业情报简报 ({{ date }})</h1>
                
                {% if data.tech %}
                <h2>🔥 技术突破 ({{ data.tech|length }})</h2>
                {% for item in data.tech %}
                <div class="item">
                    <span class="tag bg-tech">技术</span>
                    <a href="{{ item.link }}" class="title">{{ item.title }}</a>
                    <div style="margin-top: 5px;">{{ item.summary }}</div>
                    {% if item.metrics %}
                    <div class="meta">关键参数: <span class="metric">{{ item.metrics }}</span> | 来源: {{ item.source }}</div>
                    {% else %}
                    <div class="meta">来源: {{ item.source }}</div>
                    {% endif %}
                </div>
                {% endfor %}
                {% endif %}

                {% if data.market %}
                <h2>💰 市场与融资 ({{ data.market|length }})</h2>
                {% for item in data.market %}
                <div class="item">
                    <span class="tag bg-market">市场</span>
                    <a href="{{ item.link }}" class="title">{{ item.title }}</a>
                    <div style="margin-top: 5px;">{{ item.summary }}</div>
                    {% if item.amount %}
                    <div class="meta">涉及金额: <span class="metric">{{ item.amount }}</span> | 来源: {{ item.source }}</div>
                    {% else %}
                    <div class="meta">来源: {{ item.source }}</div>
                    {% endif %}
                </div>
                {% endfor %}
                {% endif %}
                
                {% if data.general %}
                <h2>📰 行业动态 ({{ data.general|length }})</h2>
                {% for item in data.general %}
                <div class="item">
                    <span class="tag bg-info">动态</span>
                    <a href="{{ item.link }}" class="title">{{ item.title }}</a>
                    <div style="margin-top: 5px;">{{ item.summary }}</div>
                    <div class="meta">来源: {{ item.source }}</div>
                </div>
                {% endfor %}
                {% endif %}
                
                <div class="footer">
                    生成时间: {{ timestamp }} <br>
                    Powered by AI Industry Analyst
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        return template.render(
            data=analysis_result,
            date=datetime.now().strftime('%Y-%m-%d'),
            timestamp=datetime.now().strftime('%H:%M:%S')
        )

    def send_email(self, html_content: str, subject_suffix=""):
        """
        发送 HTML 邮件
        """
        if not self.sender or not self.password:
            logger.error("未配置发件人邮箱或密码")
            return

        msg = MIMEMultipart()
        msg['From'] = f"{self.config['email']['sender_name']} <{self.sender}>"
        msg['To'] = self.recipient
        msg['Subject'] = f"{self.config['email']['subject_prefix']} {datetime.now().strftime('%Y-%m-%d')} {subject_suffix}"
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            logger.info(f"邮件已发送至 {self.recipient}")
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
