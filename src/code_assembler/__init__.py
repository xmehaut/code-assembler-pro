"""
Code Assembler Pro - A tool for consolidating source code for LLM analysis.
"""

from .core import assemble_codebase, assemble_from_config
from .config import AssemblerConfig
from .constants import __version__

__all__ = [
    "assemble_codebase",
    "assemble_from_config",
    "AssemblerConfig",
    "__version__",
]