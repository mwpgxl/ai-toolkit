#!/usr/bin/env python3
"""
安全审查脚本 v2.0
多维度安全评估：来源信任 / GitHub 仓库健康 / 代码扫描 / 已知威胁 / 维护状态

用法:
    python scripts/security_audit.py                  # 全量审计（离线，不调 API）
    python scripts/security_audit.py --deep           # 深度审计（调 GitHub API + 扫描代码）
    python scripts/security_audit.py --deep --id firecrawl  # 只审计单个工具
"""

import argparse
import json
import logging
import os
import re
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

# 配置日志格式
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# API 限流延迟（秒），可按需调整
API_RATE_LIMIT_DELAY: float = 0.3

ROOT_DIR = Path(__file__).parent.parent
CATALOG_FILE = ROOT_DIR / "catalog" / "tools.json"
REPORT_FILE = ROOT_DIR / "security" / "audit_report.md"

GITHUB_API = "https://api.github.com"
_RAW_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# GitHub Token 前缀白名单
_VALID_TOKEN_PREFIXES: tuple[str, ...] = ("ghp_", "gho_", "github_pat_", "ghs_")
# Token 合理长度范围
_TOKEN_MIN_LENGTH: int = 20
_TOKEN_MAX_LENGTH: int = 255


def validate_github_token(token: str) -> bool:
    """
    校验 GitHub Token 格式是否合法。
    检查前缀和长度，不发起网络请求。
    """
    if not token:
        return False
    if not token.startswith(_VALID_TOKEN_PREFIXES):
        logger.warning(
            "GITHUB_TOKEN 格式无效：必须以 %s 开头",
            " / ".join(_VALID_TOKEN_PREFIXES),
        )
        return False
    if not (_TOKEN_MIN_LENGTH <= len(token) <= _TOKEN_MAX_LENGTH):
        logger.warning(
            "GITHUB_TOKEN 长度异常（%d 字符），有效范围 %d-%d",
            len(token),
            _TOKEN_MIN_LENGTH,
            _TOKEN_MAX_LENGTH,
        )
        return False
    return True


# 仅在格式合法时使用 Token
GITHUB_TOKEN: str = _RAW_GITHUB_TOKEN if validate_github_token(_RAW_GITHUB_TOKEN) else ""


# ============================================================
# 威胁情报数据库
# ============================================================

# 已知可信来源
TRUSTED_ORGS = {
    "microsoft",
    "google",
    "anthropic",
    "bytedance",
    "openclaw",
    "googleworkspace",
    "mendableai",
    "ComposioHQ",
    "tavily-ai",
    "apify",
    "larksuite",
    "QwenLM",
    "prompt-security",
    "snyk",
    "ClawSecure",
    "TauricResearch",
    "jina-ai",
    "gsd-build",
    "rtk-ai",
    "obra",
}

# 已知安全风险（硬编码情报）
KNOWN_RISKS = {
    "capability-evolver": {
        "rating": "danger",
        "reason": "ClawHub Security 标记：未声明的数据外传到飞书/字节跳动服务器",
        "source": "https://github.com/openclaw/clawhub/issues/95",
    },
}

