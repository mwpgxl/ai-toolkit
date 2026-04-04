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

> 共 106 个工具，10 个分类 | 安全评级：🟢 trusted 🔵 verified 🟡 caution 🔴 danger ⚪ unreviewed

### MCP 服务器

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Firecrawl](https://github.com/mendableai/firecrawl) | 专为 LLM 设计的网页抓取和爬虫工具，可将网页转为干净的 Markdown | 101.6k | 🟡 | `scraping`, `crawler`, `llm` |
| [MCP Reference Servers](https://github.com/modelcontextprotocol/servers) | Anthropic 官方 MCP 参考实现，含 filesystem、memory、fetch、… | 82.9k | 🟢 | `official`, `reference`, `anthropic` |
| [Context7](https://github.com/upstash/context7) | 为 LLM 提供最新版本文档和代码示例的 MCP 服务器 | 51.6k | 🔵 | `documentation`, `context`, `code-examples` |
| [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Google 官方 Chrome DevTools MCP 服务器，AI 编码智能体的浏览器调试工具 | 33.1k | 🟢 | `chrome`, `devtools`, `browser` |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | 微软官方 Playwright MCP 服务器，为 LLM 提供浏览器自动化能力 | 30.0k | 🟡 | `browser`, `automation`, `testing` |
| [GitHub MCP Server](https://github.com/github/github-mcp-server) | GitHub 官方 MCP 服务器，操作仓库、Issue、PR、代码搜索 | 28.5k | 🟢 | `github`, `official`, `git` |
| [Composio](https://github.com/ComposioHQ/composio) | AI 智能体工具集成平台，提供 250+ 应用的工具接口 | 27.6k | 🟡 | `integration`, `tools`, `agent` |
| [Claude Task Master](https://github.com/eyaltoledano/claude-task-master) | AI 驱动的任务管理 MCP，支持 Cursor、Windsurf 等多个 AI IDE | 26.4k | ⚪ | `task-management`, `project`, `workflow` |
| [Graphiti](https://github.com/getzep/graphiti) | 实时知识图谱框架 + MCP 服务器，为 AI Agent 构建记忆 | 24.5k | 🔵 | `knowledge-graph`, `memory`, `neo4j` |
| [FastMCP](https://github.com/PrefectHQ/fastmcp) | 快速构建 MCP 服务器和客户端的 Python 框架 | 24.3k | 🔵 | `framework`, `python`, `builder` |
| [Blender MCP](https://github.com/ahujasid/blender-mcp) | 连接 Blender 到 AI 编码智能体，支持 prompt 辅助 3D 建模 | 18.4k | ⚪ | `blender`, `3d`, `modeling` |
| [Cognee](https://github.com/topoteretes/cognee) | AI Agent 记忆知识引擎，6 行代码接入知识图谱 | 14.9k | ⚪ | `knowledge-engine`, `memory`, `agent` |
| [Figma Context MCP](https://github.com/GLips/Figma-Context-MCP) | 将 Figma 设计稿布局信息提供给 AI 编码智能体 | 14.1k | ⚪ | `figma`, `design`, `ui` |
| [Jina Reader](https://github.com/jina-ai/reader) | Jina AI 网页内容提取 API，将 URL 转为 LLM 友好的文本 | 10.4k | 🟡 | `web`, `reader`, `content` |
| [Firecrawl MCP Server](https://github.com/mendableai/firecrawl-mcp-server) | Firecrawl 官方 MCP 服务器，为 Claude Code 提供网页抓取能力 | 5.9k | 🟡 | `scraping`, `mcp`, `firecrawl` |
| [Tavily Web Search](https://github.com/tavily-ai/tavily-mcp) | AI 智能体专用搜索引擎，专门为 LLM 设计，过滤广告和干扰信息 | 1.6k | 🟡 | `search`, `web`, `llm` |
| [Apify MCP Server](https://github.com/apify/apify-mcp-server) | Apify 平台的 MCP 服务器，提供 3000+ 现成的网页抓取和自动化 Actor | 985 | 🔴 | `scraping`, `automation`, `actor` |
| [Lark OpenAPI MCP](https://github.com/larksuite/lark-openapi-mcp) | 飞书/Lark 官方 OpenAPI MCP 服务器 | 622 | 🟡 | `feishu`, `lark`, `mcp` |

### Claude Code Skills

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Superpowers](https://github.com/obra/superpowers) | 智能体技能框架和软件开发方法论，包含 TDD、调试、协作等 20+ 技能 | 126.8k | 🟡 | `enhancement`, `productivity`, `power-user` |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI/UX 设计智能体技能，支持生成布局、改进界面、设计系统 Token、组件规范 | 55.5k | 🟡 | `frontend`, `ui`, `design` |
| [claude-mem](https://github.com/thedotmack/claude-mem) | Claude Code 自动记忆插件，AI 压缩会话历史并注入未来上下文 | 45.0k | ⚪ | `memory`, `persistence`, `context` |
| [Antigravity Awesome Skills](https://github.com/sickn33/antigravity-awesome-skills) | 1,340+ 可安装 Agent Skills 库，含 CLI 安装器和 bundles | 30.4k | ⚪ | `skills`, `collection`, `installer` |
| [SuperClaude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) | Claude Code 增强框架：专用命令、认知 persona、开发方法论 | 22.1k | ⚪ | `framework`, `enhancement`, `methodology` |
| [Planning with Files](https://github.com/OthmanAdi/planning-with-files) | Manus 风格持久化 Markdown 规划 Skill | 18.0k | ⚪ | `planning`, `workflow`, `markdown` |
| [claude-hud](https://github.com/jarrodwatts/claude-hud) | Claude Code 实时 HUD：上下文用量、工具状态、Agent 进度、TODO 追踪 | 16.7k | ⚪ | `monitoring`, `dashboard`, `context` |
| [Last 30 Days Skill](https://github.com/mvanhorn/last30days-skill) | AI 研究技能，跨 Reddit/X/YouTube/HN/Polymarket 等 10+ 平… | 16.6k | 🟡 | `research`, `social-media`, `trending` |
| [Awesome Claude Code Subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | 100+ 专业 Claude Code 子 Agent 合集 | 16.2k | ⚪ | `subagent`, `collection`, `awesome-list` |
| [Claude Plugins Official](https://github.com/anthropics/claude-plugins-official) | Anthropic 官方管理的高质量 Claude Code 插件目录 | 15.9k | 🟢 | `official`, `plugins`, `directory` |
| [Context Engineering Intro](https://github.com/coleam00/context-engineering-intro) | 上下文工程实战指南，以 Claude Code 为中心 | 13.1k | ⚪ | `context-engineering`, `guide`, `best-practices` |
| [Humanizer (blader)](https://github.com/blader/humanizer) | 消除 AI 写作痕迹的 Skill，社区最高星版本 | 12.3k | ⚪ | `writing`, `humanize`, `content` |
| [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills) | 精选 Claude Skills 和工具列表 | 10.5k | ⚪ | `awesome-list`, `skills`, `reference` |
| [MiniMax Skills](https://github.com/MiniMax-AI/skills) | MiniMax 官方 AI 开发技能集，覆盖前端、全栈、移动端、Shader 及文档生成 | 8.2k | 🔴 | `skills`, `collection`, `enhancement` |
| [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | 48 个 AI 智能体 + 36 个工作流技能，模拟真实游戏工作室层级 | 7.6k | 🟡 | `game`, `development`, `creative` |
| [Refly](https://github.com/refly-ai/refly) | 开源 Agent Skills Builder，定义工作流并在多平台运行 | 7.2k | ⚪ | `builder`, `workflow`, `cross-platform` |
| [Slavingia Skills](https://github.com/slavingia/skills) | Gumroad 创始人 Sahil Lavingia 的创业方法论 Skills | 6.4k | ⚪ | `entrepreneur`, `business`, `methodology` |
| [Trail of Bits Skills](https://github.com/trailofbits/skills) | 安全行业顶级团队 Trail of Bits 出品的安全审计 Skills | 4.3k | 🟢 | `security`, `audit`, `vulnerability` |
| [Claude SEO](https://github.com/AgriciDaniel/claude-seo) | 通用 SEO Skill：19 子技能 + 12 子 Agent + 3 扩展，覆盖技术 SEO… | 3.9k | ⚪ | `seo`, `marketing`, `content` |
| [AutoResearch](https://github.com/uditgoenka/autoresearch) | 自主目标导向迭代技能，灵感来自 Karpathy 的 autoresearch | 2.9k | 🟡 | `research`, `search`, `automation` |
| [Apify Agent Skills](https://github.com/apify/agent-skills) | Apify 为 AI Agent 提供的技能包，包含搜索、抓取等能力 | 1.8k | 🔵 | `agent`, `skills`, `scraping` |
| [Elite Long-term Memory](https://github.com/NextFrontierBuilds/elite-longterm-memory) | 终极 AI 记忆系统：WAL 协议 + 向量搜索 + git-notes + 云备份 | 9 | 🟡 | `memory`, `persistence`, `context` |
| CapabilityEvolver | AI 自我进化引擎，分析运行历史自动改进，ClawHub 下载量最高的技能。⚠️ 曾被发现向飞书… | - | 🔴 | `self-improvement`, `evolution`, `learning` |
| Auto Updater | 自动更新技能和工具到最新版本 | - | 🔴 | `update`, `automation`, `maintenance` |

### AI 智能体/框架

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Agency Agents](https://github.com/msitarzewski/agency-agents) | 完整的 AI 代理公司，每个智能体都有个性、流程和交付物 | 66.9k | 🟡 | `agent`, `framework`, `multi-agent` |
| [DeerFlow](https://github.com/bytedance/deer-flow) | 字节跳动开源的长程 SuperAgent 框架，支持沙箱、记忆、工具、技能和子智能体，处理分钟到… | 54.7k | 🟡 | `research`, `workflow`, `search` |
| [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 一键生成短视频，自动提取素材、合成配音和字幕 | 54.3k | 🔴 | `video`, `content`, `automation` |
| [MiroFish](https://github.com/666ghj/MiroFish) | 群体智能预测引擎，模拟数千 AI 智能体预测事件走向 | 46.6k | 🔵 | `ai`, `assistant` |
| [MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2) | 自动化在线赚钱流程，支持短视频、社交媒体自动化等 | 27.6k | 🔵 | `video`, `content`, `automation` |
| [Project Nomad](https://github.com/Crosstalk-Solutions/project-nomad) | 自包含离线生存计算机，集成关键工具、知识库和 AI，随时随地可用 | 20.4k | 🟡 | `project-management`, `agent`, `workflow` |

### 命令行工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 让所有软件变成 Agent 原生，通过 CLI 使任何应用可被 AI 控制 | 25.4k | 🔵 | `cli`, `integration`, `automation` |
| [Google Workspace CLI (gws)](https://github.com/googleworkspace/cli) | Google Workspace 全能 CLI，覆盖 Drive/Gmail/Calendar … | 23.3k | 🟡 | `google`, `workspace`, `cli` |
| [RTK](https://github.com/rtk-ai/rtk) | CLI 代理，减少 LLM Token 消耗 60-90%，Rust 单二进制零依赖 | 15.9k | 🟡 | `token`, `optimization`, `cli` |
| [ccusage](https://github.com/ryoppippi/ccusage) | Claude Code / Codex CLI 本地用量分析工具 | 12.4k | ⚪ | `usage`, `analytics`, `cost` |
| [cmux](https://github.com/manaflow-ai/cmux) | 基于 Ghostty 的 macOS 终端，支持 AI 编程智能体的垂直标签和通知 | 11.8k | 🟡 | `terminal`, `multiplexer`, `cli` |
| [ClawX (DeskClaw)](https://github.com/ValueCell-ai/ClawX) | OpenClaw 桌面版 GUI，将 CLI 智能体编排转为桌面体验 | 5.9k | 🔴 | `desktop`, `gui`, `enhancement` |
| [Lark CLI](https://github.com/larksuite/cli) | 飞书官方 CLI 工具，200+ 命令覆盖消息、文档、表格等核心业务 | 5.2k | 🟡 | `lark`, `feishu`, `office` |

### 浏览器/网页工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Carbonyl](https://github.com/fathyb/carbonyl) | 在终端中运行 Chromium 浏览器，支持 CSS、图片、视频等 | 17.5k | 🟡 | `browser`, `terminal`, `chromium` |
| [Web Access](https://github.com/eze-is/web-access) | Claude Code 完整联网技能：三层通道调度 + 浏览器 CDP + 并行分治 | 3.0k | 🟡 | `browser`, `web`, `access` |

### 语音工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [VibeVoice](https://github.com/microsoft/VibeVoice) | 微软开源的前沿语音 AI，支持 TTS 和 ASR，50+ 种语言 | 31.9k | 🔵 | `voice`, `coding`, `accessibility` |
| [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | 阿里通义千问开源语音合成模型，支持稳定表达、流式生成、语音克隆和自由设计 | 10.2k | 🔵 | `voice`, `qwen`, `chinese` |

### 金融投资工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [TradingAgents (TauricResearch)](https://github.com/TauricResearch/TradingAgents) | 多智能体 LLM 金融交易框架，模拟真实交易公司动态 | 44.8k | 🔵 | `trading`, `finance`, `multi-agent` |
| [Agents](https://github.com/wshobson/agents) | 智能自动化和多智能体编排框架，为 Claude Code 提供交易分析能力 | 32.6k | 🔵 | `trading`, `finance`, `stock` |
| Alert System | 智能提醒系统，金融投资场景的价格和事件告警 | - | 🔴 | `alert`, `notification`, `finance` |
| Backtest Engine | 策略回测引擎，测试交易策略的历史表现 | - | 🔴 | `backtest`, `trading`, `strategy` |
| China Stock Analysis | A 股分析工具，支持中国特色的股票分析指标 | - | 🔴 | `stock`, `china`, `a-share` |
| Crypto Analysis | 加密货币分析工具 | - | 🔴 | `crypto`, `blockchain`, `finance` |
| Data Analysis | 通用数据分析技能 | - | 🔴 | `data`, `analysis`, `statistics` |
| Data Visualization | 数据可视化技能，生成图表和仪表板 | - | 🔴 | `visualization`, `charts`, `dashboard` |
| Finnhub Pro | Finnhub 金融数据接口 | - | 🔴 | `finnhub`, `finance`, `data` |
| Tushare Finance | Tushare 中国金融数据接口，支持 220+ 接口覆盖 A 股/港股/美股/基金/期货 | - | 🔴 | `tushare`, `finance`, `china` |
| US Stock Analysis | 美股分析工具 | - | 🔴 | `stock`, `us-market`, `finance` |
| US Value Investing Framework | 价值投资框架，基于基本面分析的投资决策工具 | - | 🔴 | `value-investing`, `fundamental`, `finance` |
| Quant Factor Screener | 量化因子选股工具 | - | 🔴 | `quant`, `factor`, `screening` |
| Stock Portfolio Manager | 股票组合管理工具 | - | 🔴 | `portfolio`, `stock`, `management` |
| Trading Coach | AI 交易教练，提供交易指导和复盘 | - | 🔴 | `trading`, `coaching`, `education` |
| News Aggregator | 新闻聚合工具，收集多来源财经新闻 | - | 🔴 | `news`, `aggregation`, `finance` |
| Risk Management | 风险管理工具，评估投资风险 | - | 🔴 | `risk`, `management`, `finance` |

### 效率/生产力工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [Humanizer](https://github.com/brandonwise/humanizer) | AI 文本人性化工具，检测并消除 AI 写作痕迹，基于维基百科 AI 写作特征清单 | 33 | 🟡 | `chinese`, `writing`, `humanize` |
| [Token Optimizer](https://github.com/openclaw-token-optimizer/openclaw-token-optimizer) | OpenClaw Token 优化器，支持 Prompt 缓存和动态工具加载，降低 API 成本… | 8 | 🟡 | `optimization`, `token`, `cost` |
| Free Ride | 管理 OpenRouter 免费 AI 模型，自动按质量排名，配置限流回退 | - | 🔴 | `cost`, `optimization`, `free` |
| Feishu Doc | 飞书文档操作技能，支持读取、写入、更新 Wiki/Docs/Sheets/Bitable | - | 🔴 | `feishu`, `document`, `office` |
| Feishu Drive | 飞书网盘文件操作 | - | 🔴 | `feishu`, `drive`, `storage` |
| Feishu Wiki | 飞书知识库操作，导航和管理 Wiki 页面、空间、节点 | - | 🔴 | `feishu`, `wiki`, `knowledge-base` |

### 开发辅助工具

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| [OpenClaw](https://github.com/openclaw/openclaw) | 个人 AI 助手，支持任意操作系统和平台，ClawHub 技能市场 13000+ 技能 | 342.4k | 🟡 | `ecosystem`, `marketplace`, `skills` |
| [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) | Claude Code 性能优化系统，涵盖技能、本能、记忆、安全等 | 122.0k | 🔵 | `claude-code`, `awesome-list`, `reference` |
| [Get Shit Done](https://github.com/gsd-build/get-shit-done) | 轻量级元提示和规范驱动开发系统，让 Agent 长时间自主工作 | 45.6k | 🔵 | `git`, `workflow`, `productivity` |
| [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills) | OpenClaw 技能精选集，5400+ 技能筛选和分类 | 43.3k | 🟡 | `openclaw`, `skills`, `awesome-list` |
| [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code) | Claude Code 精选资源列表，收集技能、钩子、命令、插件等 | 34.7k | 🟡 | `awesome-list`, `reference`, `skills` |
| [QwenCode](https://github.com/QwenLM/qwen-code) | 阿里通义千问终端编程智能体，类似 Claude Code | 21.4k | 🟡 | `coding`, `qwen`, `assistant` |
| [Oh My Claude Code](https://github.com/Yeachan-Heo/oh-my-claudecode) | 团队优先的多智能体编排框架，零学习成本 | 17.9k | 🟡 | `config`, `enhancement`, `framework` |
| [ClawHub](https://github.com/openclaw/clawhub) | OpenClaw 官方技能市场，13000+ 社区技能，向量搜索，版本管理，VirusTotal… | 7.2k | 🔵 | `marketplace`, `skills`, `registry` |
| [Skill Security Auditor](https://github.com/openclaw/skills) | ClawHub 技能 CLI 安全分析器，20+ 恶意指标匹配，风险评分 0-100 | 3.6k | 🟢 | `security`, `audit`, `cli` |
| [Clawith (OpenClaw for Teams)](https://github.com/dataelement/Clawith) | OpenClaw 团队版，多智能体协作平台，每个 Agent 有持久身份和记忆 | 2.6k | 🔴 | `team`, `collaboration`, `skills` |
| [Snyk Agent Scan](https://github.com/snyk/agent-scan) | AI Agent、MCP Server 和技能的安全扫描器，检测 prompt injectio… | 2.0k | 🟢 | `security`, `scanning`, `mcp` |
| [ClawSec](https://github.com/prompt-security/clawsec) | OpenClaw 完整安全套件：漂移检测、实时安全建议、自动审计、技能完整性验证 | 862 | 🟢 | `security`, `audit`, `openclaw` |
| [OpenClaw Security Monitor](https://github.com/adibirzu/openclaw-security-monitor) | 主动安全监控：41 点威胁扫描、48 个修复脚本、Web 仪表板、Telegram 告警 | 29 | 🟢 | `security`, `monitoring`, `runtime` |
| [ClawSecure](https://github.com/ClawSecure/clawsecure-openclaw-security) | 免费 OpenClaw 安全扫描器，2890+ 智能体已审计，三层审计协议，OWASP ASI … | 20 | 🟢 | `security`, `audit`, `owasp` |
| Healthcheck | 安全审计和健康检查工具 | - | 🔴 | `security`, `audit`, `health` |
| Bitdefender AI Skills Checker | 免费在线 AI 技能安全检查器，AI 驱动分析技能文件，检测后门/数据外传/prompt inj… | - | 🟢 | `security`, `audit`, `scanning` |

### OpenClaw Skills

| 工具 | 说明 | Stars | 安全 | 标签 |
| --- | --- | ---: | :---: | --- |
| Podcast Reader | 播客内容转结构化笔记，提取播客中的关键信息 | - | 🔴 | `podcast`, `content`, `notes` |
| GitHub to Skills | 将 GitHub 项目转为 Claude Code 可调用的 Skill | - | 🔴 | `github`, `skills`, `conversion` |
| Skill Manager | Skill 统一管理、安装、更新工具 | - | 🔴 | `skills`, `management`, `install` |
| Skill Evolution Manager | Skill 自动迭代、优化升级管理器 | - | 🔴 | `skills`, `evolution`, `optimization` |
| MCP Builder | MCP 服务器快速构建工具 | - | 🔴 | `mcp`, `builder`, `server` |
| PPTX Skill | PPT 文件内容处理与生成 | - | 🔴 | `pptx`, `presentation`, `office` |
| Video Transcribe | 视频/音频自动转文字 | - | 🔴 | `video`, `audio`, `transcription` |
| JSON Canvas | JSON Canvas 画布文件编辑工具 | - | 🔴 | `canvas`, `json`, `visual` |

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
