# AI Toolkit - Claude Code 配置

## 项目说明
这是一个 AI 工具目录库，用于管理 Claude Code Skills、MCP Servers、AI Agent 工具和 OpenClaw/ClawHub 技能。

## 开发命令
```bash
# 安装依赖（含开发工具）
pip install -e ".[dev]"

# 代码检查
ruff check scripts/          # lint
ruff format --check scripts/ # format 检查
ruff format scripts/         # 自动格式化

# 运行测试
pytest                       # 全量测试（150 个）
pytest -k "TestValidateSchema"  # 只跑某个测试类

# 业务脚本
python scripts/update_stars.py      # 更新 Star 数据
python scripts/generate_docs.py     # 生成分类文档
python scripts/recommend.py --type fullstack  # 推荐工具
python scripts/security_audit.py    # 安全审计（离线）
python scripts/security_audit.py --deep       # 深度审计（调 API）
python scripts/validate_schema.py   # JSON Schema 校验
```

## CI
- PR/push 到 main 时自动运行 `ruff check` + `ruff format --check` + `pytest`
- 每周一自动更新 Star 数据并生成文档

## 核心文件
- `catalog/tools.json` — 工具数据库（JSON 格式，所有工具信息的唯一数据源）
- `catalog/tools_schema.json` — JSON Schema 定义
- `catalog/by-category/` — 按分类生成的 Markdown 文档（由脚本生成，勿手动编辑）
- `pyproject.toml` — 项目配置（依赖、pytest、ruff）

## 工作流程
1. 添加新工具：编辑 `catalog/tools.json`
2. 更新 Star 数：运行 `python scripts/update_stars.py`
3. 生成文档：运行 `python scripts/generate_docs.py`
4. 推荐工具：运行 `python scripts/recommend.py --type <项目类型>`
5. 安全审计：运行 `python scripts/security_audit.py`
6. 提交前检查：运行 `ruff check scripts/ && pytest`

## 代码规范
- Python 3.11+，使用 `X | None` 替代 `Optional[X]`，`datetime.UTC` 替代 `timezone.utc`
- ruff 负责 lint + format，配置见 `pyproject.toml`
- 中文全角字符（，、（）、：）在字符串/注释/docstring 中是正常的，已在 ruff 配置中忽略

## 安全审查
- `security/SECURITY_CHECKLIST.md` — 四层审查流程和检查清单
- `security/audit_report.md` — 最新审计报告（由脚本生成）
- `scripts/security_audit.py` — 自动化安全评估脚本
- 所有工具都有 `security_rating` 字段：trusted/verified/caution/danger/unreviewed

## 工具来源
- `github_url` — GitHub 开源仓库地址
- `clawhub_url` — ClawHub (OpenClaw 技能市场) 地址

## 工具分类
- `mcp-server` — MCP 服务器
- `skill` — Claude Code Skill
- `ai-agent` — AI 智能体/框架
- `cli-tool` — 命令行工具
- `browser-tool` — 浏览器/网页工具
- `voice-tool` — 语音工具
- `finance` — 金融投资工具
- `productivity` — 效率/生产力工具
- `dev-tool` — 开发辅助工具
- `openclaw-skill` — OpenClaw/ClawHub 技能
