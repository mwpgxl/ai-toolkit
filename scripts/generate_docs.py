#!/usr/bin/env python3
"""
从 tools.json 生成分类 Markdown 文档
"""

import contextlib
import json
import logging
import os
import re
import sys
import tempfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent
CATALOG_FILE = ROOT_DIR / "catalog" / "tools.json"
OUTPUT_DIR = ROOT_DIR / "catalog" / "by-category"
README_FILE = ROOT_DIR / "catalog" / "README.md"

# 分类名称映射
CATEGORY_NAMES = {
    "mcp-server": "MCP 服务器",
    "skill": "Claude Code Skills",
    "ai-agent": "AI 智能体/框架",
    "cli-tool": "命令行工具",
    "browser-tool": "浏览器/网页工具",
    "voice-tool": "语音工具",
    "finance": "金融投资工具",
    "productivity": "效率/生产力工具",
    "dev-tool": "开发辅助工具",
    "openclaw-skill": "OpenClaw Skills",
}


def stars_badge(stars: int) -> str:
    """生成 Star 数量显示"""
    if stars >= 10000 or stars >= 1000:
        return f"⭐ {stars / 1000:.1f}k"
    elif stars > 0:
        return f"⭐ {stars}"
    return ""


def generate_tool_entry(tool: dict) -> str:
    """生成单个工具的 Markdown 条目"""
    lines = []
    name = tool["name"]
    stars = stars_badge(tool.get("stars", 0))
    github = tool.get("github_url", "")

    # 标题行
    if github:
        lines.append(f"### [{name}]({github}) {stars}")
    else:
        lines.append(f"### {name} {stars}")

    # 描述
    if tool.get("description"):
        lines.append(f"\n{tool['description']}")

    # 详情表格
    details = []
    if tool.get("category"):
        details.append(f"| 分类 | {CATEGORY_NAMES.get(tool['category'], tool['category'])} |")
    if tool.get("use_cases"):
        details.append(f"| 适用场景 | {', '.join(tool['use_cases'])} |")
    if tool.get("install_cmd"):
        details.append(f"| 安装命令 | `{tool['install_cmd']}` |")
    if tool.get("tags"):
        details.append(f"| 标签 | {', '.join(f'`{t}`' for t in tool['tags'])} |")

    if details:
        lines.append("\n| 属性 | 值 |")
        lines.append("| --- | --- |")
        lines.extend(details)

    # 使用方法
    if tool.get("usage"):
        lines.append(f"\n**使用方法:** {tool['usage']}")

    lines.append("")
    return "\n".join(lines)


def generate_category_doc(category: str, tools: list) -> str:
    """生成单个分类的 Markdown 文档"""
    cat_name = CATEGORY_NAMES.get(category, category)
    now = datetime.now(UTC).strftime("%Y-%m-%d")

    # 按 Star 数降序排列
    tools_sorted = sorted(tools, key=lambda t: t.get("stars", 0), reverse=True)

    lines = [
        f"# {cat_name}",
        f"\n> 共 {len(tools)} 个工具 | 最后更新: {now}",
        "\n---\n",
    ]

    for tool in tools_sorted:
        lines.append(generate_tool_entry(tool))
        lines.append("---\n")

    return "\n".join(lines)


def generate_index(categories: dict) -> str:
    """生成总索引文档"""
    now = datetime.now(UTC).strftime("%Y-%m-%d")
    total = sum(len(tools) for tools in categories.values())

    lines = [
        "# AI 工具目录索引",
        f"\n> 共 {total} 个工具，{len(categories)} 个分类 | 最后更新: {now}\n",
    ]

    for cat, tools in sorted(categories.items()):
        cat_name = CATEGORY_NAMES.get(cat, cat)
        top_stars = max((t.get("stars", 0) for t in tools), default=0)
        lines.append(f"- [{cat_name}](by-category/{cat}.md) — {len(tools)} 个工具 (最高 {stars_badge(top_stars)})")

    return "\n".join(lines)


def sync_meta_count(data: dict) -> bool:
    """同步 meta.total_tools 与实际工具数量

    如果 meta.total_tools 与实际工具数不一致，则修正并原子写入 tools.json。

    Args:
        data: 完整的 tools.json 数据（包含 meta 和 tools 字段）

    Returns:
        bool: 如果修正了数量返回 True，否则返回 False
    """
    tools = data.get("tools", [])
    actual_count = len(tools)
    meta_count = data.get("meta", {}).get("total_tools", 0)

    if meta_count == actual_count:
        return False

    logger.info("meta.total_tools 不一致: 记录 %d，实际 %d，已修正", meta_count, actual_count)
    data["meta"]["total_tools"] = actual_count
    data["meta"]["last_updated"] = datetime.now(UTC).isoformat()

    # 原子写入 tools.json
    catalog_dir = CATALOG_FILE.parent
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=catalog_dir,
            suffix=".tmp",
            delete=False,
        ) as tmp_f:
            json.dump(data, tmp_f, ensure_ascii=False, indent=2)
            tmp_f.write("\n")
            tmp_path = tmp_f.name
        os.replace(tmp_path, CATALOG_FILE)
    except OSError as e:
        logger.error("写入 tools.json 失败: %s", e)
        # 清理临时文件（如果存在）
        if "tmp_path" in locals():
            with contextlib.suppress(OSError):
                os.unlink(tmp_path)
        raise

    return True


