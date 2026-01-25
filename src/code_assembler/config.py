"""
Configuration classes for Code Assembler Pro.

This module defines all configuration dataclasses and validation logic.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .constants import DEFAULT_EXCLUDE_PATTERNS, DEFAULT_MAX_FILE_SIZE_MB


@dataclass
class AssemblerConfig:
    """
    Main configuration for codebase assembly.

    Attributes:
        paths: List of file/directory paths to process
        extensions: File extensions to include (with or without leading dot)
        exclude_patterns: Patterns to exclude from processing
        output_file: Output markdown filename
        recursive: Whether to recursively traverse directories
        include_readmes: Whether to automatically include README files
        max_file_size_mb: Maximum file size in MB to process
        truncate_large_files: If True, truncates files exceeding max_file_size_mb
        truncation_limit_lines: Number of lines to keep if truncated
        show_progress: Whether to show progress information
        use_default_excludes: Whether to use default exclude patterns
    """

    paths: List[str]
    extensions: List[str]
    exclude_patterns: List[str] = field(default_factory=list)
    output_file: str = "codebase.md"
    recursive: bool = True
    include_readmes: bool = True
    max_file_size_mb: float = DEFAULT_MAX_FILE_SIZE_MB
    truncate_large_files: bool = True
    truncation_limit_lines: int = 500
    show_progress: bool = True
    use_default_excludes: bool = True

    def __post_init__(self):
        """Validate and normalize configuration after initialization."""
        if not self.paths:
            raise ValueError("At least one path must be specified")

        if not self.extensions:
            raise ValueError("At least one extension must be specified")

        # Normalize extensions to include leading dot
        self.extensions = [
            ext if ext.startswith('.') else f'.{ext}'
            for ext in self.extensions
        ]

        # Add default excludes if requested
        if self.use_default_excludes:
            self.exclude_patterns = list(set(
                self.exclude_patterns + DEFAULT_EXCLUDE_PATTERNS
            ))

        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")

    @classmethod
    def from_dict(cls, config_dict: dict) -> "AssemblerConfig":
        return cls(**config_dict)

    def to_dict(self) -> dict:
        return {
            "paths": self.paths,
            "extensions": self.extensions,
            "exclude_patterns": self.exclude_patterns,
            "output_file": self.output_file,
            "recursive": self.recursive,
            "include_readmes": self.include_readmes,
            "max_file_size_mb": self.max_file_size_mb,
            "truncate_large_files": self.truncate_large_files,
            "truncation_limit_lines": self.truncation_limit_lines,
            "show_progress": self.show_progress,
            "use_default_excludes": self.use_default_excludes,
        }


@dataclass
class FileEntry:
    """Represents a file or directory entry in the table of contents."""
    path: str
    type: str  # 'file' or 'dir'
    depth: int
    size_bytes: int = 0
    line_count: int = 0

    @property
    def name(self) -> str:
        return Path(self.path).name

    @property
    def is_file(self) -> bool:
        return self.type == 'file'

    @property
    def is_directory(self) -> bool:
        return self.type == 'dir'


@dataclass
class CodebaseStats:
    """Statistics about the assembled codebase."""
    total_files: int = 0
    total_lines: int = 0
    total_chars: int = 0
    estimated_tokens: int = 0
    files_by_ext: dict = field(default_factory=dict)
    largest_file: Optional[tuple] = None
    max_depth: int = 0
    skipped_files: List[str] = field(default_factory=list)

    def update_largest_file(self, path: str, size: int):
        if not self.largest_file or size > self.largest_file[1]:
            self.largest_file = (path, size)

    def add_file(self, extension: str, lines: int, size: int):
        self.total_files += 1
        self.total_lines += lines

        if extension not in self.files_by_ext:
            self.files_by_ext[extension] = 0
        self.files_by_ext[extension] += 1

    def skip_file(self, path: str, reason: str = ""):
        entry = f"{path}" + (f" ({reason})" if reason else "")
        self.skipped_files.append(entry)