"""
Utility functions for Code Assembler Pro.

This module provides helper functions for path normalization,
string formatting, and other common operations.
"""

import re
from pathlib import Path
from typing import List, Set

from .constants import CHARS_PER_TOKEN


def normalize_path(path: str) -> str:
    """
    Normalize a path to a consistent format.
    Converts to absolute, POSIX-style, lowercase path without trailing slash.
    """
    if not path:
        return ""

    p = Path(path)
    if not p.is_absolute():
        p = p.resolve()

    return str(p).replace("\\", "/").lower().rstrip("/")


def slugify_path(path: str) -> str:
    """
    Convert a file path to a valid HTML anchor identifier.
    """
    return re.sub(r'[^a-zA-Z0-9]', '_', path).lower()


def should_exclude(path: str, exclude_patterns: List[str]) -> bool:
    """
    Determine if a path should be excluded based on patterns.
    """
    if not exclude_patterns:
        return False

    path_norm = normalize_path(path)
    path_parts: Set[str] = set(p for p in path_norm.split("/") if p)

    for pattern in exclude_patterns:
        if not pattern:
            continue

        # Simple pattern (no slashes)
        if "/" not in pattern and "\\" not in pattern:
            clean_pattern = pattern.lower()

            # Exact segment match
            if clean_pattern in path_parts:
                return True

            # Partial segment match (prefix/suffix)
            for part in path_parts:
                if part.startswith(clean_pattern) or part.endswith(clean_pattern):
                    return True
        else:
            # Path-based pattern
            pattern_norm = normalize_path(pattern)
            if path_norm == pattern_norm:
                return True
            if path_norm.startswith(pattern_norm + "/"):
                return True

    return False


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text (~4 chars per token).
    """
    return len(text) // CHARS_PER_TOKEN


def format_file_size(size_bytes: int) -> str:
    """
    Format a file size in human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}PB"


def format_number(num: int) -> str:
    """
    Format a number with thousands separators.
    """
    return f"{num:,}"


def get_file_extension(path: str) -> str:
    """
    Get the file extension from a path.
    """
    return Path(path).suffix


def count_lines(text: str) -> int:
    """
    Count the number of lines in a text.
    """
    return len(text.splitlines())