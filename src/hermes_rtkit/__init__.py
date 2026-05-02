"""hermes-rtkit: RTK-powered terminal output compression for Hermes Agent.

This package is installed via pip and used for development/testing.
The Hermes plugin lives at ~/.hermes/plugins/hermes-rtkit/ instead.
"""

from __future__ import annotations

from hermes_rtkit.plugin import (  # noqa: F401
    register,
    get_rtk_filter,
    is_supported_command,
    compress_output,
    RTK_FILTER_MAP,
    SUBCOMMAND_FILTERS,
)

__version__ = "0.1.0"
