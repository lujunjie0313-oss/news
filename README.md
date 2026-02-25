# 🚀 每日行业情报简报 (Industry Digest Bot)

这是一个自动化的 GitHub Actions 机器人，专为**激光雷达 (LiDAR)** 和 **商业航天 (Commercial Aerospace)** 行业从业者设计。

它每天早上 **8:00 (北京时间)** 自动运行：
1.  **全网抓取**：从权威媒体（雷峰网、36氪、SpaceNews、Yole Group 等）采集最新资讯。
2.  **智能筛选**：通过关键词过滤掉广告和无关信息。
3.  **AI 深度分析**：调用大模型 (DeepSeek/OpenAI) 提取**核心技术参数**、**融资金额**、**市场增长率 (CAGR)**。
4.  **邮件推送**：生成一份结构化、数据驱动的 HTML 日报发送到你的邮箱。

---

## 🛠️ 快速开始

### 1. Fork 或 Clone 本仓库
推荐使用 **Private** 私有仓库，保护你的 API Key 和配置信息。

### 2. 配置 GitHub Secrets
在仓库页面点击 `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`，添加以下变量：

| Secret Name | 描述 | 示例 |
| :--- | :--- | :--- |
| `LLM_API_KEY` | DeepSeek 或 OpenAI 的 API Key | `sk-xxxxxxxx` |
| `LLM_BASE_URL` | (可选) API 地址，默认 DeepSeek | `https://api.deepseek.com/v1` |
| `EMAIL_SENDER` | 发件邮箱地址 (推荐 QQ/Gmail) | `your_email@qq.com` |
| `EMAIL_PASSWORD` | 邮箱授权码 (⚠️不是登录密码) | `abcdefghijklmn` (QQ邮箱在设置->账户开启SMTP获取) |
| `EMAIL_RECIPIENT` | 接收简报的邮箱 | `boss@company.com` |

### 3. 自定义配置 (`config.yaml`)
你可以修改 `config.yaml` 来调整关注点：

```yaml
feeds:
  lidar:
    - url: "https://www.leiphone.com/feed/category/lidar" # 添加新的 RSS
keywords:
  include: ["固态", "FMCW", "融资", "IPO"] # 增加关键词
```

### 4. 手动运行测试
1.  进入 GitHub 仓库的 `Actions` 标签页。
2.  点击左侧 workflows 中的 `Daily Industry Digest`。
3.  点击右侧 `Run workflow` 按钮。
4.  等待约 1-2 分钟，检查你的邮箱收件箱（包括垃圾邮件文件夹）。

---

## 🧩 项目结构

*   `src/collector.py`: **数据采集器** - 负责抓取 RSS，去重，关键词过滤。
*   `src/llm.py`: **AI 分析师** - 调用 LLM 提取技术参数和市场数据。
*   `src/mailer.py`: **邮件发送器** - 渲染 HTML 模板并发送。
*   `.github/workflows/daily_digest.yml`: **定时任务配置**。

## 🔧 常见问题

**Q: 收不到邮件怎么办？**
A: 
1. 检查 GitHub Actions 日志，看是否有报错。
2. 检查 `EMAIL_PASSWORD` 是否正确（QQ 邮箱需使用授权码）。
3. 检查垃圾邮件箱。

**Q: 只有标题没有内容？**
A: 这是因为部分 RSS 源只提供摘要。目前的版本设计为基于摘要进行分析。如果需要全文分析，需在 `collector.py` 中接入爬虫（但这会增加运行时间和封禁风险）。

**Q: 如何修改运行时间？**
A: 修改 `.github/workflows/daily_digest.yml` 中的 `cron` 表达式。
   - `0 0 * * *` = UTC 0点 (北京时间 8:00)
   - `0 1 * * *` = UTC 1点 (北京时间 9:00)

---
**Powered by AI Industry Analyst**
