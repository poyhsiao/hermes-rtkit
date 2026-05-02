"""hermes-rtkit -- RTK Integration for Hermes Agent."""

__version__ = "0.1.0"
__author__ = "kimhsiao"

from hermes_rtkit.compression import compress_output, is_supported_command
from hermes_rtkit.plugin import register

__all__ = [
    "__version__",
    "compress_output",
    "is_supported_command",
    "register",
]
