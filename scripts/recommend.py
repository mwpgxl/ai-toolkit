#!/usr/bin/env python3
"""
项目工具推荐引擎
根据项目类型和需求，自动推荐适合的 Skills、MCP Servers 和 AI Agent 工具
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent
CATALOG_FILE = ROOT_DIR / "catalog" / "tools.json"

# 项目类型与标签的映射关系
PROJECT_PROFILES = {
    "web-frontend": {
        "name": "Web 前端项目",
        "tags": ["frontend", "ui", "design", "css", "react", "vue", "browser"],
        "categories": ["skill", "browser-tool", "dev-tool"],
    },
    "web-backend": {
        "name": "Web 后端项目",
        "tags": ["backend", "api", "database", "server", "deploy"],
        "categories": ["mcp-server", "dev-tool", "cli-tool"],
    },
    "data-science": {
        "name": "数据科学项目",
        "tags": ["data", "analysis", "visualization", "python", "notebook"],
        "categories": ["ai-agent", "dev-tool", "productivity"],
    },
    "finance": {
        "name": "金融投资项目",
        "tags": ["finance", "trading", "stock", "crypto", "quant", "investment"],
        "categories": ["finance", "ai-agent"],
    },
    "automation": {
        "name": "自动化项目",
        "tags": ["automation", "scraping", "workflow", "browser", "cli"],
        "categories": ["mcp-server", "browser-tool", "cli-tool", "ai-agent"],
    },
    "content": {
        "name": "内容创作项目",
        "tags": ["content", "writing", "video", "audio", "media", "marketing"],
        "categories": ["ai-agent", "productivity", "voice-tool"],
    },
    "fullstack": {
        "name": "全栈项目",
        "tags": ["frontend", "backend", "database", "deploy", "browser", "api"],
        "categories": ["skill", "mcp-server", "browser-tool", "dev-tool", "cli-tool"],
    },
    "general": {
        "name": "通用项目",
        "tags": [],
        "categories": ["skill", "mcp-server", "cli-tool", "productivity"],
    },
}

# 所有项目都推荐的基础工具标签
BASE_TAGS = ["essential", "productivity", "search", "code-quality"]


def load_catalog() -> dict:
    """加载工具目录

    Returns:
        dict: 解析后的工具目录数据

    Raises:
        SystemExit: 文件不存在或 JSON 解析失败时退出
    """
    if not CATALOG_FILE.exists():
        logger.error("目录文件不存在: %s", CATALOG_FILE)
        sys.exit(1)

    # JSON 解析验证
    try:
        with open(CATALOG_FILE, encoding="utf-8") as f:
            catalog: dict = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("tools.json 格式错误，JSON 解析失败: %s", e)
        sys.exit(1)

    # Schema 校验
    from validate_schema import validate_catalog

    schema_path = ROOT_DIR / "catalog" / "tools_schema.json"
    is_valid, errors = validate_catalog(CATALOG_FILE, schema_path)
    if not is_valid:
        for err in errors:
            logger.warning("Schema: %s", err)

    return catalog


def score_tool(tool: dict, profile: dict) -> float:
    """计算工具与项目的匹配度得分"""
    score = 0.0
    tool_tags = set(tool.get("tags", []))
    profile_tags = set(profile.get("tags", []))
    base_tags = set(BASE_TAGS)

    # 标签匹配得分 (最高 40 分)
    tag_overlap = tool_tags & profile_tags
    score += len(tag_overlap) * 10
    base_overlap = tool_tags & base_tags
    score += len(base_overlap) * 5

    # 分类匹配得分 (20 分)
    if tool.get("category") in profile.get("categories", []):
        score += 20

    # Star 数加权 (最高 20 分)
    stars = tool.get("stars", 0)
    if stars >= 10000:
        score += 20
    elif stars >= 5000:
        score += 15
    elif stars >= 1000:
        score += 10
    elif stars >= 100:
        score += 5

    # 推荐优先级加权 (最高 20 分)
    priority = tool.get("priority", "normal")
    if priority == "essential":
        score += 20
    elif priority == "recommended":
        score += 10

    return score


def recommend(
    project_type: str,
    top_n: int = 20,
    min_score: float = 10.0,
    custom_tags: list[str] | None = None,
) -> list[tuple[dict, float]]:
    """根据项目类型推荐工具

    Args:
        project_type: 项目类型标识
        top_n: 返回的最大推荐数量
        min_score: 最低匹配得分阈值
        custom_tags: 用户自定义的额外标签

    Returns:
        list[tuple[dict, float]]: 推荐工具列表，每项为 (工具字典, 匹配得分)
    """
    catalog = load_catalog()
    tools: list[dict] = catalog.get("tools", [])

    # 构建工具名称集合，用于验证工具是否存在于目录中
    tool_names: set[str] = {t["name"] for t in tools if "name" in t}

    profile = PROJECT_PROFILES.get(project_type, PROJECT_PROFILES["general"])
    if custom_tags:
        profile = {**profile, "tags": profile["tags"] + custom_tags}

    # 计算得分并排序
    scored: list[tuple[dict, float]] = []
    for tool in tools:
        # 验证工具存在于目录中（具有有效名称）
        if "name" not in tool or tool["name"] not in tool_names:
            logger.warning("跳过无效工具条目（缺少 name 字段）")
            continue
        s = score_tool(tool, profile)
        if s >= min_score:
            scored.append((tool, s))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


def print_recommendations(project_type: str, results: list[tuple[dict, float]]) -> None:
    """打印推荐结果

    Args:
        project_type: 项目类型标识
        results: 推荐结果列表，每项为 (工具字典, 匹配得分)
    """
    profile = PROJECT_PROFILES.get(project_type, PROJECT_PROFILES["general"])
    print(f"\n项目类型: {profile['name']}")
    print(f"推荐工具 (共 {len(results)} 个):\n")

    for i, (tool, score) in enumerate(results, 1):
        stars = tool.get("stars", 0)
        stars_str = f"⭐{stars}" if stars > 0 else ""
        category = tool.get("category", "")
        name = tool["name"]
        desc = tool.get("description", "")

        print(f"  {i:2d}. [{category:12s}] {name:30s} {stars_str:>10s}  (匹配度: {score:.0f})")
        if desc:
            print(f"      {desc[:80]}")
        if tool.get("install_cmd"):
            print(f"      安装: {tool['install_cmd']}")
        print()


def generate_setup_script(results: list[tuple[dict, float]], output_file: str | None = None) -> None:
    """生成项目初始化安装脚本

    Args:
        results: 推荐结果列表，每项为 (工具字典, 匹配得分)
        output_file: 输出文件路径，为 None 时打印到标准输出
    """
    lines = [
        "#!/bin/bash",
        "# 自动生成的项目工具安装脚本",
        "# 生成时间: $(date)",
        "",
        "echo '🚀 开始安装推荐工具...'",
        "",
    ]

    for tool, _ in results:
        if tool.get("install_cmd"):
            lines.append(f"# {tool['name']} - {tool.get('description', '')}")
            lines.append(f"{tool['install_cmd']}")
            lines.append("")

    lines.append("echo '✅ 安装完成!'")

    script = "\n".join(lines)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(script)
        logger.info("安装脚本已生成: %s", output_file)
    else:
        logger.info("安装脚本:")
        print(script)


def main() -> int:
    """主函数

    Returns:
        int: 退出码，0 表示成功，1 表示失败
    """
    parser = argparse.ArgumentParser(description="AI 工具推荐引擎")
    parser.add_argument(
        "--type",
        choices=list(PROJECT_PROFILES.keys()),
        default="general",
        help="项目类型",
    )
    parser.add_argument("--top", type=int, default=20, help="推荐数量 (默认 20)")
    parser.add_argument("--tags", nargs="+", help="自定义标签过滤")
    parser.add_argument("--script", type=str, help="生成安装脚本到指定文件")
    parser.add_argument("--list-types", action="store_true", help="列出所有项目类型")

    args = parser.parse_args()

    if args.list_types:
        print("\n支持的项目类型:\n")
        for key, profile in PROJECT_PROFILES.items():
            print(f"  {key:20s} -- {profile['name']}")
            print(f"  {'':20s}   标签: {', '.join(profile['tags'][:5])}")
        return 0

    results = recommend(args.type, top_n=args.top, custom_tags=args.tags)

    if not results:
        logger.warning("未找到匹配的推荐工具")

    print_recommendations(args.type, results)

    if args.script:
        generate_setup_script(results, args.script)

    return 0


if __name__ == "__main__":
    sys.exit(main())
