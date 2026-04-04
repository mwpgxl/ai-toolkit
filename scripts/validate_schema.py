#!/usr/bin/env python3
"""
JSON Schema 校验脚本
校验 tools.json 是否符合 tools_schema.json 定义的结构

用法:
    python scripts/validate_schema.py
    python scripts/validate_schema.py --catalog path/to/tools.json --schema path/to/schema.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent


def validate_catalog(
    catalog_path: Path,
    schema_path: Path,
) -> tuple[bool, list[str]]:
    """校验工具目录是否符合 JSON Schema

    Args:
        catalog_path: tools.json 文件路径
        schema_path: JSON Schema 文件路径

    Returns:
        tuple[bool, list[str]]: (是否通过校验, 错误信息列表)
            - 通过校验时返回 (True, [])
            - 校验失败时返回 (False, [错误描述, ...])
            - jsonschema 未安装时返回 (True, ["jsonschema 未安装，跳过校验"])
    """
    # 检查 jsonschema 是否可用
    try:
        import jsonschema
    except ImportError:
        logger.warning("jsonschema 未安装，跳过校验。安装命令: pip install jsonschema>=4.17.0")
        return True, ["jsonschema 未安装，跳过校验"]

    # 读取目录文件
    if not catalog_path.exists():
        return False, [f"目录文件不存在: {catalog_path}"]

    try:
        with open(catalog_path, encoding="utf-8") as f:
            catalog_data: dict = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"目录文件 JSON 解析失败: {e}"]

    # 读取 Schema 文件
    if not schema_path.exists():
        return False, [f"Schema 文件不存在: {schema_path}"]

    try:
        with open(schema_path, encoding="utf-8") as f:
            schema_data: dict = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Schema 文件 JSON 解析失败: {e}"]

    # 执行校验
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema_data)

    for error in sorted(validator.iter_errors(catalog_data), key=lambda e: list(e.path)):
        # 构建可读的错误路径
        path_parts = list(error.absolute_path)
        if path_parts:
            path_str = " -> ".join(str(p) for p in path_parts)
        else:
            path_str = "(根对象)"
        errors.append(f"[{path_str}] {error.message}")

    if errors:
        return False, errors

    return True, []


def main() -> int:
    """主函数

    Returns:
        int: 退出码，0 表示校验通过，1 表示校验失败
    """
    parser = argparse.ArgumentParser(description="校验 tools.json 结构")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=ROOT_DIR / "catalog" / "tools.json",
        help="目录文件路径 (默认: catalog/tools.json)",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=ROOT_DIR / "catalog" / "tools_schema.json",
        help="Schema 文件路径 (默认: catalog/tools_schema.json)",
    )
    args = parser.parse_args()

    logger.info("开始校验 tools.json ...")
    logger.info("目录文件: %s", args.catalog)
    logger.info("Schema 文件: %s", args.schema)

    is_valid, errors = validate_catalog(args.catalog, args.schema)

    if is_valid:
        if errors:
            # jsonschema 未安装的情况
            for msg in errors:
                logger.warning(msg)
        else:
            logger.info("校验通过! tools.json 结构符合 Schema 定义。")
        return 0
    else:
        logger.error("校验失败! 发现 %d 个错误:", len(errors))
        for i, err in enumerate(errors, 1):
            logger.error("  %d. %s", i, err)
        return 1


if __name__ == "__main__":
    sys.exit(main())
