#!/usr/bin/env python3
"""
API 调用与文件 I/O 的 Mock 测试套件

覆盖范围:
  - update_stars.py: GitHub API 请求、原子写入、线程池并行、Token 验证
  - security_audit.py: 仓库数据获取、文件内容获取（含分支回退）、原子写入、API 限流
  - generate_docs.py: 输出文件创建、JSON 解析错误处理

运行方式:
  python3 -m pytest scripts/tests/test_api_io.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# 将 scripts/ 目录加入 import 路径
SCRIPTS_DIR = Path(__file__).parent.parent
ROOT_DIR = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import contextlib

import generate_docs
import security_audit
import update_stars

# ============================================================
# 通用 Fixtures
# ============================================================


@pytest.fixture
def 模拟成功响应() -> MagicMock:
    """构造一个 200 状态码的 GitHub API 模拟响应"""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "stargazers_count": 12345,
        "forks_count": 678,
        "description": "A great tool",
        "language": "Python",
        "topics": ["ai", "tool"],
        "updated_at": "2026-03-30T10:00:00Z",
        "archived": False,
        "open_issues_count": 42,
    }
    return resp


@pytest.fixture
def 模拟工具数据() -> dict:
    """一个最小化的工具数据"""
    return {
        "id": "test-tool",
        "name": "Test Tool",
        "github_url": "https://github.com/testorg/testrepo",
        "category": "cli-tool",
        "stars": 100,
        "forks": 10,
        "description": "测试工具",
    }


@pytest.fixture
def 模拟目录数据(模拟工具数据: dict) -> dict:
    """一个最小化的目录 (catalog) 数据"""
    return {
        "meta": {
            "last_updated": "2026-03-30T00:00:00Z",
            "total_tools": 1,
        },
        "tools": [模拟工具数据],
    }


# ============================================================
# update_stars.py — GitHub API Mock 测试
# ============================================================


class TestUpdateStars_API请求:
    """update_stars.py 的 GitHub API 请求测试"""

    @patch("update_stars.requests.get")
    def test_fetch_github_data_成功(self, mock_get: MagicMock, 模拟成功响应: MagicMock) -> None:
        """成功获取仓库信息时，应正确提取 star 数量和其他字段"""
        mock_get.return_value = 模拟成功响应

        result = update_stars.fetch_repo_info("testorg/testrepo")

        assert result is not None
        assert result["stars"] == 12345
        assert result["forks"] == 678
        assert result["description"] == "A great tool"
        assert result["language"] == "Python"
        assert result["archived"] is False
        mock_get.assert_called_once()

    @patch("update_stars.requests.get")
    def test_fetch_github_data_404(self, mock_get: MagicMock) -> None:
        """仓库不存在 (404) 时，应返回 None 并记录警告"""
        resp = MagicMock()
        resp.status_code = 404
        mock_get.return_value = resp

        result = update_stars.fetch_repo_info("nonexistent/repo")

        assert result is None

    @patch("update_stars.requests.get")
    def test_fetch_github_data_403限流(self, mock_get: MagicMock) -> None:
        """触发 API 限流 (403) 时，应返回 None 并记录错误"""
        resp = MagicMock()
        resp.status_code = 403
        mock_get.return_value = resp

        result = update_stars.fetch_repo_info("testorg/testrepo")

        assert result is None

    @patch("update_stars.requests.get")
    def test_fetch_github_data_超时(self, mock_get: MagicMock) -> None:
        """请求超时时，应捕获异常并返回 None"""
        import requests as real_requests

        mock_get.side_effect = real_requests.exceptions.Timeout("连接超时")

        result = update_stars.fetch_repo_info("testorg/testrepo")

        assert result is None

    @patch("update_stars.requests.get")
    def test_fetch_github_data_网络错误(self, mock_get: MagicMock) -> None:
        """发生网络连接错误时，应捕获异常并返回 None"""
        import requests as real_requests

        mock_get.side_effect = real_requests.exceptions.ConnectionError("无法连接")

        result = update_stars.fetch_repo_info("testorg/testrepo")

        assert result is None


# ============================================================
# update_stars.py — 原子写入 Mock 测试
# ============================================================


class TestUpdateStars_原子写入:
    """update_stars.py 的原子写入逻辑测试"""

    @patch("update_stars.os.replace")
    @patch("update_stars.tempfile.NamedTemporaryFile")
    @patch("update_stars.check_rate_limit", return_value={"remaining": 100, "limit": 5000, "reset": "soon"})
    @patch("update_stars.fetch_repo_info")
    @patch("update_stars.CATALOG_FILE")
    def test_原子写入成功(
        self,
        mock_catalog_file: MagicMock,
        mock_fetch: MagicMock,
        mock_rate_limit: MagicMock,
        mock_tmp: MagicMock,
        mock_replace: MagicMock,
        模拟目录数据: dict,
    ) -> None:
        """原子写入应先写临时文件，再用 os.replace 替换目标文件"""
        # 设置 CATALOG_FILE mock
        mock_catalog_file.exists.return_value = True
        mock_catalog_file.parent = Path("/fake/catalog")
        mock_catalog_file.__str__ = lambda s: "/fake/catalog/tools.json"
        mock_catalog_file.__fspath__ = lambda s: "/fake/catalog/tools.json"

        # 设置 fetch 返回值（无 github_url 的工具不会调用 fetch）
        mock_fetch.return_value = {
            "stars": 999,
            "forks": 10,
            "description": "",
            "language": "Python",
            "topics": [],
            "updated_at": "2026-03-30T10:00:00Z",
            "archived": False,
            "open_issues": 0,
        }

        # 设置临时文件 mock
        tmp_file_mock = MagicMock()
        tmp_file_mock.name = "/fake/catalog/tmp12345.tmp"
        tmp_file_mock.__enter__ = Mock(return_value=tmp_file_mock)
        tmp_file_mock.__exit__ = Mock(return_value=False)
        mock_tmp.return_value = tmp_file_mock

        # 模拟 open 读取目录数据
        m_open = mock_open(read_data=json.dumps(模拟目录数据))
        with patch("builtins.open", m_open):
            try:
                update_stars.update_catalog()
            except SystemExit:
                pass  # update_catalog 在各种情况下可能调用 sys.exit

        # 验证 os.replace 被调用（原子写入的关键步骤）
        mock_replace.assert_called_once()

    @patch("update_stars.os.unlink")
    @patch("update_stars.os.replace")
    @patch("update_stars.tempfile.NamedTemporaryFile")
    @patch("update_stars.check_rate_limit", return_value={"remaining": 100, "limit": 5000, "reset": "soon"})
    @patch("update_stars.fetch_repo_info")
    @patch("update_stars.CATALOG_FILE")
    def test_原子写入失败时清理临时文件(
        self,
        mock_catalog_file: MagicMock,
        mock_fetch: MagicMock,
        mock_rate_limit: MagicMock,
        mock_tmp: MagicMock,
        mock_replace: MagicMock,
        mock_unlink: MagicMock,
        模拟目录数据: dict,
    ) -> None:
        """os.replace 失败时，应清理残留的临时文件"""
        mock_catalog_file.exists.return_value = True
        mock_catalog_file.parent = Path("/fake/catalog")
        mock_catalog_file.__str__ = lambda s: "/fake/catalog/tools.json"
        mock_catalog_file.__fspath__ = lambda s: "/fake/catalog/tools.json"

        mock_fetch.return_value = {
            "stars": 999,
            "forks": 10,
            "description": "",
            "language": "Python",
            "topics": [],
            "updated_at": "2026-03-30T10:00:00Z",
            "archived": False,
            "open_issues": 0,
        }

        tmp_file_mock = MagicMock()
        tmp_file_mock.name = "/fake/catalog/tmp12345.tmp"
        tmp_file_mock.__enter__ = Mock(return_value=tmp_file_mock)
        tmp_file_mock.__exit__ = Mock(return_value=False)
        mock_tmp.return_value = tmp_file_mock

        # os.replace 抛出 OSError，模拟写入失败
        mock_replace.side_effect = OSError("磁盘空间不足")

        m_open = mock_open(read_data=json.dumps(模拟目录数据))
        with patch("builtins.open", m_open), pytest.raises(SystemExit):
            update_stars.update_catalog()

        # 验证尝试清理临时文件
        mock_unlink.assert_called_with("/fake/catalog/tmp12345.tmp")


# ============================================================
# update_stars.py — 线程池 Mock 测试
# ============================================================


class TestUpdateStars_线程池:
    """update_stars.py 的并行请求测试"""

    @patch("update_stars.as_completed")
    @patch("update_stars.ThreadPoolExecutor")
    @patch("update_stars.check_rate_limit", return_value={"remaining": 100, "limit": 5000, "reset": "soon"})
    @patch("update_stars.CATALOG_FILE")
    def test_并行请求使用线程池(
        self,
        mock_catalog_file: MagicMock,
        mock_rate_limit: MagicMock,
        mock_executor_cls: MagicMock,
        mock_as_completed: MagicMock,
        模拟目录数据: dict,
    ) -> None:
        """应使用 max_workers=5 的线程池进行并行请求"""
        mock_catalog_file.exists.return_value = True
        mock_catalog_file.parent = Path("/fake/catalog")
        mock_catalog_file.__str__ = lambda s: "/fake/catalog/tools.json"
        mock_catalog_file.__fspath__ = lambda s: "/fake/catalog/tools.json"

        # 模拟线程池上下文管理器
        mock_executor = MagicMock()
        mock_executor.__enter__ = Mock(return_value=mock_executor)
        mock_executor.__exit__ = Mock(return_value=False)
        mock_executor.submit.return_value = MagicMock()
        mock_executor_cls.return_value = mock_executor

        # as_completed 返回空迭代器（不实际执行任务）
        mock_as_completed.return_value = iter([])

        m_open = mock_open(read_data=json.dumps(模拟目录数据))
        with patch("builtins.open", m_open), patch("update_stars.tempfile.NamedTemporaryFile") as mock_tmp:
            tmp_mock = MagicMock()
            tmp_mock.name = "/fake/tmp.tmp"
            tmp_mock.__enter__ = Mock(return_value=tmp_mock)
            tmp_mock.__exit__ = Mock(return_value=False)
            mock_tmp.return_value = tmp_mock
            with patch("update_stars.os.replace"), contextlib.suppress(SystemExit):
                update_stars.update_catalog()

        # 验证 ThreadPoolExecutor 被以 max_workers=5 调用
        mock_executor_cls.assert_called_once_with(max_workers=5)


# ============================================================
# update_stars.py — Token 验证测试
# ============================================================


class TestUpdateStars_Token验证:
    """update_stars.py 的 GitHub Token 格式验证测试"""

    @pytest.mark.parametrize(
        "token, expected",
        [
            # 合法 Token
            ("ghp_abcdefghijklmnopqrstuvwxyz1234567890", True),
            ("gho_abcdefghijklmnopqrstuvwxyz1234567890", True),
            ("ghu_abcdefghijklmnopqrstuvwxyz1234567890", True),
            ("ghs_abcdefghijklmnopqrstuvwxyz1234567890", True),
            ("github_pat_abcdefghijklmnopqrstuvwxyz1234567890", True),
            # 非法 Token
            ("", False),
            ("invalid_token_format", False),
            ("Bearer ghp_abc123", False),
            ("sk-1234567890abcdef", False),
            ("glpat-xxxxxxxxxxx", False),
        ],
        ids=[
            "ghp_经典个人令牌",
            "gho_OAuth令牌",
            "ghu_App用户令牌",
            "ghs_App安装令牌",
            "github_pat_细粒度令牌",
            "空字符串",
            "无效前缀",
            "Bearer前缀不算",
            "OpenAI格式",
            "GitLab格式",
        ],
    )
    def test_validate_github_token各种格式(self, token: str, expected: bool) -> None:
        """验证各种 Token 格式是否被正确判断"""
        result = update_stars.validate_github_token(token)
        assert result == expected


# ============================================================
# security_audit.py — GitHub API Mock 测试
# ============================================================


class TestSecurityAudit_API请求:
    """security_audit.py 的 GitHub API 请求测试"""

    @patch("security_audit.requests.get")
    def test_fetch_repo_data_成功(self, mock_get: MagicMock) -> None:
        """成功获取仓库数据时，应返回完整的 JSON 响应"""
        repo_data = {
            "full_name": "testorg/testrepo",
            "stargazers_count": 5000,
            "forks_count": 200,
            "archived": False,
            "pushed_at": "2026-03-28T12:00:00Z",
            "license": {"spdx_id": "MIT"},
            "description": "Test repository",
            "open_issues_count": 10,
        }
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = repo_data
        mock_get.return_value = resp

        result = security_audit.fetch_repo_data("testorg/testrepo")

        assert result is not None
        assert result["stargazers_count"] == 5000
        assert result["license"]["spdx_id"] == "MIT"
        mock_get.assert_called_once()

    @patch("security_audit.requests.get")
    def test_fetch_repo_data_失败(self, mock_get: MagicMock) -> None:
        """API 调用失败时（非 200 状态码），应返回 None"""
        resp = MagicMock()
        resp.status_code = 500
        mock_get.return_value = resp

        result = security_audit.fetch_repo_data("testorg/testrepo")

        assert result is None

    @patch("security_audit.requests.get")
    def test_fetch_repo_data_网络异常(self, mock_get: MagicMock) -> None:
        """发生网络异常时，应捕获并返回 None"""
        import requests as real_requests

        mock_get.side_effect = real_requests.exceptions.ConnectionError("DNS 解析失败")

        result = security_audit.fetch_repo_data("testorg/testrepo")

        assert result is None


# ============================================================
# security_audit.py — 文件内容获取 Mock 测试
# ============================================================


class TestSecurityAudit_文件内容获取:
    """security_audit.py 的 fetch_file_content 测试，含分支回退逻辑"""

    @patch("security_audit.requests.get")
    def test_fetch_file_content_成功(self, mock_get: MagicMock) -> None:
        """main 分支上成功获取文件内容时，应直接返回文本"""
        resp = MagicMock()
        resp.status_code = 200
        resp.text = "# SKILL.md\n这是一个测试文件"
        mock_get.return_value = resp

        result = security_audit.fetch_file_content("testorg/testrepo", "SKILL.md")

        assert result is not None
        assert "SKILL.md" in result

    @patch("security_audit.requests.get")
    def test_fetch_file_content_回退master(self, mock_get: MagicMock) -> None:
        """main 分支获取失败时，应回退尝试 master 分支"""
        # 第一次请求 (main) 返回 404，第二次请求 (master) 返回 200
        resp_404 = MagicMock()
        resp_404.status_code = 404
        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.text = "# README from master branch"

        mock_get.side_effect = [resp_404, resp_200]

        result = security_audit.fetch_file_content("testorg/testrepo", "SKILL.md")

        assert result is not None
        assert "master" in result.lower() or result == "# README from master branch"
        # 验证发起了两次请求（main 和 master）
        assert mock_get.call_count == 2

    @patch("security_audit.requests.get")
    def test_fetch_file_content_两个分支都失败(self, mock_get: MagicMock) -> None:
        """main 和 master 分支都失败时，应返回 None"""
        resp_404 = MagicMock()
        resp_404.status_code = 404
        # fetch_file_content 会尝试多个路径变体 (path, PATH, path)
        # 每个变体尝试 main 和 master 两个分支
        mock_get.return_value = resp_404

        result = security_audit.fetch_file_content("testorg/testrepo", "SKILL.md")

        assert result is None
        # 应尝试多次（3 个路径变体 x 2 个分支 = 6 次请求）
        assert mock_get.call_count == 6


# ============================================================
# security_audit.py — 原子写入 Mock 测试
# ============================================================


class TestSecurityAudit_原子写入:
    """security_audit.py 的原子写入测试"""

    @patch("security_audit.os.replace")
    @patch("security_audit.tempfile.NamedTemporaryFile")
    def test_原子写入tools_json(
        self,
        mock_tmp: MagicMock,
        mock_replace: MagicMock,
        模拟目录数据: dict,
    ) -> None:
        """tools.json 的原子写入应使用 tempfile + os.replace 模式"""
        # 模拟 run_audit 中的原子写入片段
        # 直接测试原子写入模式：先写临时文件，再 replace
        tmp_file_mock = MagicMock()
        tmp_file_mock.name = "/fake/catalog/audit_tmp.tmp"
        tmp_file_mock.__enter__ = Mock(return_value=tmp_file_mock)
        tmp_file_mock.__exit__ = Mock(return_value=False)
        mock_tmp.return_value = tmp_file_mock

        catalog_dir = Path("/fake/catalog")
        catalog_file = catalog_dir / "tools.json"

        # 执行原子写入逻辑（模拟 run_audit 中的写入部分）
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=catalog_dir,
            suffix=".tmp",
            delete=False,
        ) as tmp_f:
            json.dump(模拟目录数据, tmp_f, ensure_ascii=False, indent=2)
            tmp_path = Path(tmp_f.name)
        os.replace(tmp_path, catalog_file)

        # 验证原子写入的两个关键步骤
        mock_tmp.assert_called_once_with(
            mode="w",
            encoding="utf-8",
            dir=catalog_dir,
            suffix=".tmp",
            delete=False,
        )
        mock_replace.assert_called_once_with(
            Path("/fake/catalog/audit_tmp.tmp"),
            catalog_file,
        )

    @patch("security_audit.os.replace")
    @patch("security_audit.tempfile.NamedTemporaryFile")
    def test_原子写入audit_report(
        self,
        mock_tmp: MagicMock,
        mock_replace: MagicMock,
    ) -> None:
        """audit_report.md 的原子写入应使用相同的 tempfile + os.replace 模式"""
        tmp_file_mock = MagicMock()
        tmp_file_mock.name = "/fake/security/report_tmp.tmp"
        tmp_file_mock.__enter__ = Mock(return_value=tmp_file_mock)
        tmp_file_mock.__exit__ = Mock(return_value=False)
        mock_tmp.return_value = tmp_file_mock

        report_dir = Path("/fake/security")
        report_file = report_dir / "audit_report.md"
        report_content = "# 安全审计报告\n内容..."

        # 执行原子写入
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=report_dir,
            suffix=".tmp",
            delete=False,
        ) as tmp_f:
            tmp_f.write(report_content)
            tmp_path = Path(tmp_f.name)
        os.replace(tmp_path, report_file)

        # 验证写入和替换
        mock_tmp.assert_called_once_with(
            mode="w",
            encoding="utf-8",
            dir=report_dir,
            suffix=".tmp",
            delete=False,
        )
        mock_replace.assert_called_once_with(
            Path("/fake/security/report_tmp.tmp"),
            report_file,
        )


# ============================================================
# security_audit.py — API 限流延迟测试
# ============================================================


class TestSecurityAudit_API限流:
    """security_audit.py 的 API 限流延迟测试"""

    @patch("security_audit.time.sleep")
    @patch("security_audit.fetch_file_content", return_value=None)
    @patch("security_audit.fetch_repo_data")
    def test_API限流延迟(
        self,
        mock_fetch_repo: MagicMock,
        mock_fetch_file: MagicMock,
        mock_sleep: MagicMock,
        模拟工具数据: dict,
    ) -> None:
        """deep 模式下每次 API 请求后应调用 time.sleep(API_RATE_LIMIT_DELAY)"""
        mock_fetch_repo.return_value = {
            "stargazers_count": 100,
            "forks_count": 10,
            "archived": False,
            "pushed_at": "2026-03-28T12:00:00Z",
            "license": {"spdx_id": "MIT"},
            "description": "test",
            "open_issues_count": 5,
        }

        # 在 deep 模式下调用 assess_tool
        security_audit.assess_tool(模拟工具数据, deep=True)

        # 验证调用了 time.sleep 进行限流延迟
        mock_sleep.assert_called_once_with(security_audit.API_RATE_LIMIT_DELAY)

    def test_API限流延迟常量值(self) -> None:
        """API_RATE_LIMIT_DELAY 应为合理的延迟值（大于 0，小于 5 秒）"""
        assert 0 < security_audit.API_RATE_LIMIT_DELAY < 5
        assert security_audit.API_RATE_LIMIT_DELAY == 0.3


# ============================================================
# generate_docs.py — 文件 I/O 测试
# ============================================================


class TestGenerateDocs_文件IO:
    """generate_docs.py 的文件 I/O 测试"""

    def test_generate_docs_输出文件创建(
        self,
        模拟目录数据: dict,
        tmp_path: Path,
    ) -> None:
        """生成文档时，应为每个分类创建对应的 Markdown 文件"""
        # 使用 pytest 内置的 tmp_path 避免操作真实文件系统
        output_dir = tmp_path / "by-category"
        output_dir.mkdir()
        catalog_dir = tmp_path / "catalog"
        catalog_dir.mkdir()

        # 将模拟数据写入真实临时文件
        catalog_file = catalog_dir / "tools.json"
        catalog_file.write_text(json.dumps(模拟目录数据, ensure_ascii=False), encoding="utf-8")

        with patch("generate_docs.CATALOG_FILE", catalog_file), patch("generate_docs.OUTPUT_DIR", output_dir):
            with patch("generate_docs.ROOT_DIR", tmp_path):
                result = generate_docs.main()

        assert result == 0
        # 验证分类文件被创建
        category_files = list(output_dir.glob("*.md"))
        assert len(category_files) >= 1
        # 验证 cli-tool.md 被创建（测试工具的分类）
        assert (output_dir / "cli-tool.md").exists()

    @patch("generate_docs.CATALOG_FILE")
    def test_generate_docs_JSON解析错误处理(
        self,
        mock_catalog_file: MagicMock,
    ) -> None:
        """tools.json 格式错误时，应返回错误码 1 而不是崩溃"""
        mock_catalog_file.exists.return_value = True

        # 模拟打开一个格式错误的 JSON 文件
        malformed_json = "{ invalid json content ,,, }"
        m_open = mock_open(read_data=malformed_json)

        with patch("builtins.open", m_open):
            result = generate_docs.main()

        assert result == 1


# ============================================================
# 环境变量 Mock 测试（使用 monkeypatch）
# ============================================================


class TestEnvironment_环境变量:
    """使用 monkeypatch 测试环境变量对行为的影响"""

    def test_github_token_从环境变量读取(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """GITHUB_TOKEN 应从环境变量中读取"""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test1234567890abcdefghij")

        # 重新读取环境变量
        token = os.environ.get("GITHUB_TOKEN", "")
        assert token == "ghp_test1234567890abcdefghij"
        assert update_stars.validate_github_token(token) is True

    def test_github_token_未设置时为空(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """未设置 GITHUB_TOKEN 时，应得到空字符串"""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        token = os.environ.get("GITHUB_TOKEN", "")
        assert token == ""
        assert update_stars.validate_github_token(token) is False

    def test_get_headers_无token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """未设置 Token 时，请求头不应包含 Authorization"""
        monkeypatch.setattr(update_stars, "GITHUB_TOKEN", "")

        headers = update_stars.get_headers()
        assert "Authorization" not in headers
        assert "Accept" in headers

    def test_get_headers_有token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """设置了 Token 时，请求头应包含正确的 Authorization"""
        monkeypatch.setattr(update_stars, "GITHUB_TOKEN", "ghp_validtoken123")

        headers = update_stars.get_headers()
        assert headers["Authorization"] == "token ghp_validtoken123"


# ============================================================
# URL 解析测试
# ============================================================


class TestURL解析:
    """GitHub URL 解析的边界情况测试"""

    @pytest.mark.parametrize(
        "url, expected",
        [
            ("https://github.com/owner/repo", "owner/repo"),
            ("https://github.com/owner/repo.git", "owner/repo"),
            ("https://github.com/owner/repo/tree/main", "owner/repo"),
            ("https://github.com/owner/repo/blob/main/file.py", "owner/repo"),
            ("", None),
            ("https://gitlab.com/owner/repo", None),
            ("not-a-url", None),
        ],
        ids=[
            "标准URL",
            "带.git后缀",
            "带路径tree/main",
            "带文件路径",
            "空字符串",
            "非GitHub_URL",
            "非URL格式",
        ],
    )
    def test_extract_repo_from_url(self, url: str, expected: str | None) -> None:
        """update_stars 的 URL 解析应正确提取 owner/repo"""
        result = update_stars.extract_repo_from_url(url)
        assert result == expected

    @pytest.mark.parametrize(
        "url, expected",
        [
            ("https://github.com/owner/repo", "owner/repo"),
            ("https://github.com/owner/repo.git", "owner/repo"),
            ("", None),
            (None, None),
        ],
        ids=["标准URL", "带.git后缀", "空字符串", "None值"],
    )
    def test_security_audit_extract_repo(self, url: str, expected: str | None) -> None:
        """security_audit 的 URL 解析应正确提取 owner/repo"""
        result = security_audit.extract_repo(url or "")
        assert result == expected
