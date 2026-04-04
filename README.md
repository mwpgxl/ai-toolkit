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

## 工具分类

| 分类 | 说明 | 数量 |
| --- | --- | --- |
| MCP Server | MCP 协议服务器 | - |
| Skill | Claude Code 技能 | - |
| AI Agent | AI 智能体/框架 | - |
| CLI Tool | 命令行工具 | - |
| Browser Tool | 浏览器/网页工具 | - |
| Voice Tool | 语音工具 | - |
| Finance | 金融投资工具 | - |
| Productivity | 效率/生产力工具 | - |
| Dev Tool | 开发辅助工具 | - |
| OpenClaw Skill | OpenClaw 生态技能 | - |

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
