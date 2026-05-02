"""Hermes plugin for RTK terminal output compression.

Registers the `transform_terminal_output` hook to intercept and
compress terminal command outputs before they reach the LLM.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from hermes_rtkit.compression import compress_output

if TYPE_CHECKING:
    from hermes_cli.plugins import PluginContext


def register(ctx: PluginContext) -> None:
    """Register the transform_terminal_output hook with Hermes.

    Args:
        ctx: Plugin context containing configuration from config.yaml.
             Expected config keys:
               - enabled (bool): Master switch (default: True)
               - verbose (bool): Log compression events (default: False)
               - rtk_path (str): Path to RTK binary (default: "rtk")
               - exclude_commands (list[str]): Commands to never compress
    """
    config = ctx.config or {}
    enabled = config.get("enabled", True)
    verbose = config.get("verbose", False)
    rtk_path = config.get("rtk_path", "rtk")
    exclude_commands = config.get("exclude_commands", [])

    def transform_terminal_output(
        command: str,
        output: str,
        returncode: int,
        task_id: str,
        env_type: str,
    ) -> Optional[str]:
        # Fast path: skip all compression work when disabled
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
