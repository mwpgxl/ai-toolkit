---
name: 1Password 仓库结构
description: 用户的 1Password 仓库布局，用于查找 API keys 和凭证
type: reference
---

1Password CLI: `/opt/homebrew/bin/op` v2.33.0

仓库列表：
- **Claude Code Keys** — API keys 和服务凭证（OpenRouter、GSC、WooCommerce、Feishu、TrackMage、Ahrefs、Gemini、17TRACK、WordPress）
- **Personal** — 个人账号
- **团队账号** — 团队共享凭证
- **金融信息** — 金融相关凭证

读取方式：`op read "op://Claude Code Keys/条目名/字段名"`
