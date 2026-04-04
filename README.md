# AI Toolkit

> AI 工具字典 — 管理 Claude Code Skills、MCP Servers 和 AI Agent 工具的综合目录

## 这是什么？

随着 AI 智能体工具层出不穷，管理起来越来越麻烦。这个项目是一个**工具字典/说明书**，帮助你：

1. **了解市面上最优秀的工具** — 按 GitHub Star 数和实用性排序
2. **快速查找工具信息** — 名称、功能、开源地址、使用方法
3. **新项目自动推荐** — 根据项目类型自动推荐适合的工具组合
4. **自动更新** — 通过 GitHub Actions 定时更新 Star 数等信息

## 快速开始

```bash
# 安装依赖
pip install -r scripts/requirements.txt

# 更新 GitHub Star 数据（需要 GITHUB_TOKEN）
export GITHUB_TOKEN=ghp_xxxx
python scripts/update_stars.py

# 生成分类文档
python scripts/generate_docs.py

# 根据项目类型获取工具推荐
python scripts/recommend.py --type fullstack
python scripts/recommend.py --type finance
python scripts/recommend.py --list-types
```

## 目录结构

```
ai-toolkit/
├── catalog/
│   ├── tools.json          # 核心数据库（唯一数据源）
│   ├── by-category/        # 按分类的 Markdown 文档（自动生成）
│   └── README.md           # 分类索引
├── scripts/
│   ├── update_stars.py     # GitHub Star 自动更新
│   ├── generate_docs.py    # 从 JSON 生成 Markdown 文档
│   ├── recommend.py        # 项目工具推荐引擎
│   └── requirements.txt
├── .github/workflows/
│   └── update-catalog.yml  # 每周自动更新
├── CLAUDE.md               # Claude Code 配置
└── README.md
```

## 工具总览

> 共 81 个工具，10 个分类 | 安全评级：🟢 trusted 🔵 verified 🟡 caution 🔴 danger ⚪ unreviewed

