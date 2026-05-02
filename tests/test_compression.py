\
"""Unit tests for hermes_rtkit compression functions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes_rtkit.plugin import (
    compress_output,
    get_rtk_filter,
    is_supported_command,
)


class TestGetRtkFilter:
    """Tests for get_rtk_filter()."""

    def test_cargo_test_returns_cargo_test_filter(self):
        assert get_rtk_filter("cargo test") == "cargo-test"

    def test_cargo_build_returns_cargo_build_filter(self):
        assert get_rtk_filter("cargo build") == "cargo-build"

    def test_pytest_returns_pytest_filter(self):
        assert get_rtk_filter("pytest") == "pytest"

    def test_pytest_with_path_returns_pytest(self):
        assert get_rtk_filter("pytest tests/") == "pytest"

    def test_git_diff_returns_git_diff_filter(self):
        assert get_rtk_filter("git diff") == "git-diff"

    def test_git_status_returns_git_log_filter(self):
        assert get_rtk_filter("git status") == "git-log"

    def test_git_log_returns_git_log_filter(self):
        assert get_rtk_filter("git log --oneline") == "git-log"

    def test_npm_test_returns_npm_filter(self):
        assert get_rtk_filter("npm test") == "npm"

    def test_docker_ps_returns_docker_filter(self):
        assert get_rtk_filter("docker ps") == "docker"

    def test_kubectl_get_returns_kubectl_filter(self):
        assert get_rtk_filter("kubectl get pods") == "kubectl"

    def test_ruff_check_returns_ruff_filter(self):
        assert get_rtk_filter("ruff check .") == "ruff"

    def test_ruff_format_returns_ruff_filter(self):
        assert get_rtk_filter("ruff format .") == "ruff"

    def test_empty_command_returns_none(self):
        assert get_rtk_filter("") is None

    def test_unsupported_command_returns_none(self):
        assert get_rtk_filter("random-cmd") is None
        assert get_rtk_filter("emacs") is None
        assert get_rtk_filter("vim") is None

    def test_command_with_flags_uses_base_command(self):
        """Flags after subcommand should not break filter detection."""
        assert get_rtk_filter("cargo test --lib -- --nocapture") == "cargo-test"

    def test_git_with_unknown_subcommand_falls_back_to_git_log(self):
        assert get_rtk_filter("git foo") == "git-log"


class TestIsSupportedCommand:
    """Tests for is_supported_command()."""

    @pytest.mark.parametrize(
        "cmd",
        [
            "cargo test",
            "cargo build",
            "pytest",
            "pytest tests/",
            "git diff",
            "git status",
            "npm test",
            "pnpm run build",
            "docker ps",
            "kubectl get pods",
            "ruff check .",
            "mypy src/",
        ],
    )
    def test_supported_commands_return_true(self, cmd):
        assert is_supported_command(cmd) is True

    @pytest.mark.parametrize("cmd", ["random", "emacs", "vim", "top", "htop"])
    def test_unsupported_commands_return_false(self, cmd):
        assert is_supported_command(cmd) is False

    def test_empty_string_returns_false(self):
        assert is_supported_command("") is False


class TestCompressOutput:
    """Tests for compress_output()."""

    def test_disabled_returns_original_output(self):
        result = compress_output("cargo test", "raw output", enabled=False)
        assert result == "raw output"

    def test_excluded_command_returns_original_output(self):
        result = compress_output(
            "cargo test",
            "raw output",
            exclude_commands=["cargo"],
        )
        assert result == "raw output"

    def test_unsupported_command_returns_original_output(self):
        result = compress_output("random cmd", "raw output")
        assert result == "raw output"

    def test_empty_output_returns_empty(self):
        result = compress_output("cargo test", "")
        assert result == ""

    def test_whitespace_only_output_returns_original(self):
        result = compress_output("cargo test", "   \n\t  ")
        assert result == "   \n\t  "

    def test_rtk_not_found_returns_original_output(self):
        with patch("shutil.which", return_value=None):
            result = compress_output("cargo test", "raw output")
        assert result == "raw output"

    def test_rtk_successful_compression(self):
        """RTK returns compressed output on success."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "cargo test: 5 passed (0.01s)"

        with patch("subprocess.run", return_value=mock_result):
            with patch("shutil.which", return_value="/usr/local/bin/rtk"):
                result = compress_output(
                    "cargo test",
                    "raw cargo test output with lots of verbose text\n" * 50,
                )
        assert result == "cargo test: 5 passed (0.01s)"

    def test_rtk_failure_returns_original_output(self):
        """RTK non-zero return code -> original output."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            with patch("shutil.which", return_value="/usr/local/bin/rtk"):
                result = compress_output("cargo test", "raw output")
        assert result == "raw output"

    def test_rtk_timeout_returns_original_output(self):
        """RTK timeout -> original output."""
        import subprocess
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 2.0)):
            with patch("shutil.which", return_value="/usr/local/bin/rtk"):
                result = compress_output("cargo test", "raw output")
        assert result == "raw output"

    def test_rtk_empty_stdout_returns_original_output(self):
        """RTK returns empty stdout -> original output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            with patch("shutil.which", return_value="/usr/local/bin/rtk"):
                result = compress_output("cargo test", "raw output")
        assert result == "raw output"

    def test_correct_filter_passed_to_rtk_pipe(self):
        """Verify the right -f filter flag is passed to rtk pipe."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "compressed"

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with patch("shutil.which", return_value="/usr/local/bin/rtk"):
                compress_output("pytest tests/", "raw output")

        call_args = mock_run.call_args
        rtk_args = call_args[0][0]
        assert rtk_args == ["rtk", "pipe", "-f", "pytest"]
        assert call_args[1]["input"] == "raw output"