def update_catalog_readme(data: dict) -> None:
    """更新 catalog/README.md 中的工具数量和日期

    从实际数据中统计各分类工具数量，重新生成 README.md 中的统计表格行，
    并更新"最后更新"日期为今天。使用原子写入保证文件安全。

    Args:
        data: 完整的 tools.json 数据（包含 meta 和 tools 字段）
    """
    tools = data.get("tools", [])
    today = datetime.now(UTC).strftime("%Y-%m-%d")

    # 按分类统计工具数量
    categories: defaultdict[str, list[dict]] = defaultdict(list)
    for tool in tools:
        cat = tool.get("category", "other")
        categories[cat].append(tool)

    total = sum(len(t) for t in categories.values())
    num_categories = len(categories)

    # 生成各分类的统计行
    category_lines: list[str] = []
    for cat in sorted(categories.keys()):
        cat_tools = categories[cat]
        cat_name = CATEGORY_NAMES.get(cat, cat)
        top_stars = max((t.get("stars", 0) for t in cat_tools), default=0)
        star_text = f" (最高 {stars_badge(top_stars)})" if top_stars > 0 else ""
        category_lines.append(f"- [{cat_name}](by-category/{cat}.md) — {len(cat_tools)} 个工具{star_text}")

    # 如果 README 不存在，直接生成完整内容
    if not README_FILE.exists():
        logger.info("catalog/README.md 不存在，将生成新文件")
        content = _build_full_readme(total, num_categories, today, category_lines)
    else:
        # 读取现有 README 并替换统计内容
        with open(README_FILE, encoding="utf-8") as f:
            existing = f.read()
        content = _patch_readme(existing, total, num_categories, today, category_lines)

    # 原子写入 README.md
    readme_dir = README_FILE.parent
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=readme_dir,
            suffix=".tmp",
            delete=False,
        ) as tmp_f:
            tmp_f.write(content)
            tmp_path = tmp_f.name
        os.replace(tmp_path, README_FILE)
    except OSError as e:
        logger.error("写入 catalog/README.md 失败: %s", e)
        if "tmp_path" in locals():
            with contextlib.suppress(OSError):
                os.unlink(tmp_path)
        raise

    logger.info("catalog/README.md 已更新: 共 %d 个工具，%d 个分类", total, num_categories)


def _build_full_readme(total: int, num_categories: int, date: str, category_lines: list[str]) -> str:
    """构建完整的 README.md 内容

    Args:
        total: 工具总数
        num_categories: 分类数量
        date: 日期字符串
        category_lines: 各分类的 Markdown 行列表

    Returns:
        str: 完整的 README.md 内容
    """
    lines = [
        "# AI 工具目录索引",
        "",
        f"> 共 {total} 个工具，{num_categories} 个分类 | 最后更新: {date}",
        "",
    ]
    lines.extend(category_lines)
    # 确保文件末尾有换行
    return "\n".join(lines) + "\n"


def _patch_readme(existing: str, total: int, num_categories: int, date: str, category_lines: list[str]) -> str:
    """替换 README.md 中的统计头部和分类列表

    保留 README 中分类列表之后的自定义内容（如果有）。

    Args:
        existing: 现有的 README.md 内容
        total: 工具总数
        num_categories: 分类数量
        date: 日期字符串
        category_lines: 各分类的 Markdown 行列表

    Returns:
        str: 更新后的 README.md 内容
    """
    lines = existing.splitlines()
    result: list[str] = []
    i = 0

    # 第一阶段：保留标题行
    while i < len(lines):
        line = lines[i]
        # 找到统计摘要行（以 "> 共" 开头），替换为新的统计数据
        if line.startswith("> 共") or re.search(r"最后更新", line):
            result.append(f"> 共 {total} 个工具，{num_categories} 个分类 | 最后更新: {date}")
            i += 1
            break
        else:
            result.append(line)
            i += 1

    # 跳过旧的空行和分类列表行
    while i < len(lines):
        line = lines[i]
        # 跳过空行和以 "- [" 开头的分类列表行
        if line.strip() == "" or line.startswith("- ["):
            i += 1
        else:
            break

    # 插入新的分类列表
    result.append("")  # 统计行后的空行
    result.extend(category_lines)

    # 保留分类列表之后的自定义内容（如果有）
    if i < len(lines):
        result.append("")
        while i < len(lines):
            result.append(lines[i])
            i += 1

    # 确保文件末尾有换行
    return "\n".join(result) + "\n"


def main() -> int:
    """主函数

    Returns:
        int: 退出码，0 表示成功，1 表示失败
    """
    if not CATALOG_FILE.exists():
        logger.error("目录文件不存在: %s", CATALOG_FILE)
        return 1

    # JSON 解析验证
    try:
        with open(CATALOG_FILE, encoding="utf-8") as f:
            catalog = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("tools.json 格式错误，JSON 解析失败: %s", e)
        return 1

    # Schema 校验
    from validate_schema import validate_catalog

    schema_path = ROOT_DIR / "catalog" / "tools_schema.json"
    is_valid, errors = validate_catalog(CATALOG_FILE, schema_path)
    if not is_valid:
        for err in errors:
            logger.warning("Schema: %s", err)

    tools = catalog.get("tools", [])
    logger.info("加载了 %d 个工具", len(tools))

    # 按分类分组
    categories: defaultdict[str, list[dict]] = defaultdict(list)
    for tool in tools:
        cat = tool.get("category", "other")
        categories[cat].append(tool)

    # 生成每个分类的文档
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cat, cat_tools in categories.items():
        doc = generate_category_doc(cat, cat_tools)
        output_file = OUTPUT_DIR / f"{cat}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(doc)
        logger.info("  %s: %d 个工具 -> %s", CATEGORY_NAMES.get(cat, cat), len(cat_tools), output_file.name)

    # 同步 meta.total_tools 计数
    if sync_meta_count(catalog):
        logger.info("tools.json meta.total_tools 已同步")

    # 更新 catalog/README.md（统计数量和日期）
    update_catalog_readme(catalog)

    logger.info("文档生成完成!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