# ClawHavoc 恶意指标 (基于 Snyk ToxicSkills 研究)
MALICIOUS_PATTERNS = [
    # 数据外传
    (r"curl\s+.*?\|\s*sh", "通过 curl 管道执行远程脚本", 40),
    (r"wget\s+.*?-o\s*-\s*\|\s*sh", "通过 wget 管道执行远程脚本", 40),
    (r"curl\s+.*?-d\s+.*?\$HOME", "curl 外传 HOME 目录数据", 35),
    (r"curl\s+.*?-d\s+.*?\.ssh", "curl 外传 SSH 密钥", 50),
    (r"curl\s+.*?-d\s+.*?\.env", "curl 外传环境变量", 50),
    (r"curl\s+.*?-d\s+.*?\.aws", "curl 外传 AWS 凭证", 50),
    # 敏感文件访问
    (r"cat\s+~?/\.ssh/", "读取 SSH 密钥", 40),
    (r"cat\s+~?/\.env", "读取 .env 文件", 35),
    (r"cat\s+~?/\.aws/", "读取 AWS 凭证", 40),
    (r"cat\s+~?/\.gnupg/", "读取 GPG 密钥", 40),
    (r"cat\s+~?/\.gitconfig", "读取 Git 配置", 15),
    (r"cat\s+~?/\.npmrc", "读取 npm 凭证", 30),
    (r"cat\s+~?/\.pypirc", "读取 PyPI 凭证", 30),
    (r"/etc/shadow", "访问系统密码文件", 50),
    (r"keychain|keyring|wallet", "访问系统密钥链", 30),
    # 代码执行
    (r"eval\s*\(", "eval() 动态执行代码", 25),
    (r"exec\s*\(", "exec() 动态执行代码", 25),
    (r"subprocess\.call.*shell\s*=\s*true", "shell=True 命令注入风险", 30),
    (r"os\.system\s*\(", "os.system() 命令执行", 25),
    (r"__import__\s*\(", "动态导入模块", 20),
    # 编码混淆
    (r"base64\.(b64)?decode", "Base64 解码（可能隐藏恶意载荷）", 20),
    (r"\\x[0-9a-f]{2}\\x[0-9a-f]{2}", "十六进制编码字符串", 15),
    (r"\\u[0-9a-f]{4}\\u[0-9a-f]{4}", "Unicode 编码字符串", 10),
    (r"atob\s*\(", "JS Base64 解码", 20),
    (r"string\.fromcharcode", "JS 字符编码混淆", 20),
    # 网络行为
    (r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "硬编码 IP 地址请求", 30),
    (r"ngrok\.io|serveo\.net|localhost\.run", "使用隧道服务（可能是 C2）", 40),
    (r"discord\.com/api/webhooks", "Discord Webhook 外传", 35),
    (r"hooks\.slack\.com", "Slack Webhook 外传", 25),
    (r"api\.telegram\.org/bot", "Telegram Bot 外传", 25),
    # 权限提升
    (r"sudo\s+", "请求 sudo 权限", 20),
    (r"chmod\s+[0-7]*7[0-7]*\s", "设置全局可执行权限", 15),
    (r"chown\s+root", "修改文件所有者为 root", 25),
    # Prompt Injection
    (r"ignore\s+(?:all\s+)?previous\s+instructions", "Prompt Injection: 忽略指令", 50),
    (r"you\s+are\s+now\s+(?:a|an|dan)", "Prompt Injection: 角色覆盖", 50),
    (r"system\s*:\s*you\s+(?:must|should|will)", "Prompt Injection: 伪造系统提示", 40),
    (r"do\s+not\s+reveal\s+(?:this|these)", "Prompt Injection: 隐藏指令", 35),
]

# 可疑域名
SUSPICIOUS_DOMAINS = [
    "feishu.cn",
    "lark.suite",
    "dingtalk.com",  # 未声明的中国服务
    "pastebin.com",
    "paste.ee",
    "ghostbin.co",  # 粘贴板服务
    "bit.ly",
    "tinyurl.com",
    "t.co",  # 短链接
    "raw.githubusercontent.com",  # 可能加载远程代码
]


# ============================================================
# GitHub API 工具函数
# ============================================================


