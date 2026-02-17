"""
Utility functions for Code Assembler Pro.

This module provides helper functions for path normalization,
string formatting, clipboard operations, and other common tasks.
"""

import re
import fnmatch
import subprocess
import platform
from pathlib import Path, PurePosixPath
from typing import List

from .constants import CHARS_PER_TOKEN


def normalize_path(path: str) -> str:
    """
    Normalize a path to a consistent POSIX-style lowercase string.
    Does NOT resolve against CWD to avoid environment-dependent behavior.
    """
    if not path:
        return ""
    # Convert to forward slashes and lowercase, strip trailing slash
    return str(PurePosixPath(path)).replace("\\", "/").lower().rstrip("/")


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
    path_parts: List[str] = [p for p in path_norm.split("/") if p]

    for pattern in exclude_patterns:
        if not pattern:
            continue

        clean_pattern = pattern.lower().rstrip("/")

        # Path-based pattern (contains /)
        if "/" in clean_pattern or "\\" in clean_pattern:
            pattern_norm = normalize_path(clean_pattern)
            if path_norm == pattern_norm:
                return True
            if ("/" + pattern_norm + "/") in ("/" + path_norm + "/"):
                return True
            continue

        # Simple pattern — match against each path segment
        for part in path_parts:
            if part == clean_pattern:
                return True
            if ("*" in clean_pattern or "?" in clean_pattern):
                if fnmatch.fnmatch(part, clean_pattern):
                    return True
            if clean_pattern.startswith(".") and part.endswith(clean_pattern):
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
    if size_bytes == 0:
        return "0B"
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}" if unit != 'B' else f"{int(size)}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


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


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to the system clipboard without external dependencies.
    Handles Unicode characters correctly on Windows, macOS, and Linux.
    """
    system = platform.system()
    try:
        if system == "Windows":
            # 1. On force PowerShell à interpréter l'entrée (stdin) en UTF8
            # 2. On utilise Out-String pour s'assurer que le flux est traité comme une chaîne unique
            # 3. On utilise l'encodage 'utf-8' côté Python
            command = [
                "powershell", "-NoProfile", "-Command",
                "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
                "$input | Out-String | Set-Clipboard"
            ]
            subprocess.run(command, input=text, encoding='utf-8', check=True)

        elif system == "Darwin":  # macOS
            subprocess.run("pbcopy", input=text, text=True, check=True)

        elif system == "Linux":
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
            except FileNotFoundError:
                subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False
