"""Hermes plugin for RTK terminal output compression.

Registers the `transform_terminal_output` hook to intercept and
compress terminal command outputs before they reach the LLM.
"""

from __future__ import annotations

import subprocess
import shutil
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from hermes_cli.plugins import PluginContext

from hermes_cli.config import load_config

# Supported commands mapped to their RTK filter names
RTK_FILTER_MAP: dict[str, str] = {
    "cargo": "cargo-test",
    "pytest": "pytest",
    "git": "git-log",
    "npm": "npm",
    "pnpm": "pnpm",
    "docker": "docker",
    "kubectl": "kubectl",
    "ruff": "ruff",
    "eslint": "eslint",
    "rubocop": "rubocop",
    "rspec": "rspec",
    "mypy": "mypy",
    "golangci-lint": "golangci-lint",
    "bundle": "bundle",
    "gradle": "gradle",
    "mvn": "mvn",
    "make": "make",
    "cmake": "cmake",
    "curl": "curl",
    "wget": "wget",
    "aws": "aws",
    "gcloud": "gcloud",
    "az": "az",
    "terraform": "terraform",
    "ansible": "ansible",
    "vagrant": "vagrant",
    "psql": "psql",
    "mongosh": "mongosh",
    "redis-cli": "redis-cli",
}

# Commands that have sub-command-specific filters
SUBCOMMAND_FILTERS: dict[tuple[str, str], str] = {
    ("git", "diff"): "git-diff",
    ("git", "status"): "git-log",
    ("git", "log"): "git-log",
    ("git", "branch"): "git-log",
    ("cargo", "test"): "cargo-test",
    ("cargo", "build"): "cargo-build",
    ("cargo", "check"): "cargo-test",
    ("cargo", "clippy"): "cargo-test",
    ("npm", "test"): "npm",
    ("npm", "run"): "npm",
    ("pnpm", "test"): "pnpm",
    ("pnpm", "run"): "pnpm",
    ("docker", "ps"): "docker",
    ("docker", "images"): "docker",
    ("docker", "logs"): "docker",
    ("kubectl", "get"): "kubectl",
    ("kubectl", "describe"): "kubectl",
    ("kubectl", "logs"): "kubectl",
    ("ruff", "check"): "ruff",
    ("ruff", "format"): "ruff",
}


def get_rtk_filter(command: str) -> Optional[str]:
    """Determine the RTK filter name for a given command."""
    if not command:
        return None
    parts = command.strip().split()
    if not parts:
        return None
    cmd_base = parts[0]
    subcmd = parts[1] if len(parts) > 1 else None
    if subcmd:
        filter_name = SUBCOMMAND_FILTERS.get((cmd_base, subcmd))
        if filter_name:
            return filter_name
    return RTK_FILTER_MAP.get(cmd_base)


def is_supported_command(command: str) -> bool:
    """Check if command has a supported RTK filter."""
    return get_rtk_filter(command) is not None


def compress_output(
    command: str,
    output: str,
    enabled: bool = True,
    exclude_commands: Optional[list[str]] = None,
    rtk_path: str = "rtk",
    timeout: float = 2.0,
) -> str:
    """Compress terminal output using RTK if available and command is supported."""
    if not enabled:
        return output
    if exclude_commands is None:
        exclude_commands = []
    if not command:
        return output
    cmd_base = command.strip().split()[0]
    if cmd_base in exclude_commands:
        return output
    filter_name = get_rtk_filter(command)
    if not filter_name:
        return output
    if not shutil.which(rtk_path):
        return output
    if not output or not output.strip():
        return output
    try:
        result = subprocess.run(
            [rtk_path, "pipe", "-f", filter_name],
            input=output,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return output
        compressed = result.stdout
        if not compressed or not compressed.strip():
            return output
        return compressed
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return output


def register(ctx: "PluginContext") -> None:
    """Register the transform_terminal_output hook with Hermes."""
    # Get per-plugin config from config.yaml: plugins.hermes-rtkit.*
    plugin_cfg = {}
    try:
        full_cfg = load_config()
        plugins_cfg = full_cfg.get("plugins") or {}
        plugin_cfg = plugins_cfg.get("hermes-rtkit") or {}
    except Exception:
        pass

    enabled = plugin_cfg.get("enabled", True)
    verbose = plugin_cfg.get("verbose", False)
    rtk_path = plugin_cfg.get("rtk_path", "rtk")
    exclude_commands = plugin_cfg.get("exclude_commands", [])

    def transform_terminal_output(
        command: str,
        output: str,
        returncode: int,
        task_id: str,
        env_type: str,
    ) -> Optional[str]:
        if not enabled:
            return output
        original_output = output
        result = compress_output(
            command=command,
            output=output,
            enabled=enabled,
            exclude_commands=exclude_commands,
            rtk_path=rtk_path,
        )
        if verbose and result != original_output:
            saved = len(original_output) - len(result)
            pct = (saved / len(original_output) * 100) if original_output else 0
            print(
                f"[hermes-rtkit] Compressed '{command}' "
                f"({len(original_output)} -> {len(result)} chars, "
                f"{pct:.0f}% saved)"
            )
        return result

    ctx.register_hook("transform_terminal_output", transform_terminal_output)
