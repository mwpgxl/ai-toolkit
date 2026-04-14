---
name: browser-automation 项目
description: HubStudio 指纹浏览器 + Playwright 自动注册框架，当前对接 Dreamina (CapCut)
type: project
---

## 项目位置
`~/projects/browser-automation/`

## 技术栈
- Python 3.11 + Playwright + httpx + rich
- HubStudio 指纹浏览器（付费版，本地 API 端口 6873）
- Fastmail IMAP catch-all 邮箱接码（域名 tktkk.com）
- 新加坡代理池（SOCKS5/HTTP 格式 host:port:user:pass）

## 核心流程
创建 HubStudio 环境 + 代理 → 启动浏览器 → Playwright 连接 CDP → CapCut 注册（邮箱→密码→生日→OTP验证码）→ 导入 cookie → 关闭

## 关键发现（调试中积累）
- CapCut 注册用 `www.capcut.com/login`，不用 `dreamina.capcut.com/ai-tool/login`（后者需额外点击）
- 注册流程是 3 步：1) 邮箱+密码 2) 生日 3) 邮箱验证码
- 验证码在邮件标题里提取（HTML body 含 #000000 颜色代码会干扰 \d{6} 正则）
- OTP 是 6 个独立 input，用 `fill()` 逐个填入
- 生日下拉的 Month/Day 输入框被 span 遮挡，需要 `force=True` 点击
- HubStudio 浏览器关闭后 cookie 会自动保存，但额外通过 API import-cookie 更可靠
- HubStudio "打开指定网址" 功能只能通过 GUI 设置，API 不支持

## 运行
```bash
cd ~/projects/browser-automation
source .venv/bin/activate
python -m src.main              # 按 config.yaml 的 count 跑
```

**Why:** 用户需要批量注册 Dreamina 账号用于业务
**How to apply:** 下次用户要加新目标网站时，参考此项目结构；用户要求整理成可分享的 Skill
