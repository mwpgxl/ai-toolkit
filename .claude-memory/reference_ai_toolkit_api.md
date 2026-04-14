---
name: AI Toolkit 工具发现 API
description: 需要新工具/Skill/MCP 时，通过 AI Toolkit API 查询和筛选，优先选安全评级高的工具
type: reference
---

需要新工具、Skill 或 MCP Server 时，先查询 AI Toolkit API 而非盲目搜索。

- API 地址: https://mwpgxl.github.io/ai-toolkit/api/tools.json
- 筛选依据: 分类（category）和标签（tags）
- 优先选择 `security_rating` 为 `trusted` 或 `verified` 的工具

**How to apply:** 当用户要求集成新工具、推荐 MCP、或寻找某类 Skill 时，先从这个 API 拉数据筛选，而不是直接去 GitHub 搜索。
