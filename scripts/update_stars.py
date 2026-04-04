#!/usr/bin/env python3
"""
GitHub Star 自动更新脚本
从 GitHub API 获取最新的 Star 数量并更新 tools.json
"""

import contextlib
import json
import logging
import os
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import requests

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
CATALOG_FILE = ROOT_DIR / "catalog" / "tools.json"

# GitHub API 配置
GITHUB_API = "https://api.github.com"
# 优先使用环境变量中的 token，可大幅提升 API 限额（5000/h vs 60/h）
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def validate_github_token(token: str) -> bool:
    """
    验证 GitHub Token 格式是否合法

    支持的格式:
      - ghp_ : 个人访问令牌 (classic)
      - gho_ : OAuth 访问令牌
      - ghu_ : GitHub App 用户令牌
      - ghs_ : GitHub App 安装令牌
      - github_pat_ : 细粒度个人访问令牌
    """
    if not token:
        return False
    valid_prefixes = ("ghp_", "gho_", "ghu_", "ghs_", "github_pat_")
    return token.startswith(valid_prefixes)


def get_headers() -> dict:
    """获取 GitHub API 请求头"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def extract_repo_from_url(url: str) -> str | None:
    """从 GitHub URL 中提取 owner/repo"""
    if not url:
        return None
    match = re.match(r"https?://github\.com/([^/]+/[^/]+?)(?:\.git)?(?:/.*)?$", url)
    return match.group(1) if match else None


def fetch_repo_info(owner_repo: str) -> dict | None:
    """从 GitHub API 获取仓库信息，返回 None 表示失败"""
    url = f"{GITHUB_API}/repos/{owner_repo}"
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "description": data.get("description", ""),
                "language": data.get("language", ""),
                "topics": data.get("topics", []),
                "updated_at": data.get("updated_at", ""),
                "archived": data.get("archived", False),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
            }
        elif resp.status_code == 404:
            logger.warning("仓库不存在: %s", owner_repo)
        elif resp.status_code == 403:
            # 触发速率限制，记录错误
            logger.error("API 限额已用完 (403): %s，请设置 GITHUB_TOKEN 环境变量", owner_repo)
            return None
        else:
            logger.warning("请求失败 (%d): %s", resp.status_code, owner_repo)
    except requests.RequestException as e:
        logger.error("网络错误: %s", e)
    return None


def check_rate_limit() -> dict:
    """检查 GitHub API 剩余配额"""
    url = f"{GITHUB_API}/rate_limit"
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            core = data["resources"]["core"]
            return {
                "remaining": core["remaining"],
                "limit": core["limit"],
                "reset": datetime.fromtimestamp(core["reset"], tz=UTC).isoformat(),
            }
    except requests.RequestException:
        pass
    return {"remaining": 0, "limit": 0, "reset": "unknown"}


def _fetch_single_tool(tool: dict) -> tuple[dict, dict | None, str | None]:
    """
    获取单个工具的 GitHub 信息（供线程池调用）

    返回: (tool, info, repo) 三元组
    """
    repo = extract_repo_from_url(tool["github_url"])
    if not repo:
        logger.warning("无法解析 URL: %s", tool["github_url"])
        return tool, None, None
    info = fetch_repo_info(repo)
    return tool, info, repo


def update_catalog() -> None:
    """更新工具目录中的 GitHub 信息"""
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
    if not tools:
        logger.error("工具列表为空")
        sys.exit(1)

    # 验证 GITHUB_TOKEN 格式
    if GITHUB_TOKEN:
        if not validate_github_token(GITHUB_TOKEN):
            logger.error("GITHUB_TOKEN 格式无效，应以 ghp_/gho_/ghu_/ghs_/github_pat_ 开头")
            sys.exit(1)
    else:
        logger.info("提示: 设置 GITHUB_TOKEN 环境变量可将限额从 60/h 提升到 5000/h")
        logger.info("  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx")

    # 检查 API 配额
    rate = check_rate_limit()
    logger.info(
        "GitHub API 配额: %d/%d (重置时间: %s)",
        rate["remaining"],
        rate["limit"],
        rate["reset"],
    )

    github_tools = [t for t in tools if t.get("github_url")]
    logger.info("共 %d 个工具，其中 %d 个有 GitHub 地址", len(tools), len(github_tools))

    # 使用线程池并行获取，max_workers=5 以尊重速率限制
    updated_count = 0
    failure_count = 0
    results: list[tuple[dict, dict | None, str | None]] = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_index = {executor.submit(_fetch_single_tool, tool): idx for idx, tool in enumerate(github_tools)}
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                result = future.result()
                results.append((idx, result))
            except Exception as e:
                logger.error("获取工具信息时发生异常: %s", e)
                failure_count += 1

    # 按原始顺序排序后处理结果
    results.sort(key=lambda x: x[0])

    for idx, (tool, info, repo) in results:
        display_name = f"[{idx + 1}/{len(github_tools)}] {tool['name']}"
        if repo is None:
            # URL 解析失败，已在 _fetch_single_tool 中记录警告
            continue

        if info:
            old_stars = tool.get("stars", 0)
            tool["stars"] = info["stars"]
            tool["forks"] = info["forks"]
            tool["github_language"] = info["language"]
            tool["github_archived"] = info["archived"]
            tool["last_github_update"] = info["updated_at"]

            if info.get("description") and not tool.get("description_en"):
                tool["description_en"] = info["description"]

            diff = info["stars"] - old_stars
            diff_str = f" (+{diff})" if diff > 0 else f" ({diff})" if diff < 0 else ""
            logger.info("%s (%s) — ⭐ %d%s", display_name, repo, info["stars"], diff_str)
            updated_count += 1
        else:
            logger.warning("%s (%s) — 跳过", display_name, repo)
            failure_count += 1

    # 更新元数据
    catalog["meta"]["last_updated"] = datetime.now(UTC).isoformat()
    catalog["meta"]["total_tools"] = len(tools)

    # 原子写入：先写临时文件，再 os.replace 替换目标文件
    catalog_dir = CATALOG_FILE.parent
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=catalog_dir,
            suffix=".tmp",
            delete=False,
        ) as tmp_f:
            json.dump(catalog, tmp_f, ensure_ascii=False, indent=2)
            tmp_path = tmp_f.name
        os.replace(tmp_path, CATALOG_FILE)
    except OSError as e:
        logger.error("写入文件失败: %s", e)
        # 清理临时文件（如果存在）
        if "tmp_path" in locals():
            with contextlib.suppress(OSError):
                os.unlink(tmp_path)
        sys.exit(1)

    logger.info("更新完成! 成功更新 %d/%d 个工具", updated_count, len(github_tools))
    logger.info("数据已写入: %s", CATALOG_FILE)

    # 如果有失败的请求，以非零状态码退出
    if failure_count > 0:
        logger.error("有 %d 个工具获取失败", failure_count)
        sys.exit(1)


if __name__ == "__main__":
    update_catalog()
