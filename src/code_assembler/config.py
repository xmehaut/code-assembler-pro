"""
Configuration classes for Code Assembler Pro.

This module defines all configuration dataclasses and validation logic.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict

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
        compress: If True, reduces files to signatures + docstrings only
        compress_level: Compression depth — "signatures" keeps function/class
                        headers and docstrings; "docstrings_only" is reserved
                        for a future stricter mode.
        description: Optional free-text description embedded in the
                      frontmatter block. Omitted from the frontmatter entirely
                      when None — never written as an empty/null field, so a
                      run that doesn't set it produces the exact same
                      frontmatter shape as before this field existed.
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
    description: Optional[str] = None

    # Exact filenames to match (e.g. Dockerfile, Makefile, .env)
    exact_filenames: List[str] = field(default_factory=list)

    # --- Compression (v4.5) ---
    compress: bool = False
    compress_level: str = "signatures"  # "signatures" | "docstrings_only"

    def __post_init__(self):
        """Validate and normalize configuration after initialization."""
        if not self.paths:
            raise ValueError("At least one path must be specified")
        if not self.extensions:
            raise ValueError("At least one extension must be specified")

        # Validate compress_level early so the error is clear
        valid_levels = {"signatures", "docstrings_only"}
        if self.compress_level not in valid_levels:
            raise ValueError(
                f"compress_level must be one of {valid_levels}, "
                f"got: '{self.compress_level}'"
            )

        # Separate exact filenames from extensions
        normalized_ext = []
        for ext in self.extensions:
            # FIX: guard against empty strings — ext[0] would raise IndexError
            if not ext:
                continue
            if ext.startswith('.'):
                # Already has dot: .py, .env, .env.j2 → extension
                normalized_ext.append(ext)
            elif '.' in ext:
                # Has internal dot but no leading dot: env.j2 → .env.j2
                normalized_ext.append(f'.{ext}')
            elif ext[0].isupper():
                # Starts with uppercase, no dot: Dockerfile, Makefile → exact filename
                self.exact_filenames.append(ext)
            else:
                # Lowercase, no dot: py, md, js → extension, add dot
                normalized_ext.append(f'.{ext}')

        self.extensions = normalized_ext

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
            "compress": self.compress,
            "compress_level": self.compress_level,
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
    source_chars: int = 0
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
        self.source_chars += size

        if extension not in self.files_by_ext:
            self.files_by_ext[extension] = 0
        self.files_by_ext[extension] += 1

    def skip_file(self, path: str, reason: str = ""):
        entry = f"{path}" + (f" ({reason})" if reason else "")
        self.skipped_files.append(entry)


def derive_module_output(root_output: str, module_name: str) -> str:
    """
    Derive a per-module output filename from the root "output" (MODULES_SPEC.md
    §4): insert "_{module_name}" before the extension, defaulting to ".md" if
    the root output has none, and preserving any directory component.

        "codebase.md"            + "api" -> "codebase_api.md"
        "codebase"                + "api" -> "codebase_api.md"
        "snapshots/codebase.md"  + "api" -> "snapshots/codebase_api.md"
    """
    p = Path(root_output)
    suffix = p.suffix if p.suffix else ".md"
    new_name = f"{p.stem}_{module_name}{suffix}"
    return str(p.parent / new_name) if str(p.parent) != "." else new_name


def resolve_module_configs(config_data: dict) -> Dict[str, dict]:
    """
    Expand a "modules" block (MODULES_SPEC.md §2-4) into one fully-resolved
    config dict per module, ready to pass as **kwargs to assemble_codebase().

    Every static error is raised here, before any module is assembled —
    the whole point of validating up front (§9, §10) is that a batch never
    starts writing files only to fail midway on something that was already
    knowable from the config alone (an unknown path or a genuinely broken
    module can still fail later, at assembly time — that's a runtime
    failure, handled per-module by the caller, not a config error).

    Override semantics (§3): a module's own keys REPLACE the matching root
    key entirely — no merging, no appending, one rule for every key.
    """
    if "paths" in config_data:
        raise ValueError(
            '"paths" and "modules" are mutually exclusive at the config root '
            '— set "paths" inside each module instead (see MODULES_SPEC.md §2.1)'
        )

    modules = config_data.get("modules")
    if not modules or not isinstance(modules, dict):
        raise ValueError('"modules" must be a non-empty object of {name: config}')

    # Every root key except the four with module-specific handling becomes
    # each module's default, per §3. "depends_on" is deliberately excluded
    # from inheritance too: a root-level depends_on would apply to every
    # module including the one it names, producing an instant, confusing
    # self-reference error for that module. §6 scopes it to per-module only.
    root_defaults = {
        k: v for k, v in config_data.items()
        if k not in ("modules", "paths", "output", "depends_on")
    }
    root_output = config_data.get("output", "codebase.md")

    resolved: Dict[str, dict] = {}
    for name, module_conf in modules.items():
        if not isinstance(module_conf, dict):
            raise ValueError(f'Module "{name}" must be a config object')
        if "/" in name or "\\" in name:
            raise ValueError(
                f'Module name "{name}" must not contain a path separator '
                '(flat module names only — see MODULES_SPEC.md §4/§8)'
            )
        if "paths" not in module_conf:
            raise ValueError(f'Module "{name}" must define its own "paths"')

        effective = dict(root_defaults)
        effective.update(module_conf)  # module keys replace root keys, wholesale

        if not effective.get("extensions"):
            raise ValueError(
                f'Module "{name}" has no "extensions" — set it at the module '
                'level or at the config root'
            )

        depends_on = effective.get("depends_on") or []
        if not isinstance(depends_on, list):
            raise ValueError(f'Module "{name}": "depends_on" must be a list of module names')
        effective["depends_on"] = depends_on

        effective.setdefault("output", derive_module_output(root_output, name))
        resolved[name] = effective

    # §6: every depends_on reference must resolve to another module in the
    # same batch — checked only once every module name is known, so order
    # inside the "modules" object never matters, and a self-reference is
    # rejected explicitly rather than silently accepted as a trivial cycle.
    module_names = set(resolved)
    for name, effective in resolved.items():
        for dep in effective["depends_on"]:
            if dep == name:
                raise ValueError(f'Module "{name}" cannot depend_on itself')
            if dep not in module_names:
                raise ValueError(f'Module "{name}" depends_on unknown module "{dep}"')

    return resolved