### MCP 服务器

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Firecrawl](https://github.com/mendableai/firecrawl) | 专为 LLM 设计的网页抓取和爬虫工具，可将网页转为干净的 Markdown | 101.6k | 🟡 | `scraping`, `crawler`, `llm` |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | 微软官方 Playwright MCP 服务器，为 LLM 提供浏览器自动化能力 | 30.0k | 🟡 | `browser`, `automation`, `testing` |
| [Composio](https://github.com/ComposioHQ/composio) | AI 智能体工具集成平台，提供 250+ 应用的工具接口 | 27.6k | 🟡 | `integration`, `tools`, `agent` |
| [Jina Reader](https://github.com/jina-ai/reader) | Jina AI 网页内容提取 API，将 URL 转为 LLM 友好的文本 | 10.4k | 🟡 | `web`, `reader`, `content` |
| [Firecrawl MCP Server](https://github.com/mendableai/firecrawl-mcp-server) | Firecrawl 官方 MCP 服务器，为 Claude Code 提供网页抓取能力 | 5.9k | 🟡 | `scraping`, `mcp`, `firecrawl` |
| [Tavily Web Search](https://github.com/tavily-ai/tavily-mcp) | AI 智能体专用搜索引擎，过滤广告和干扰信息 | 1.6k | 🟡 | `search`, `web`, `llm` |
| [Apify MCP Server](https://github.com/apify/apify-mcp-server) | Apify 平台 MCP 服务器，3000+ 网页抓取和自动化 Actor | 985 | 🔴 | `scraping`, `automation`, `actor` |
| [Lark OpenAPI MCP](https://github.com/larksuite/lark-openapi-mcp) | 飞书/Lark 官方 OpenAPI MCP 服务器 | 622 | 🟡 | `feishu`, `lark`, `mcp` |

### Claude Code Skills

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Superpowers](https://github.com/obra/superpowers) | 智能体技能框架和软件开发方法论，20+ 技能 | 126.8k | 🟡 | `enhancement`, `productivity`, `power-user` |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI/UX 设计智能体技能，支持布局、界面、设计系统 | 55.5k | 🟡 | `frontend`, `ui`, `design` |
| [Last 30 Days Skill](https://github.com/mvanhorn/last30days-skill) | AI 研究技能，跨 10+ 平台搜索近 30 天热点 | 16.6k | 🟡 | `research`, `social-media`, `trending` |
| [MiniMax Skills](https://github.com/MiniMax-AI/skills) | MiniMax 官方 AI 开发技能集，覆盖前端、全栈、移动端 | 8.2k | 🔴 | `skills`, `collection`, `enhancement` |
| [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | 48 个 AI 智能体 + 36 个工作流，模拟游戏工作室 | 7.6k | 🟡 | `game`, `development`, `creative` |
| [AutoResearch](https://github.com/uditgoenka/autoresearch) | 自主目标导向迭代研究技能 | 2.9k | 🟡 | `research`, `search`, `automation` |
| [Apify Agent Skills](https://github.com/apify/agent-skills) | Apify AI Agent 技能包，搜索、抓取等 | 1.8k | 🔵 | `agent`, `skills`, `scraping` |
| [Elite Long-term Memory](https://github.com/NextFrontierBuilds/elite-longterm-memory) | AI 记忆系统：WAL 协议 + 向量搜索 + 云备份 | 9 | 🟡 | `memory`, `persistence`, `context` |
| CapabilityEvolver | ⚠️ 已知风险：AI 自我进化引擎，曾被发现向飞书传输数据 | - | 🔴 | `self-improvement`, `evolution`, `learning` |
| Auto Updater | ⚠️ 已知风险：自动更新技能和工具 | - | 🔴 | `update`, `automation`, `maintenance` |

### AI 智能体/框架

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Agency Agents](https://github.com/msitarzewski/agency-agents) | 完整的 AI 代理公司，每个智能体有个性和交付物 | 66.9k | 🟡 | `agent`, `framework`, `multi-agent` |
| [DeerFlow](https://github.com/bytedance/deer-flow) | 字节跳动长程 SuperAgent 框架，支持沙箱、记忆、子智能体 | 54.7k | 🟡 | `research`, `workflow`, `search` |
| [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 一键生成短视频，自动提取素材、合成配音和字幕 | 54.3k | 🔴 | `video`, `content`, `automation` |
| [MiroFish](https://github.com/666ghj/MiroFish) | 群体智能预测引擎，模拟数千 AI 智能体预测事件走向 | 46.6k | 🔵 | `ai`, `assistant` |
| [MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2) | 自动化在线赚钱流程，支持短视频、社交媒体自动化 | 27.6k | 🔵 | `video`, `content`, `automation` |
| [Project Nomad](https://github.com/Crosstalk-Solutions/project-nomad) | 自包含离线生存计算机，集成工具、知识库和 AI | 20.4k | 🟡 | `project-management`, `agent`, `workflow` |

### 命令行工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 让所有软件变成 Agent 原生，通过 CLI 使应用可被 AI 控制 | 25.4k | 🔵 | `cli`, `integration`, `automation` |
| [Google Workspace CLI](https://github.com/googleworkspace/cli) | Google Workspace 全能 CLI，覆盖 Drive/Gmail/Calendar | 23.3k | 🟡 | `google`, `workspace`, `cli` |
| [RTK](https://github.com/rtk-ai/rtk) | CLI 代理，减少 LLM Token 消耗 60-90%，Rust 单二进制 | 15.9k | 🟡 | `token`, `optimization`, `cli` |
| [cmux](https://github.com/manaflow-ai/cmux) | 基于 Ghostty 的 macOS 终端，支持 AI 编程垂直标签 | 11.8k | 🟡 | `terminal`, `multiplexer`, `cli` |
| [ClawX](https://github.com/ValueCell-ai/ClawX) | OpenClaw 桌面版 GUI | 5.9k | 🔴 | `desktop`, `gui`, `enhancement` |
| [Lark CLI](https://github.com/larksuite/cli) | 飞书官方 CLI，200+ 命令覆盖消息、文档、表格 | 5.2k | 🟡 | `lark`, `feishu`, `office` |

### 浏览器/网页工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Carbonyl](https://github.com/fathyb/carbonyl) | 在终端中运行 Chromium 浏览器 | 17.5k | 🟡 | `browser`, `terminal`, `chromium` |
| [Web Access](https://github.com/eze-is/web-access) | Claude Code 完整联网技能：三层通道 + 浏览器 CDP | 3.0k | 🟡 | `browser`, `web`, `access` |

### 语音工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [VibeVoice](https://github.com/microsoft/VibeVoice) | 微软开源语音 AI，支持 TTS 和 ASR，50+ 种语言 | 31.9k | 🔵 | `voice`, `coding`, `accessibility` |
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | 阿里通义千问开源语音合成，支持流式生成和语音克隆 | 10.2k | 🔵 | `voice`, `qwen`, `chinese` |

### 金融投资工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | 多智能体 LLM 金融交易框架 | 44.8k | 🔵 | `trading`, `finance`, `multi-agent` |
| [Agents](https://github.com/wshobson/agents) | 智能自动化和多智能体编排框架 | 32.6k | 🔵 | `trading`, `finance`, `stock` |
| Alert System | 价格和事件告警系统 | - | 🔴 | `alert`, `notification`, `finance` |
| Backtest Engine | 策略回测引擎 | - | 🔴 | `backtest`, `trading`, `strategy` |
| China Stock Analysis | A 股分析工具 | - | 🔴 | `stock`, `china`, `a-share` |
| Crypto Analysis | 加密货币分析 | - | 🔴 | `crypto`, `blockchain`, `finance` |
| Data Analysis | 通用数据分析 | - | 🔴 | `data`, `analysis`, `statistics` |
| Data Visualization | 数据可视化，生成图表和仪表板 | - | 🔴 | `visualization`, `charts`, `dashboard` |
| Finnhub Pro | Finnhub 金融数据接口 | - | 🔴 | `finnhub`, `finance`, `data` |
| Tushare Finance | Tushare 中国金融数据，220+ 接口 | - | 🔴 | `tushare`, `finance`, `china` |
| US Stock Analysis | 美股分析工具 | - | 🔴 | `stock`, `us-market`, `finance` |
| US Value Investing Framework | 价值投资框架 | - | 🔴 | `value-investing`, `fundamental`, `finance` |
| Quant Factor Screener | 量化因子选股 | - | 🔴 | `quant`, `factor`, `screening` |
| Stock Portfolio Manager | 股票组合管理 | - | 🔴 | `portfolio`, `stock`, `management` |
| Trading Coach | AI 交易教练 | - | 🔴 | `trading`, `coaching`, `education` |
| News Aggregator | 多来源财经新闻聚合 | - | 🔴 | `news`, `aggregation`, `finance` |
| Risk Management | 投资风险评估 | - | 🔴 | `risk`, `management`, `finance` |

### 效率/生产力工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Humanizer](https://github.com/brandonwise/humanizer) | AI 文本人性化，检测并消除 AI 写作痕迹 | 33 | 🟡 | `chinese`, `writing`, `humanize` |
| [Token Optimizer](https://github.com/openclaw-token-optimizer/openclaw-token-optimizer) | Token 优化器，降低 API 成本 | 8 | 🟡 | `optimization`, `token`, `cost` |
| Free Ride | 管理 OpenRouter 免费 AI 模型 | - | 🔴 | `cost`, `optimization`, `free` |
| Feishu Doc | 飞书文档操作：Wiki/Docs/Sheets/Bitable | - | 🔴 | `feishu`, `document`, `office` |
| Feishu Drive | 飞书网盘文件操作 | - | 🔴 | `feishu`, `drive`, `storage` |
| Feishu Wiki | 飞书知识库操作 | - | 🔴 | `feishu`, `wiki`, `knowledge-base` |

### 开发辅助工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [OpenClaw](https://github.com/openclaw/openclaw) | 个人 AI 助手，任意 OS/平台，ClawHub 13000+ 技能 | 342.4k | 🟡 | `ecosystem`, `marketplace`, `skills` |
| [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) | Claude Code 性能优化系统 | 122.0k | 🔵 | `claude-code`, `awesome-list`, `reference` |
| [Get Shit Done](https://github.com/gsd-build/get-shit-done) | 轻量级元提示和规范驱动开发系统，让 Agent 长时间自主工作 | 45.6k | 🔵 | `git`, `workflow`, `productivity` |
| [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills) | OpenClaw 技能精选集，5400+ 技能筛选和分类 | 43.3k | 🟡 | `openclaw`, `skills`, `awesome-list` |
| [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code) | Claude Code 精选资源列表 | 34.7k | 🟡 | `awesome-list`, `reference`, `skills` |
| [QwenCode](https://github.com/QwenLM/qwen-code) | 阿里通义千问终端编程智能体 | 21.4k | 🟡 | `coding`, `qwen`, `assistant` |
| [Oh My Claude Code](https://github.com/Yeachan-Heo/oh-my-claudecode) | 团队优先的多智能体编排框架 | 17.9k | 🟡 | `config`, `enhancement`, `framework` |
| [ClawHub](https://github.com/openclaw/clawhub) | OpenClaw 官方技能市场，13000+ 社区技能 | 7.2k | 🔵 | `marketplace`, `skills`, `registry` |
| [Skill Security Auditor](https://github.com/openclaw/skills) | ClawHub 技能安全分析器，20+ 恶意指标匹配 | 3.6k | 🟢 | `security`, `audit`, `cli` |
| [Clawith](https://github.com/dataelement/Clawith) | OpenClaw 团队版，多智能体协作平台 | 2.6k | 🔴 | `team`, `collaboration`, `skills` |
| [Snyk Agent Scan](https://github.com/snyk/agent-scan) | AI Agent 和 MCP 安全扫描器 | 2.0k | 🟢 | `security`, `scanning`, `mcp` |
| [ClawSec](https://github.com/prompt-security/clawsec) | OpenClaw 完整安全套件 | 862 | 🟢 | `security`, `audit`, `openclaw` |
| [OpenClaw Security Monitor](https://github.com/adibirzu/openclaw-security-monitor) | 主动安全监控：41 点威胁扫描 + Web 仪表板 | 29 | 🟢 | `security`, `monitoring`, `runtime` |
| [ClawSecure](https://github.com/ClawSecure/clawsecure-openclaw-security) | 免费安全扫描器，2890+ 智能体已审计 | 20 | 🟢 | `security`, `audit`, `owasp` |
| Healthcheck | 安全审计和健康检查 | - | 🔴 | `security`, `audit`, `health` |
| Bitdefender AI Skills Checker | 免费 AI 技能安全检查器 | - | 🟢 | `security`, `audit`, `scanning` |

### OpenClaw Skills

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| Podcast Reader | 播客内容转结构化笔记 | - | 🔴 | `podcast`, `content`, `notes` |
| GitHub to Skills | 将 GitHub 项目转为 Skill | - | 🔴 | `github`, `skills`, `conversion` |
| Skill Manager | Skill 统一管理、安装、更新 | - | 🔴 | `skills`, `management`, `install` |
| Skill Evolution Manager | Skill 自动迭代优化 | - | 🔴 | `skills`, `evolution`, `optimization` |
| MCP Builder | MCP 服务器快速构建 | - | 🔴 | `mcp`, `builder`, `server` |
| PPTX Skill | PPT 文件处理与生成 | - | 🔴 | `pptx`, `presentation`, `office` |
| Video Transcribe | 视频/音频自动转文字 | - | 🔴 | `video`, `audio`, `transcription` |
| JSON Canvas | JSON Canvas 画布编辑 | - | 🔴 | `canvas`, `json`, `visual` |

## 添加新工具

编辑 `catalog/tools.json`，添加一条新记录：

```json
{
  "id": "tool-id",
  "name": "Tool Name",
  "description": "工具描述",
  "category": "skill",
  "github_url": "https://github.com/owner/repo",
  "stars": 0,
  "tags": ["tag1", "tag2"],
  "use_cases": ["用途1", "用途2"],
  "install_cmd": "安装命令",
  "usage": "使用方法",
  "priority": "normal"
}
```

然后运行 `python scripts/update_stars.py && python scripts/generate_docs.py` 更新数据。

## 自动更新

项目配置了 GitHub Actions，**每周一自动更新** Star 数据并重新生成文档。也可以手动触发：

1. 进入 GitHub 仓库的 Actions 页面
2. 选择「自动更新工具目录」工作流
3. 点击「Run workflow」

## License

MIT
