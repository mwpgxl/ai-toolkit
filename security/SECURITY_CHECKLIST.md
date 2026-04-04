# AI Toolkit 安全审查检查清单

> 所有工具在正式使用前必须通过安全审查。
> 背景：2026 年 2 月 ClawHub 发现 824+ 恶意技能（ClawHavoc 事件），91% 结合 prompt injection + 恶意软件。

## 审查等级定义

| 等级 | 标签 | 含义 |
|------|------|------|
| ✅ | `trusted` | 已审查，来源可信（官方/知名公司出品） |
| 🟢 | `verified` | 已审查，代码安全，无已知风险 |
| 🟡 | `caution` | 已审查，存在轻微风险或注意事项 |
| 🔴 | `danger` | 已审查，存在已知安全风险 |
| ⬜ | `unreviewed` | 未审查 |

## 四层审查流程

### 第 1 层：安装前静态检查（必做）

**工具：** Skill Vetter + Bitdefender AI Skills Checker

```bash
# ClawHub 技能 - Skill Vetter 自动扫描
clawhub install skill-vetter
# 然后安装任何技能时会自动触发预检

# Bitdefender 在线检查（手动）
# 上传 SKILL.md 到 https://www.bitdefender.com/en-us/consumer/ai-skills-checker
```

**检查项：**
- [ ] SKILL.md 是否声明了所有需要的权限？
- [ ] 是否有未声明的网络请求（curl/wget/fetch）？
- [ ] 是否有可疑的文件系统操作（读取 ~/.ssh、~/.aws、~/.env）？
- [ ] 是否有 base64 编码的可疑内容？
- [ ] 是否有硬编码的外部 URL 或 IP？
- [ ] 发布者 GitHub 账号是否超过 1 周（ClawHub 基本要求）？

### 第 2 层：代码级深度审计

**工具：** Skill Security Auditor + Snyk Agent Scan

```bash
# CLI 风险评分 (0-100)
npx clawhub install skill-security-auditor
# 运行: analyze-skill.sh <skill-path>

# Snyk 供应链扫描
# 安装 snyk agent-scan，扫描 MCP Server 和技能
```

**检查项：**
- [ ] 风险评分是否 < 30？（30+ 需要人工复核）
- [ ] 是否包含 prompt injection 模式？
- [ ] 依赖项是否有已知漏洞？
- [ ] 是否有数据外传行为（向外部 API 发送数据）？

### 第 3 层：运行时监控（持续）

**工具：** ClawSec + OpenClaw Security Monitor

```bash
# ClawSec 安装
# 参考: https://github.com/prompt-security/clawsec

# Security Monitor 部署
# 参考: https://github.com/adibirzu/openclaw-security-monitor
```

**监控项：**
- [ ] SOUL.md / AGENTS.md 等配置文件完整性
- [ ] 异常网络连接（IOC 数据库比对）
- [ ] 内存投毒检测
- [ ] 进程树异常

### 第 4 层：全量审计（定期）

**工具：** ClawSecure

```bash
# 三层审计协议
# 参考: https://github.com/ClawSecure/clawsecure-openclaw-security
```

**周期：**
- 每月一次全量审计
- 每次安装新技能后立即审计
- ClawHub 安全公告发布后立即审计

## 已知威胁情报

| 威胁 | 描述 | 检测工具 |
|------|------|---------|
| ClawHavoc | 824+ 恶意技能，分发 AMOS 窃取器 | Security Monitor |
| Prompt Injection | 36% ClawHub 技能含注入（Snyk 数据） | Snyk Agent Scan |
| 数据外传 | 如 CapabilityEvolver 向飞书发送数据 | Skill Vetter |
| CVE-2026-25253 | OpenClaw 已知漏洞 | Security Monitor |
| 供应链攻击 | 伪装成热门技能的恶意版本 | Bitdefender |

## 高风险操作白名单

以下操作需要额外人工确认：
- 任何请求 `~/.ssh/`、`~/.aws/`、`~/.env` 访问的技能
- 任何需要 root/sudo 权限的技能
- 任何需要向外部服务器发送数据的技能
- 任何修改 Git 配置或 commit hook 的技能
- 任何请求浏览器 Cookie 或凭证的技能
