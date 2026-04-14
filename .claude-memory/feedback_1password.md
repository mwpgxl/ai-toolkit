---
name: 用 1Password CLI 获取凭证
description: 需要 API key 或凭证时，主动用 op CLI 从 1Password 读取，不要让用户手动去找
type: feedback
---

需要 API key、密码、凭证时，直接用 `op` CLI 从 1Password 获取，不要让用户自己去找然后粘贴。

**Why:** 用户是 1Password 重度用户，op CLI 已安装（v2.33.0）。用户明确说"不要每次都让我自己去给你找"。

**How to apply:**
- 需要凭证时先 `op vault list` 找到合适的仓库
- 用 `op item list --vault "仓库名"` 查找条目
- 用 `op read "op://仓库名/条目名/字段名"` 读取值
- 主要仓库：`Claude Code Keys`（API keys）、`Personal`、`团队账号`、`金融信息`
- 用环境变量传递敏感值给脚本，避免在命令行中直接显示
