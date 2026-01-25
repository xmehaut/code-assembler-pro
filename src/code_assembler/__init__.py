"""
Code Assembler Pro - A tool for consolidating source code for LLM analysis.
"""

from .core import assemble_codebase, assemble_from_config
from .config import AssemblerConfig
from .constants import __version__
from .interactive import run_interactive_mode

__all__ = [
    "assemble_codebase",
    "assemble_from_config",
    "AssemblerConfig",
    "run_interactive_mode",
    "__version__",
]