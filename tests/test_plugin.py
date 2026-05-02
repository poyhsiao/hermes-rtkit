\
"""Unit tests for hermes_rtkit.plugin module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes_rtkit.plugin import register


class TestPluginRegistration:
    """Tests for register() function."""

    def test_register_hooks_transform_terminal_output(self, mock_plugin_context):
        """register() should call ctx.register_hook with correct hook name."""
        register(mock_plugin_context)
        mock_plugin_context.register_hook.assert_called_once()
        call_args = mock_plugin_context.register_hook.call_args
        assert call_args[0][0] == "transform_terminal_output"

    def test_hook_function_is_registered(self, mock_plugin_context):
        """The registered hook should be a callable."""
        register(mock_plugin_context)
        hook_func = mock_plugin_context.register_hook.call_args[0][1]
        assert callable(hook_func)

    def test_enabled_passes_through_to_compress_output(self, mock_plugin_context):
        """enabled=True config should be passed to compress_output."""
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            mock_compress.return_value = "compressed"
            register(mock_plugin_context)
            hook_func = mock_plugin_context.register_hook.call_args[0][1]

            hook_func(
                command="cargo test",
                output="raw output",
                returncode=0,
                task_id="test-task",
                env_type="local",
            )

            mock_compress.assert_called_once()
            assert mock_compress.call_args[1]["enabled"] is True

    def test_disabled_skips_compression(self, mock_plugin_context_disabled):
        """enabled=False should skip compression entirely."""
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            register(mock_plugin_context_disabled)
            hook_func = mock_plugin_context_disabled.register_hook.call_args[0][1]

            result = hook_func(
                command="cargo test",
                output="raw output",
                returncode=0,
                task_id="test-task",
                env_type="local",
            )

            mock_compress.assert_not_called()
            assert result == "raw output"

    def test_exclude_commands_passed_to_compress_output(self, mock_plugin_context_excluded):
        """exclude_commands from config should be passed through."""
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            mock_compress.return_value = "original"
            register(mock_plugin_context_excluded)
            hook_func = mock_plugin_context_excluded.register_hook.call_args[0][1]

            hook_func(
                command="git status",
                output="raw output",
                returncode=0,
                task_id="test-task",
                env_type="local",
            )

            mock_compress.assert_called_once()
            assert mock_compress.call_args[1]["exclude_commands"] == ["git", "cargo"]

    def test_rtk_path_passed_to_compress_output(self, mock_plugin_context):
        """rtk_path from config should be passed through."""
        mock_plugin_context.config["rtk_path"] = "/custom/bin/rtk"
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            mock_compress.return_value = "compressed"
            register(mock_plugin_context)
            hook_func = mock_plugin_context.register_hook.call_args[0][1]

            hook_func(
                command="cargo test",
                output="raw output",
                returncode=0,
                task_id="test-task",
                env_type="local",
            )

            assert mock_compress.call_args[1]["rtk_path"] == "/custom/bin/rtk"

    def test_verbose_logs_compression_event(self, mock_plugin_context_verbose):
        """verbose=True should print compression stats."""
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            mock_compress.return_value = "comp"  # shorter than original
            with patch("builtins.print") as mock_print:
                register(mock_plugin_context_verbose)
                hook_func = mock_plugin_context_verbose.register_hook.call_args[0][1]

                result = hook_func(
                    command="cargo test",
                    output="raw cargo output",
                    returncode=0,
                    task_id="test-task",
                    env_type="local",
                )

                assert mock_print.called
                assert "[hermes-rtkit]" in mock_print.call_args[0][0]

    def test_no_log_when_output_unchanged(self, mock_plugin_context_verbose):
        """No verbose log when RTK returns same output."""
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            mock_compress.return_value = "raw cargo output"  # unchanged
            with patch("builtins.print") as mock_print:
                register(mock_plugin_context_verbose)
                hook_func = mock_plugin_context_verbose.register_hook.call_args[0][1]

                hook_func(
                    command="cargo test",
                    output="raw cargo output",
                    returncode=0,
                    task_id="test-task",
                    env_type="local",
                )

                mock_print.assert_not_called()

    def test_empty_config_uses_defaults(self):
        """Empty config should use default values."""
        ctx = MagicMock()
        ctx.config = {}
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            mock_compress.return_value = "result"
            register(ctx)
            hook_func = ctx.register_hook.call_args[0][1]
            hook_func("cargo test", "raw", 0, "t", "local")
            assert mock_compress.call_args[1]["enabled"] is True
            assert mock_compress.call_args[1]["rtk_path"] == "rtk"
            assert mock_compress.call_args[1]["exclude_commands"] == []

    def test_none_config_uses_defaults(self):
        """None config should use default values."""
        ctx = MagicMock()
        ctx.config = None
        with patch("hermes_rtkit.plugin.compress_output") as mock_compress:
            mock_compress.return_value = "result"
            register(ctx)
            hook_func = ctx.register_hook.call_args[0][1]
            hook_func("cargo test", "raw", 0, "t", "local")
            assert mock_compress.call_args[1]["enabled"] is True
            assert mock_compress.call_args[1]["rtk_path"] == "rtk"