def get_headers() -> dict:
    """获取 GitHub API 请求头"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def extract_repo(url: str) -> str | None:
    """从 GitHub URL 提取 owner/repo"""
    if not url:
        return None
    match = re.match(r"https?://github\.com/([^/]+/[^/]+?)(?:\.git)?(?:/.*)?$", url)
    return match.group(1) if match else None


def fetch_repo_data(repo: str) -> dict | None:
    """从 GitHub API 获取仓库完整信息"""
    try:
        resp = requests.get(f"{GITHUB_API}/repos/{repo}", headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None


def fetch_file_content(repo: str, path: str) -> str | None:
    """从 GitHub 获取文件内容（用于扫描 SKILL.md / README 等）"""
    # 先尝试常见路径
    for p in [path, path.upper(), path.lower()]:
        try:
            url = f"https://raw.githubusercontent.com/{repo}/main/{p}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.text
            # 也尝试 master 分支
            url = f"https://raw.githubusercontent.com/{repo}/master/{p}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.text
        except requests.RequestException:
            pass
    return None


# ============================================================
# 评估维度
# ============================================================


def assess_source_trust(tool: dict) -> tuple[float, list[str]]:
    """
    维度 1：来源信任度 (0-25 分)
    检查：开发者身份、组织可信度
    """
    score = 0.0
    findings = []
    github_url = tool.get("github_url", "")
    clawhub_url = tool.get("clawhub_url", "")
    org = extract_repo(github_url)
    org_name = org.split("/")[0] if org else None

    if org_name and org_name.lower() in {o.lower() for o in TRUSTED_ORGS}:
        score = 25
        findings.append(f"✅ 可信组织: {org_name}")
    elif github_url and clawhub_url:
        score = 18
        findings.append("✅ 双平台发布 (GitHub + ClawHub)")
    elif github_url:
        score = 15
        findings.append(f"ℹ️ GitHub 来源: {org_name or 'unknown'}")
    elif clawhub_url:
        score = 10
        findings.append("ℹ️ 仅 ClawHub 来源（无法审计源码）")
    else:
        score = 0
        findings.append("❌ 无任何来源 URL")

    return score, findings


def assess_community(tool: dict) -> tuple[float, list[str]]:
    """
    维度 2：社区信任度 (0-20 分)
    检查：Star 数量、Fork 数量
    """
    score = 0.0
    findings = []
    stars = tool.get("stars", 0)
    tool.get("forks", 0)

    if stars >= 50000:
        score = 20
        findings.append(f"✅ 顶级项目 (⭐ {stars:,})")
    elif stars >= 10000:
        score = 18
        findings.append(f"✅ 高人气项目 (⭐ {stars:,})")
    elif stars >= 1000:
        score = 12
        findings.append(f"🟡 中等人气 (⭐ {stars:,})")
    elif stars >= 100:
        score = 7
        findings.append(f"🟡 小型项目 (⭐ {stars})")
    elif stars > 0:
        score = 3
        findings.append(f"⚠️ 低人气 (⭐ {stars})")
    else:
        score = 0
        findings.append("⬜ 无 Star 数据")

    return score, findings


def assess_repo_health(tool: dict, repo_data: dict | None) -> tuple[float, list[str]]:
    """
    维度 3：仓库健康度 (0-25 分) — 需要 --deep 模式
    检查：是否归档、最后更新时间、License、是否有安全策略
    """
    if not repo_data:
        return 10, ["⬜ 未进行仓库健康检查（需 --deep 模式）"]

    score = 0.0
    findings = []

    # 是否归档
    if repo_data.get("archived"):
        score -= 5
        findings.append("🔴 仓库已归档（不再维护）")
    else:
        score += 5
        findings.append("✅ 仓库活跃")

    # 最后更新时间
    updated = repo_data.get("pushed_at", "")
    if updated:
        last_push = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        days_ago = (datetime.now(UTC) - last_push).days
        if days_ago <= 30:
            score += 8
            findings.append(f"✅ 近期活跃（{days_ago} 天前更新）")
        elif days_ago <= 180:
            score += 5
            findings.append(f"🟡 半年内有更新（{days_ago} 天前）")
        elif days_ago <= 365:
            score += 2
            findings.append(f"🟡 半年以上未更新（{days_ago} 天前）")
        else:
            findings.append(f"⚠️ 超过一年未更新（{days_ago} 天前）")

    # License
    license_info = repo_data.get("license")
    if license_info and license_info.get("spdx_id") != "NOASSERTION":
        score += 5
        findings.append(f"✅ 有许可证: {license_info.get('spdx_id', 'unknown')}")
    else:
        score += 1
        findings.append("🟡 无许可证或未声明")

    # 贡献者数量（通过 fork 间接判断）
    forks = repo_data.get("forks_count", 0)
    if forks >= 100:
        score += 4
        findings.append(f"✅ 活跃社区 ({forks} forks)")
    elif forks >= 10:
        score += 2
        findings.append(f"ℹ️ 有社区参与 ({forks} forks)")

    # 是否有 description
    if not repo_data.get("description"):
        score -= 2
        findings.append("🟡 无仓库描述")

    # 开放的 issue 数量
    issues = repo_data.get("open_issues_count", 0)
    if issues > 500:
        score -= 2
        findings.append(f"🟡 大量未关闭 issue ({issues})")

    return max(0, min(25, score)), findings


def assess_code_safety(tool: dict, content: str | None) -> tuple[float, list[str]]:
    """
    维度 4：代码安全性 (0-30 分) — 需要 --deep 模式
    检查：SKILL.md/README 中的可疑模式、恶意指标
    """
    if not content:
        return 15, ["⬜ 未进行代码扫描（需 --deep 模式）"]

    score = 30.0  # 从满分开始扣
    findings = []
    content_lower = content.lower()

    # 扫描恶意模式
    triggered = []
    for pattern, desc, penalty in MALICIOUS_PATTERNS:
        matches = re.findall(pattern, content_lower)
        if matches:
            score -= penalty
            triggered.append((desc, penalty, len(matches)))

    if triggered:
        for desc, penalty, count in sorted(triggered, key=lambda x: -x[1]):
            icon = "🔴" if penalty >= 30 else "🟡" if penalty >= 15 else "ℹ️"
            findings.append(f"{icon} {desc} (x{count}, -{penalty}分)")
    else:
        findings.append("✅ 未检测到已知恶意模式")

    # 扫描可疑域名
    for domain in SUSPICIOUS_DOMAINS:
        if domain in content_lower:
            score -= 15
            findings.append(f"🔴 可疑域名: {domain}")

    # 检查文件大小（异常大的 SKILL.md 可能隐藏载荷）
    if len(content) > 50000:
        score -= 5
        findings.append(f"🟡 文件异常大 ({len(content):,} 字符)")

    # 检查是否有过多的外部 URL
    urls = re.findall(r"https?://[^\s\)\"'`]+", content)
    unique_domains = set()
    for url in urls:
        match = re.match(r"https?://([^/]+)", url)
        if match:
            unique_domains.add(match.group(1))
    if len(unique_domains) > 15:
        score -= 5
        findings.append(f"🟡 引用大量外部域名 ({len(unique_domains)} 个)")

    return max(0, min(30, score)), findings


# ============================================================
# 主评估逻辑
# ============================================================


def assess_tool(tool: dict, deep: bool = False) -> dict:
    """
    对单个工具进行多维度安全评估

    评分体系 (总分 100):
      - 来源信任度: 25 分
      - 社区信任度: 20 分
      - 仓库健康度: 25 分 (deep 模式)
      - 代码安全性: 30 分 (deep 模式)
    """
    tid = tool["id"]

    # 检查已知风险（直接标记，不走评分）
    if tid in KNOWN_RISKS:
        risk = KNOWN_RISKS[tid]
        return {
            "rating": "danger",
            "score": 5,
            "dimensions": {"来源信任": 0, "社区信任": 0, "仓库健康": 0, "代码安全": 0},
            "issues": [f"🔴 已知风险: {risk['reason']}", f"ℹ️ 来源: {risk['source']}"],
        }

    # 已手动标记为 trusted 的安全工具
    if tool.get("security_rating") == "trusted":
        s1, f1 = assess_source_trust(tool)
        s2, f2 = assess_community(tool)
        return {
            "rating": "trusted",
            "score": 95,
            "dimensions": {"来源信任": s1, "社区信任": s2, "仓库健康": 25, "代码安全": 30},
            "issues": f1 + f2 + ["✅ 已标记为可信安全工具"],
        }

    # 四维度评估
    s1, f1 = assess_source_trust(tool)
    s2, f2 = assess_community(tool)

    repo_data = None
    content = None
    github_url = tool.get("github_url", "")
    repo = extract_repo(github_url)

    if deep and repo:
        repo_data = fetch_repo_data(repo)
        # 扫描 SKILL.md 或 README.md
        for fname in ["SKILL.md", "README.md", "readme.md"]:
            content = fetch_file_content(repo, fname)
            if content:
                break
        time.sleep(API_RATE_LIMIT_DELAY)  # 避免限流

    s3, f3 = assess_repo_health(tool, repo_data)
    s4, f4 = assess_code_safety(tool, content)

    total = s1 + s2 + s3 + s4

    # 确定评级
    if total >= 80:
        rating = "verified"
    elif total >= 55:
        rating = "caution"
    else:
        rating = "danger"

    return {
        "rating": rating,
        "score": round(total),
        "dimensions": {
            "来源信任": round(s1),
            "社区信任": round(s2),
            "仓库健康": round(s3),
            "代码安全": round(s4),
        },
        "issues": f1 + f2 + f3 + f4,
    }


# ============================================================
# 报告生成
# ============================================================


def generate_report(tools: list, results: dict, stats: dict, mode: str) -> str:
    """生成 Markdown 审计报告"""
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# 安全审计报告",
        f"\n> 审计时间: {now}",
        f"> 审计模式: {'🔬 深度审计 (GitHub API + 代码扫描)' if mode == 'deep' else '⚡ 快速审计 (离线)'}",
        f"> 工具总数: {len(tools)}",
        "\n## 评分体系说明\n",
        "| 维度 | 满分 | 检查内容 |",
        "| --- | --- | --- |",
        "| 来源信任 | 25 | 开发者/组织身份、双平台发布 |",
        "| 社区信任 | 20 | GitHub Star 数量 |",
        "| 仓库健康 | 25 | 归档状态、更新频率、许可证、社区活跃度 |",
        "| 代码安全 | 30 | 恶意模式扫描、可疑域名、prompt injection |",
        "\n## 统计摘要\n",
        "| 等级 | 数量 | 占比 |",
        "| --- | --- | --- |",
    ]

    for level, label in [
        ("trusted", "✅ 可信"),
        ("verified", "🟢 已验证"),
        ("caution", "🟡 注意"),
        ("danger", "🔴 危险"),
        ("unreviewed", "⬜ 未审查"),
    ]:
        count = stats.get(level, 0)
        pct = count / len(tools) * 100 if tools else 0
        lines.append(f"| {label} | {count} | {pct:.1f}% |")

    # 危险工具详情
    danger = [(t, results[t["id"]]) for t in tools if results[t["id"]]["rating"] == "danger"]
    if danger:
        lines.append(f"\n## 🔴 危险工具 ({len(danger)} 个)\n")
        for tool, res in danger:
            dims = res.get("dimensions", {})
            lines.append(f"### {tool['name']} — 评分: {res['score']}/100\n")
            lines.append("| 维度 | 得分 |")
            lines.append("| --- | --- |")
            for d, v in dims.items():
                lines.append(f"| {d} | {v} |")
            lines.append("\n**发现：**\n")
            for issue in res["issues"]:
                lines.append(f"- {issue}")
            lines.append("")

    # 注意工具
    caution = [(t, results[t["id"]]) for t in tools if results[t["id"]]["rating"] == "caution"]
    if caution:
        lines.append(f"\n## 🟡 需注意的工具 ({len(caution)} 个)\n")
        lines.append("| 名称 | 评分 | 来源 | 社区 | 健康 | 代码 | 主要问题 |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for tool, res in sorted(caution, key=lambda x: x[1]["score"]):
            dims = res.get("dimensions", {})
            top_issue = next((i for i in res["issues"] if i.startswith(("🔴", "🟡", "⚠️", "❌"))), "—")
            lines.append(
                f"| {tool['name']} | {res['score']} | "
                f"{dims.get('来源信任', '—')} | {dims.get('社区信任', '—')} | "
                f"{dims.get('仓库健康', '—')} | {dims.get('代码安全', '—')} | {top_issue[:50]} |"
            )

    # 已验证工具
    verified = [(t, results[t["id"]]) for t in tools if results[t["id"]]["rating"] in ("trusted", "verified")]
    lines.append(f"\n## ✅ 可信/已验证工具 ({len(verified)} 个)\n")
    for tool, res in sorted(verified, key=lambda x: -x[1]["score"]):
        dims = res.get("dimensions", {})
        lines.append(
            f"- **{tool['name']}** ({res['score']}分) — 来源{dims.get('来源信任', '?')}/社区{dims.get('社区信任', '?')}/健康{dims.get('仓库健康', '?')}/代码{dims.get('代码安全', '?')}"
        )

    return "\n".join(lines)


# ============================================================
# 主函数
# ============================================================


def run_audit():
    """执行安全审计"""
    parser = argparse.ArgumentParser(description="AI Toolkit 安全审计")
    parser.add_argument("--deep", action="store_true", help="深度审计：调用 GitHub API + 扫描代码")
    parser.add_argument("--id", type=str, help="只审计指定工具 ID")
    args = parser.parse_args()

    if not CATALOG_FILE.exists():
        logger.error("目录文件不存在: %s", CATALOG_FILE)
        sys.exit(1)

    with open(CATALOG_FILE, encoding="utf-8") as f:
        catalog = json.load(f)

    # Schema 校验
    from validate_schema import validate_catalog

    schema_path = ROOT_DIR / "catalog" / "tools_schema.json"
    is_valid, errors = validate_catalog(CATALOG_FILE, schema_path)
    if not is_valid:
        for err in errors:
            logger.warning("Schema: %s", err)

    tools = catalog.get("tools", [])
    if args.id:
        tools = [t for t in tools if t["id"] == args.id]
        if not tools:
            logger.error("未找到工具 ID: %s", args.id)
            sys.exit(1)

    mode = "deep" if args.deep else "quick"
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    logger.info("AI Toolkit 安全审计 v2.0")
    logger.info("时间: %s", now)
    logger.info("模式: %s", "深度 (GitHub API + 代码扫描)" if args.deep else "快速 (离线)")
    logger.info("工具: %d 个", len(tools))

    if args.deep and not GITHUB_TOKEN:
        logger.warning("未设置 GITHUB_TOKEN，API 限额较低")
        logger.info("提示: export GITHUB_TOKEN=$(op read 'op://Personal/ai-toolkit/token')")

    results = {}
    stats = {"trusted": 0, "verified": 0, "caution": 0, "danger": 0, "unreviewed": 0}

    for i, tool in enumerate(tools, 1):
        assessment = assess_tool(tool, deep=args.deep)
        results[tool["id"]] = assessment
        rating = assessment["rating"]
        stats[rating] = stats.get(rating, 0) + 1

        # 更新 tools.json
        tool["security_rating"] = rating
        tool["security_score"] = assessment["score"]
        tool["security_dimensions"] = assessment.get("dimensions", {})

        dims = assessment.get("dimensions", {})
        dim_str = (
            f"[来源{dims.get('来源信任', '?'):>2}"
            f"/社区{dims.get('社区信任', '?'):>2}"
            f"/健康{dims.get('仓库健康', '?'):>2}"
            f"/代码{dims.get('代码安全', '?'):>2}]"
        )
        logger.info(
            "[%d/%d] %-45s %3d分 %s -> %s",
            i,
            len(tools),
            tool["name"][:45],
            assessment["score"],
            dim_str,
            rating,
        )

    # 保存
    all_tools = catalog.get("tools", [])
    if args.id:
        # 只更新单个工具
        for t in all_tools:
            if t["id"] == args.id:
                t.update(tools[0])
    catalog["meta"]["last_security_audit"] = now
    catalog["meta"]["security_audit_mode"] = mode

    # 原子写入 tools.json：先写临时文件，再 rename，防止进程中断导致数据损坏
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=CATALOG_FILE.parent,
            suffix=".tmp",
            delete=False,
        ) as tmp_f:
            json.dump(catalog, tmp_f, ensure_ascii=False, indent=2)
            tmp_path = Path(tmp_f.name)
        os.replace(tmp_path, CATALOG_FILE)
    except OSError:
        logger.error("写入 %s 失败", CATALOG_FILE)
        # 清理可能残留的临时文件
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    # 生成报告（同样使用原子写入）
    report = generate_report(tools, results, stats, mode)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=REPORT_FILE.parent,
            suffix=".tmp",
            delete=False,
        ) as tmp_f:
            tmp_f.write(report)
            tmp_path = Path(tmp_f.name)
        os.replace(tmp_path, REPORT_FILE)
    except OSError:
        logger.error("写入 %s 失败", REPORT_FILE)
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    logger.info("=" * 70)
    logger.info("审计结果:")
    for level, label in [("trusted", "可信"), ("verified", "已验证"), ("caution", "注意"), ("danger", "危险")]:
        count = stats.get(level, 0)
        bar = "█" * count
        logger.info("  %s: %3d %s", label, count, bar)
    logger.info("报告: %s", REPORT_FILE)
    logger.info("数据: %s", CATALOG_FILE)

    danger_count = stats.get("danger", 0)
    if danger_count:
        logger.warning("发现 %d 个危险工具，请立即检查!", danger_count)


if __name__ == "__main__":
    run_audit()
