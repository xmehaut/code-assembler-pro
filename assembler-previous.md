# Consolidated Codebase

> **Snapshot:** 2026-05-02 04:39 | **Files:** 34 | **Tokens:** ~28,149

---

## Table of Contents

- `code_assembler/`
  - `__init__.py` | 2026-02-17 09:29
  - `__main__.py` | 2026-02-17 09:29
  - `analyzers.py` | 2026-02-17 09:28
  - `cli.py` | 2026-02-17 09:29
  - `config.py` | 2026-02-17 09:29
  - `constants.py` | 2026-02-17 11:22
  - `core.py` | 2026-02-17 09:29
  - `delta.py` | 2026-02-17 09:28
  - `file_io.py` | 2026-02-17 09:29
  - `formatters.py` | 2026-02-17 09:29
  - `interactive.py` | 2026-02-17 09:29
  - `rebuilder.py` | 2026-02-17 11:25
  - `templates/`
    - `components/`
      - `architecture.md.j2` | 2026-02-14 19:44
      - `file_block.md.j2` | 2026-02-14 19:44
      - `readme_context.md.j2` | 2026-02-14 19:44
      - `stats_table.md.j2` | 2026-02-14 19:44
      - `toc.md.j2` | 2026-02-16 16:43
    - `main_header.md.j2` | 2026-02-16 16:59
  - `utils.py` | 2026-02-17 10:10
- `__init__.py` | 2026-01-25 11:22
- `advanced_config.py` | 2026-02-17 11:20
- `basic_usage.py` | 2026-02-17 11:26
- `interactive_demo.py` | 2026-01-25 16:13
- `rebuild_usage.py` | 2026-02-17 11:28
- `__init__.py` | 2026-01-25 11:21
- `test_clipboard.py` | 2026-02-17 10:10
- `test_config.py` | 2026-02-17 09:29
- `test_core.py` | 2026-02-17 09:29
- `test_delta_scenario.py` | 2026-02-17 09:29
- `test_file_io.py` | 2026-02-17 09:29
- `test_formats.py` | 2026-02-17 09:29
- `test_interactive.py` | 2026-02-17 09:29
- `test_rebuild.py` | 2026-02-17 09:29
- `test_utils.py` | 2026-02-17 09:29


---

## Architecture

**Components:**
- `examples/` (5 files)
- `src/` (19 files)
- `tests/` (10 files)

**File types:**
- `.py` (python): 28 — 82.4%
- `.j2` (jinja2): 6 — 17.6%


---

## Stats

**34** files | **3,255** lines | ~**28,149** tokens | Extensions: j2, py


---

34 source files follow below.

---


# `code_assembler/`

### `src\code_assembler\__init__.py`

```python
"""
Code Assembler Pro - A tool for consolidating source code for LLM analysis.
"""

from .config import AssemblerConfig
from .constants import __version__
from .core import assemble_codebase, assemble_from_config
from .interactive import run_interactive_mode

__all__ = [
    "assemble_codebase",
    "assemble_from_config",
    "AssemblerConfig",
    "run_interactive_mode",
    "__version__",
]

```

### `src\code_assembler\__main__.py`

```python
"""
Entry point for: python -m code_assembler
"""
from .cli import main

if __name__ == "__main__":
    main()

```

### `src\code_assembler\analyzers.py`

```python
"""
Architecture and Quality analyzers for Code Assembler Pro.

This module extracts structural data and patterns from the codebase
without handling formatting (delegated to templates).
"""
import os
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set, Any

from .config import FileEntry, CodebaseStats
from .constants import LANGUAGE_MAP


class ArchitectureAnalyzer:
    """Analyzes codebase structure and detects patterns, returning raw data."""

    def __init__(self, entries: List[FileEntry], stats: CodebaseStats):
        """
        Initialize analyzer.

        Args:
            entries: List of file entries
            stats: Codebase statistics
        """
        self.entries = entries
        self.stats = stats

    def analyze_data(self) -> Dict[str, Any]:
        """
        Perform complete architecture analysis and return raw data.
        """
        # Calculate depth distribution first to update self.stats.max_depth
        depth_dist = self._get_depth_distribution()

        return {
            "components": self._get_components(),
            "distribution": self._get_distribution(),
            "patterns": self._get_patterns(),
            "max_depth": self.stats.max_depth,
            "depth_distribution": depth_dist
        }

    def _get_components(self) -> List[Dict[str, Any]]:
        """Identify top-level components relative to the entries."""
        if not self.entries:
            return []

        # Find the common path to determine the root
        all_paths = [Path(e.path) for e in self.entries]
        root_path = Path(os.path.commonpath([str(p) for p in all_paths]))

        results = []
        top_dirs = set()

        for entry in self.entries:
            try:
                # Calculate relative path from common root
                rel_path = Path(entry.path).relative_to(root_path)
                if len(rel_path.parts) > 1:
                    top_dirs.add(rel_path.parts[0])
            except ValueError:
                continue

        for dir_name in sorted(top_dirs):
            # Count files belonging to this component
            count = sum(1 for e in self.entries if e.is_file and dir_name in Path(e.path).parts)
            results.append({"name": dir_name, "count": count})

        return results

    def _get_depth_distribution(self) -> Dict[int, int]:
        """Count files at each directory depth level and sync max_depth."""
        depth_counts = defaultdict(int)
        for e in self.entries:
            if e.is_file:
                depth_counts[e.depth] += 1

        if depth_counts:
            self.stats.max_depth = max(depth_counts.keys())

        return dict(sorted(depth_counts.items()))

    def _get_distribution(self) -> List[Dict[str, Any]]:
        """Get file distribution by extension and language."""
        results = []
        if not self.stats.files_by_ext:
            return results

        # Sort by count descending
        sorted_exts = sorted(
            self.stats.files_by_ext.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for ext, count in sorted_exts:
            lang = LANGUAGE_MAP.get(ext, "unknown")
            percentage = (count / self.stats.total_files * 100) if self.stats.total_files > 0 else 0
            results.append({
                "ext": ext,
                "lang": lang,
                "count": count,
                "percentage": round(percentage, 1)
            })
        return results

    def _get_patterns(self) -> List[str]:
        """Detect common design patterns based on filenames."""
        dir_files: Dict[str, Set[str]] = defaultdict(set)
        for entry in self.entries:
            if entry.is_file:
                parent = str(Path(entry.path).parent)
                filename = Path(entry.path).name.lower()
                dir_files[parent].add(filename)

        detected = []
        patterns_map = {
            'MVC': {
                'indicators': ['model.py', 'view.py', 'controller.py'],
                'description': 'Model-View-Controller pattern detected'
            },
            'Testing': {
                'indicators': ['test_', '__test__', 'tests.py', 'test.py'],
                'description': 'Organized test structure'
            },
            'Configuration': {
                'indicators': ['.env', 'config.py', 'settings.py', 'config.yml', 'pyproject.toml'],
                'description': 'Centralized configuration files'
            },
            'Documentation': {
                'indicators': ['readme.md', 'docs/', 'documentation/'],
                'description': 'Structured documentation'
            },
            'API': {
                'indicators': ['routes.py', 'api.py', 'endpoints.py', 'views.py'],
                'description': 'API/Routes architecture'
            },
            'Database': {
                'indicators': ['models.py', 'schema.py', 'migrations/', 'db.py'],
                'description': 'Persistence/Database layer'
            },
        }

        for pattern_info in patterns_map.values():
            for files in dir_files.values():
                if any(any(ind in f for f in files) for ind in pattern_info['indicators']):
                    detected.append(pattern_info['description'])
                    break

        return sorted(list(set(detected)))

```

### `src\code_assembler\cli.py`

```python
"""
Command Line Interface (CLI) for Code Assembler Pro.

This module serves as the main entry point for the application. It handles
argument parsing and dispatches execution to the appropriate engine:
1. Assembly Engine: Consolidates code into Markdown (Direct or Config mode).
2. Rebuild Engine: Reconstructs a project from a Markdown snapshot.
3. Interactive Engine: Guided wizard for configuration.

New in v4.4.0:
    - --rebuild: Restore project structure from a .md file.
    - --clip: Direct copy to system clipboard.
    - --since: Incremental updates based on previous snapshots.
"""

import argparse
import json
import sys
from typing import List, Optional

from .constants import (
    __version__,
    DEFAULT_MAX_FILE_SIZE_MB,
    EMOJI
)
from .core import assemble_codebase, assemble_from_config


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Consolidate a codebase into a single Markdown file for LLM analysis or rebuild it."
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # --- Execution Modes ---
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive wizard")
    parser.add_argument("--config", "-c", type=str, help="Path to a JSON configuration file")

    # --- Rebuild Mode ---
    rebuild_group = parser.add_argument_group("Rebuild Mode")
    rebuild_group.add_argument("--rebuild", type=str, metavar="MD_FILE", help="Reconstruct project")
    rebuild_group.add_argument("--output-dir", type=str, default="./rebuilt_project", help="Target directory")
    rebuild_group.add_argument("--dry-run", action="store_true", help="Preview rebuild")

    # --- Utility Flags ---
    parser.add_argument("--show-excludes", action="store_true", help="Show default exclusions")
    parser.add_argument("--save-config", type=str, metavar="FILE", help="Save CLI args to JSON")
    parser.add_argument("--clip", "-k", action="store_true", help="Copy to clipboard")

    # --- Main Arguments ---
    parser.add_argument("paths", nargs="*", help="Files or directories to analyze")
    parser.add_argument("--ext", "-e", dest="extensions", nargs="+", help="Extensions to include")
    parser.add_argument("--output", "-o", default="codebase.md", help="Output filename")
    parser.add_argument("--exclude", "-x", dest="exclude_patterns", nargs="+", help="Extra exclusions")

    # --- Flags ---
    parser.add_argument("--no-recursive", action="store_false", dest="recursive", help="Disable recursion")
    parser.add_argument("--no-readmes", action="store_false", dest="include_readmes", help="Disable READMEs")
    parser.add_argument("--no-default-excludes", action="store_false", dest="use_default_excludes",
                        help="Disable defaults")
    parser.add_argument("--max-size", type=float, default=DEFAULT_MAX_FILE_SIZE_MB, help="Max size in MB")
    parser.add_argument("--since", "-s", type=str, metavar="SNAPSHOT", help="Delta mode")

    parser.set_defaults(recursive=True, include_readmes=True, use_default_excludes=True)
    return parser.parse_args()


def _save_config(args: argparse.Namespace, extensions: List[str]):
    """Save CLI arguments as a JSON config file."""
    config = {
        "paths": args.paths,
        "extensions": extensions,
        "output": args.output,
        "recursive": args.recursive,
        "include_readmes": args.include_readmes,
        "max_file_size_mb": args.max_size,
        "use_default_excludes": args.use_default_excludes,
    }
    if args.exclude_patterns:
        config["exclude_patterns"] = args.exclude_patterns

    with open(args.save_config, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point."""
    args = parse_args()
    content: Optional[str] = None

    try:
        if args.show_excludes:
            from .cli import _show_excludes
            _show_excludes()
            return

        if args.interactive:
            from .interactive import run_interactive_mode
            run_interactive_mode()
            return

        if args.rebuild:
            from .rebuilder import CodebaseRebuilder
            rebuilder = CodebaseRebuilder(args.rebuild, args.output_dir, args.dry_run)
            count, errors = rebuilder.rebuild()
            return

        if args.config:
            # FIX: Removed args.show_progress check
            content = assemble_from_config(args.config, since=args.since)
        else:
            if not args.paths or not args.extensions:
                print(f"{EMOJI['error']} Error: Paths and extensions are required.")
                sys.exit(1)

            if args.save_config:
                _save_config(args, args.extensions)

            content = assemble_codebase(
                paths=args.paths,
                extensions=args.extensions,
                exclude_patterns=args.exclude_patterns,
                output=args.output,
                recursive=args.recursive,
                include_readmes=args.include_readmes,
                max_file_size_mb=args.max_size,
                use_default_excludes=args.use_default_excludes,
                since=args.since,
            )

        if args.clip and content:
            from .utils import copy_to_clipboard
            if copy_to_clipboard(content):
                print(f"{EMOJI['clipboard']} Content copied to clipboard!")

    except Exception as e:
        print(f"\n{EMOJI['error']} An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

```

### `src\code_assembler\config.py`

```python
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

    # Exact filenames to match (e.g. Dockerfile, Makefile, .env)
    exact_filenames: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate and normalize configuration after initialization."""
        if not self.paths:
            raise ValueError("At least one path must be specified")
        if not self.extensions:
            raise ValueError("At least one extension must be specified")

        # Separate exact filenames from extensions
        normalized_ext = []
        for ext in self.extensions:
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

```

### `src\code_assembler\constants.py`

```python
"""
Constants for Code Assembler Pro.

This module contains all constant values used throughout the package,
including language mappings, file extensions, and default configurations.
"""

from typing import Dict

try:
    from importlib.metadata import version as _get_version

    __version__ = _get_version("code-assembler-pro")
except Exception:
    __version__ = "4.4.2"  # Fallback for dev mode without pip install

# Language mapping for syntax highlighting
LANGUAGE_MAP: Dict[str, str] = {
    # Programming languages
    ".py": "python",
    ".pyw": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "jsx",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".hxx": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".m": "objective-c",
    ".r": "r",
    ".jl": "julia",
    ".lua": "lua",
    ".pl": "perl",
    ".pm": "perl",
    ".dart": "dart",
    ".elm": "elm",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hrl": "erlang",
    ".clj": "clojure",
    ".cljs": "clojure",
    ".fs": "fsharp",
    ".fsx": "fsharp",
    ".hs": "haskell",
    ".ml": "ocaml",
    ".v": "verilog",
    ".vhd": "vhdl",

    # Web & markup
    ".html": "html",
    ".htm": "html",
    ".xml": "xml",
    ".svg": "xml",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".vue": "vue",
    ".svelte": "svelte",

    # Data & config
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "ini",
    ".csv": "csv",
    ".tsv": "csv",

    # Documentation
    ".md": "markdown",
    ".markdown": "markdown",
    ".rst": "rst",
    ".txt": "text",
    ".adoc": "asciidoc",

    # Shell & scripts
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".fish": "fish",
    ".ps1": "powershell",
    ".psm1": "powershell",
    ".bat": "batch",
    ".cmd": "batch",

    # Database
    ".sql": "sql",
    ".psql": "sql",
    ".mysql": "sql",
    ".pgsql": "sql",

    # Build & CI/CD
    ".dockerfile": "dockerfile",
    ".dockerignore": "text",
    ".gitignore": "text",
    ".gitattributes": "text",
    ".editorconfig": "ini",

    # Other
    ".env": "bash",
    ".properties": "properties",
    ".gradle": "gradle",
    ".makefile": "makefile",
    ".cmake": "cmake",
    ".proto": "protobuf",
    ".graphql": "graphql",
    ".gql": "graphql",

    # Templates & Web Engines
    ".j2": "jinja2",
    ".jinja": "jinja2",
    ".jinja2": "jinja2",
    ".liquid": "liquid",
    ".handlebars": "handlebars",
    ".hbs": "handlebars",
    ".mustache": "mustache",

    # Infrastructure & Cloud (DevOps)
    ".tf": "hcl",
    ".hcl": "hcl",
    ".terraform": "hcl",
    ".nomad": "hcl",
    ".k8s": "yaml",
    ".properties": "properties",

    # Modern Web & Data
    ".astro": "astro",
    ".prisma": "prisma",
    ".graphql": "graphql",
    ".gql": "graphql",
    ".ipynb": "json",
    ".jsonl": "json",
}

# Default exclude patterns
DEFAULT_EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".dylib",
    ".egg-info",
    ".eggs",
    "dist",
    "build",
    ".git",
    ".svn",
    ".hg",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode",
    ".DS_Store",
    "Thumbs.db",
]

# Common README filenames
README_FILENAMES = [
    "README.md",
    "README.MD",
    "README.rst",
    "README.txt",
    "README",
    "readme.md",
    "Readme.md",
]

# Token estimation constants
CHARS_PER_TOKEN = 4  # Average characters per token (rough estimate)

# File size limits
DEFAULT_MAX_FILE_SIZE_MB = 10.0
MAX_SAFE_FILE_SIZE_MB = 100.0


def _supports_emoji() -> bool:
    """Detect if the terminal can display emoji correctly."""
    import sys
    import os

    # Non-interactive (piped, CI) -> skip detection
    if not sys.stderr.isatty():
        return False

    # Windows: only Windows Terminal and modern consoles support emoji
    if os.name == 'nt':
        if os.environ.get('WT_SESSION'):
            return True
        if os.environ.get('TERM_PROGRAM'):
            return True
        return False

    # macOS / Linux -> generally fine
    return True


# Emoji icons (using Unicode escapes for encoding safety)
_EMOJI_ICONS = {
    "folder": "\U0001f4c1",
    "file": "\U0001f4c4",
    "readme": "\u2139\ufe0f",
    "success": "\u2705",
    "warning": "\u26a0\ufe0f",
    "error": "\u274c",
    "rocket": "\U0001f680",
    "chart": "\U0001f4ca",
    "target": "\U0001f3af",
    "building": "\U0001f3db\ufe0f",
    "map": "\U0001f5fa\ufe0f",
    "book": "\U0001f4d6",
    "bug": "\U0001f41b",
    "memo": "\U0001f4dd",
    "mag": "\U0001f50d",
    "test": "\U0001f9ea",
    "recycle": "\U0001f504",
    "bulb": "\U0001f4a1",
    "floppy": "\U0001f4be",
    "clipboard": "\U0001f4cb",
    "recycle": "\u267b\ufe0f",
}

# ASCII fallbacks for terminals that don't support emoji
_ASCII_ICONS = {
    "folder": "[DIR]",
    "file": "[FILE]",
    "readme": "[i]",
    "success": "[OK]",
    "warning": "[!]",
    "error": "[X]",
    "rocket": "[>>]",
    "chart": "[#]",
    "target": "[*]",
    "building": "[B]",
    "map": "[M]",
    "book": "[B]",
    "bug": "[bug]",
    "memo": "[N]",
    "mag": "[?]",
    "test": "[T]",
    "recycle": "[R]",
    "bulb": "[!]",
    "floppy": "[S]",
    "clipboard": "[CLIP]",
    "recycle": "[REBUILD]",
}

# Select the right icon set for the current terminal
EMOJI = _EMOJI_ICONS if _supports_emoji() else _ASCII_ICONS

# Header templates
HEADER_LEVELS = {
    "document": 1,
    "section": 2,
    "subsection": 3,
    "file": 2,
}

```

### `src\code_assembler\core.py`

```python
"""
Core assembly engine for Code Assembler Pro.

This module orchestrates the traversal of directories, file processing,
and the final assembly of the Markdown document, including delta analysis
and metadata injection.
"""

import os
from pathlib import Path
from typing import List, Set, Optional

from .analyzers import ArchitectureAnalyzer
from .config import AssemblerConfig, FileEntry, CodebaseStats
from .constants import README_FILENAMES, EMOJI
from .file_io import read_file_content, read_file_head
from .formatters import MarkdownFormatter
from .utils import should_exclude, get_file_extension, count_lines, estimate_tokens


class CodebaseAssembler:
    """Main assembler class that orchestrates codebase consolidation."""

    def __init__(self, config: AssemblerConfig, since: Optional[str] = None):
        """
        Initialize the assembler.

        Args:
            config: Configuration for the assembly process.
            since: Path to a previous .md snapshot for delta analysis.
        """
        self.config = config
        self.since = since
        self.since_filter: Optional[Set[str]] = None
        self.deleted_files: Set[str] = set()
        self.stats = CodebaseStats()
        self.toc_entries: List[FileEntry] = []
        self.content_buffer: List[str] = []
        self.formatter = MarkdownFormatter()

    def _collect_all_files(self) -> Set[str]:
        """Collect all candidate files from configured paths without processing them."""
        result = set()
        for path in self.config.paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                if self._matches_file(Path(path)):
                    result.add(os.path.abspath(path))
            elif os.path.isdir(path):
                self._collect_dir(path, result)
        return result

    def _collect_dir(self, dir_path: str, result: Set[str]) -> None:
        """Recursively traverse a directory to collect file paths."""
        current = Path(dir_path)
        if should_exclude(str(current), self.config.exclude_patterns):
            return
        try:
            for item in sorted(current.iterdir(), key=lambda p: p.name.lower()):
                if should_exclude(str(item), self.config.exclude_patterns):
                    continue
                if item.is_file() and self._matches_file(item):
                    result.add(os.path.abspath(str(item)))
                elif item.is_dir() and self.config.recursive:
                    self._collect_dir(str(item), result)
        except PermissionError:
            pass

    def _matches_file(self, filepath: Path) -> bool:
        """Check if a file matches configured extensions or exact filenames."""
        name = filepath.name
        if any(name.endswith(ext) for ext in self.config.extensions):
            return True
        if name in self.config.exact_filenames:
            return True
        return False

    def process_file(self, file_path: str, depth: int = 0) -> bool:
        """
        Process a single file and add its content to the buffer.
        Handles large files by truncating them if configured.
        """
        # Apply delta filter if active
        if self.since_filter is not None and os.path.abspath(file_path) not in self.since_filter:
            return False

        try:
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            content = ""
            is_truncated = False

            if size_mb > self.config.max_file_size_mb:
                if self.config.truncate_large_files:
                    limit = self.config.truncation_limit_lines
                    content = read_file_head(file_path, limit)
                    content += (
                        f"\n\n# ... [TRUNCATED] ...\n"
                        f"# Content truncated because > {self.config.max_file_size_mb}MB.\n"
                        f"# Only the first {limit} lines are shown for context."
                    )
                    is_truncated = True
                    if self.config.show_progress:
                        print(f"  {EMOJI['warning']}  Truncated (too large): {Path(file_path).name}")
                else:
                    self.stats.skip_file(file_path, f"too large: {size_mb:.1f}MB")
                    return False
            else:
                content = read_file_content(file_path)

        except OSError as e:
            self.stats.skip_file(file_path, f"system error: {e}")
            return False

        if content.startswith("[ERROR]"):
            self.stats.skip_file(file_path, "read error")
            return False

        line_count = count_lines(content)
        md_block = self.formatter.format_file_block(
            file_path=file_path, content=content, depth=depth,
            size_bytes=size_bytes, line_count=line_count
        )

        self.content_buffer.append(md_block)
        self.stats.add_file(get_file_extension(file_path), line_count, size_bytes)
        self.stats.update_largest_file(file_path, size_bytes)
        self.toc_entries.append(FileEntry(
            path=file_path, type='file', depth=depth,
            size_bytes=size_bytes, line_count=line_count
        ))

        if self.config.show_progress and not is_truncated:
            print(f"  {EMOJI['success']} {Path(file_path).name} ({line_count:,} lines)")

        return True

    def process_readme(self, dir_path: str, depth: int = 0) -> bool:
        """Process README file if it exists in the directory for context."""
        for readme_name in README_FILENAMES:
            readme_path = os.path.join(dir_path, readme_name)
            if os.path.exists(readme_path) and not should_exclude(readme_path, self.config.exclude_patterns):
                content = read_file_content(readme_path)
                if not content.startswith("[ERROR]"):
                    self.content_buffer.append(self.formatter.format_readme_context(content, depth))
                    if self.config.show_progress:
                        print(f"  {EMOJI['readme']}  README found: {readme_name}")
                    return True
        return False

    def process_directory(self, dir_path: str, depth: int = 0) -> None:
        """Process a directory recursively."""
        current_path = Path(dir_path)
        if should_exclude(str(current_path), self.config.exclude_patterns):
            return

        if self.config.show_progress:
            print(f"{'  ' * depth}{EMOJI['folder']} {current_path.name}")

        try:
            if self.config.include_readmes:
                self.process_readme(str(current_path), depth)

            items = sorted(current_path.iterdir(), key=lambda p: p.name.lower())
            for item in items:
                if should_exclude(str(item), self.config.exclude_patterns):
                    continue
                if item.is_file() and self._matches_file(item):
                    self.process_file(str(item), depth)
                elif item.is_dir() and self.config.recursive:
                    self.content_buffer.append(self.formatter.format_directory_header(str(item), depth))
                    self.toc_entries.append(FileEntry(path=str(item), type='dir', depth=depth))
                    self.process_directory(str(item), depth + 1)
        except PermissionError:
            self.stats.skip_file(str(current_path), "permission denied")

    def assemble(self) -> str:
        """Assemble the complete codebase into a single Markdown string."""

        # Handle Delta Mode
        delta_summary = ""
        if self.since and os.path.exists(self.since):
            from .delta import filter_changed_files, get_delta, format_delta_summary
            all_files = self._collect_all_files()
            files_to_assemble, self.deleted_files = filter_changed_files(self.since, all_files)
            self.since_filter = files_to_assemble

            modified, added, deleted = get_delta(self.since, all_files)
            delta_summary = format_delta_summary(modified, added, deleted)

            if self.config.show_progress:
                print(f"\n{EMOJI['mag']} Delta mode: {len(files_to_assemble)} file(s) changed")

        if self.config.show_progress:
            print(f"\n{EMOJI['rocket']} Starting assembly...\n")

        for path in self.config.paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                if self._matches_file(Path(path)):
                    self.process_file(path)
            elif os.path.isdir(path):
                self.process_directory(path)

        # Finalize statistics and formatting
        full_content = "".join(self.content_buffer)
        self.stats.total_chars = len(full_content)
        self.stats.estimated_tokens = estimate_tokens(full_content)

        toc = self.formatter.generate_toc(self.toc_entries)
        analyzer = ArchitectureAnalyzer(self.toc_entries, self.stats)
        archi_data = analyzer.analyze_data()
        architecture_md = self.formatter.render("components/architecture.md.j2", archi_data)

        # Generate Header with optional delta summary
        header = self.formatter.generate_header(self.stats, self.config, toc, architecture_md)
        if delta_summary:
            header = header.replace("---", f"{delta_summary}\n\n---", 1)

        # Generate hidden metadata for future delta analysis
        metadata_block = self.formatter.generate_metadata_block(self.toc_entries)

        if self.config.show_progress:
            self._print_summary()

        return header + "\n\n" + full_content + metadata_block

    def _print_summary(self) -> None:
        """Print assembly summary to console."""
        from .utils import format_file_size, format_number
        print(f"\n{EMOJI['success']} Assembly completed!")
        print(f"\n{EMOJI['chart']} Summary:")
        print(f"   {EMOJI['file']} Files: {format_number(self.stats.total_files)}")
        print(f"   {EMOJI['mag']} Lines: {format_number(self.stats.total_lines)}")
        print(f"   {EMOJI['floppy']} Size: {format_file_size(self.stats.total_chars)}")
        print(f"   {EMOJI['target']} Tokens: ~{format_number(self.stats.estimated_tokens)}")


def assemble_codebase(
        paths: List[str],
        extensions: List[str],
        exclude_patterns: Optional[List[str]] = None,
        output: str = "codebase.md",
        since: Optional[str] = None,
        **kwargs
) -> str:
    """Main entry point function to assemble a codebase."""
    from .file_io import write_file_content

    if 'output_file' in kwargs:
        output = kwargs.pop('output_file')

    config = AssemblerConfig(
        paths=paths, extensions=extensions,
        exclude_patterns=exclude_patterns or [],
        output_file=output, **kwargs
    )

    assembler = CodebaseAssembler(config, since=since)
    content = assembler.assemble()
    write_file_content(output, content)

    if config.show_progress:
        print(f"\n{EMOJI['floppy']} Saved: {output}\n")

    return content


def assemble_from_config(config_file: str, since: Optional[str] = None) -> str:
    """Assemble codebase using a JSON configuration file."""
    import json
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    if 'output_file' in config_data and 'output' not in config_data:
        config_data['output'] = config_data.pop('output_file')
    elif 'output_file' in config_data:
        config_data.pop('output_file')

    return assemble_codebase(since=since, **config_data)

```

### `src\code_assembler\delta.py`

```python
"""
Delta analysis engine for Code Assembler Pro.

This module provides the logic to compare the current state of a codebase
against a previously generated Markdown snapshot. It enables "incremental"
updates by identifying which files have been modified, added, or deleted
since the last assembly.

Key Features:
    * Metadata Extraction: Reads hidden JSON metadata embedded in Markdown
      snapshots to ensure 100% accuracy in file identification.
    * Path Normalization: Handles cross-platform path differences (Windows
      backslashes vs. POSIX slashes) and case sensitivity.
    * Change Detection: Compares modification timestamps (mtime) while
      ignoring seconds to match the granularity of the stored metadata.
    * Delta Reporting: Generates human-readable summaries of changes for
      inclusion in the document header.

The delta engine is designed to be robust against duplicate filenames
by using relative paths as unique keys, reconstructed from the execution
root (CWD).
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Tuple

# Regex simple pour extraire le bloc JSON
_METADATA_RE = re.compile(r'<!-- CODE_ASSEMBLER_METADATA\s+(.*?)\s+-->', re.DOTALL)


def extract_metadata(md_file: str) -> Dict[str, datetime]:
    """Extrait le dictionnaire {chemin: date} du bloc caché."""
    result = {}
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        match = _METADATA_RE.search(content)
        if match:
            data = json.loads(match.group(1))
            for path, date_str in data.get('files', {}).items():
                try:
                    result[path] = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
    except Exception:
        pass  # Fichier illisible ou pas de métadonnées
    return result


def normalize_key(path: str) -> str:
    """Normalise un chemin (minuscules + slashs)."""
    return str(Path(path)).replace('\\', '/').lower().strip('/')


def get_delta(md_file: str, current_files: Set[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    # 1. Charger le snapshot (Fiable à 100%)
    snapshot = extract_metadata(md_file)

    # Si pas de métadonnées (vieux fichier), on renvoie tout comme "Nouveau"
    if not snapshot:
        return set(current_files), set(current_files), set()

    modified = set()
    added = set()
    deleted = set()
    matched_keys = set()

    # 2. Calculer la racine commune des fichiers actuels
    if current_files:
        try:
            common_root = os.path.commonpath(list(current_files))
            if os.path.isfile(common_root): common_root = os.path.dirname(common_root)
        except ValueError:
            common_root = os.getcwd()
    else:
        common_root = os.getcwd()

    # 3. Comparaison
    for abs_path in current_files:
        # Calcul chemin relatif
        try:
            rel_path = os.path.relpath(abs_path, common_root).replace('\\', '/')
            if rel_path.startswith('./'): rel_path = rel_path[2:]
        except ValueError:
            rel_path = normalize_key(abs_path)

        # On cherche une correspondance (Exacte ou Suffixe)
        match_key = None

        # Test exact
        if rel_path in snapshot:
            match_key = rel_path
        else:
            # Test suffixe (pour gérer les différences de racine src/ vs ./)
            for snap_key in snapshot:
                if rel_path.endswith(snap_key) or snap_key.endswith(rel_path):
                    if Path(rel_path).name == Path(snap_key).name:
                        match_key = snap_key
                        break

        if match_key:
            matched_keys.add(match_key)
            if _has_changed(abs_path, snapshot[match_key]):
                modified.add(abs_path)
        else:
            added.add(abs_path)

    # 4. Suppressions
    for snap_key in snapshot:
        if snap_key not in matched_keys:
            deleted.add(snap_key)

    return modified, added, deleted


def _has_changed(abs_path: str, snapshot_dt: datetime) -> bool:
    try:
        current_mtime = datetime.fromtimestamp(os.path.getmtime(abs_path)).replace(second=0, microsecond=0)
        snapshot_mtime = snapshot_dt.replace(second=0, microsecond=0)
        return current_mtime != snapshot_mtime
    except OSError:
        return True


def filter_changed_files(md_file: str, all_files: Set[str]) -> Tuple[Set[str], Set[str]]:
    modified, added, deleted = get_delta(md_file, all_files)
    return modified | added, deleted


def format_delta_summary(modified: Set[str], added: Set[str], deleted: Set[str]) -> str:
    lines = []

    def _fmt(files, label, icon):
        if not files: return
        count = len(files)
        names = sorted(Path(p).name for p in files)
        disp = ', '.join(names[:5]) + (f", ... (+{count - 5})" if count > 5 else "")
        lines.append(f"> {icon} {label} ({count}): {disp}")

    _fmt(modified, "Modified", "✏️ ")
    _fmt(added, "Added", "➕")
    _fmt(deleted, "Deleted", "❌")

    if not lines: lines.append("> ✅ No changes detected since last snapshot")
    return '\n'.join(lines)

```

### `src\code_assembler\file_io.py`

```python
"""
File I/O operations for Code Assembler Pro.

This module handles all file reading and encoding detection operations.
"""

from typing import Optional

import chardet


def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file with intelligent fallback.
    Reads only a sample (64KB) to avoid loading huge files into memory.
    """
    SAMPLE_SIZE = 65536  # 64KB is enough for reliable detection

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(SAMPLE_SIZE)
        return 'utf-8'
    except UnicodeDecodeError:
        pass
    except FileNotFoundError:
        raise

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(SAMPLE_SIZE)
            result = chardet.detect(raw_data)
            detected_encoding = result.get('encoding')
            return detected_encoding if detected_encoding else 'utf-8'
    except Exception:
        return 'utf-8'


def read_file_content(file_path: str, encoding: Optional[str] = None) -> str:
    """
    Read the content of a file with automatic encoding detection.
    """
    try:
        if encoding is None:
            encoding = detect_encoding(file_path)

        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            return f.read()

    except FileNotFoundError:
        return f"[ERROR] File not found: {file_path}"
    except PermissionError:
        return f"[ERROR] Permission denied: {file_path}"
    except Exception as e:
        return f"[ERROR] Error reading file: {str(e)}"


def write_file_content(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Write content to a file.
    """
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[ERROR] Error writing file {file_path}: {e}")
        return False


def read_file_head(file_path: str, max_lines: int, encoding: Optional[str] = None) -> str:
    """
    Read only the first N lines of a file.
    """
    if encoding is None:
        encoding = detect_encoding(file_path)

    lines = []
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
        return "".join(lines)
    except Exception as e:
        return f"[ERROR] Error reading file head: {str(e)}"

```

### `src\code_assembler\formatters.py`

```python
"""
Markdown formatters for Code Assembler Pro using Jinja2 templates.

This module handles the transformation of analyzed codebase data into
structured Markdown, including the generation of a hidden metadata block
for delta analysis.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader

from .config import FileEntry, CodebaseStats, AssemblerConfig
from .constants import LANGUAGE_MAP, EMOJI, __version__
from .utils import slugify_path, format_file_size, format_number


class MarkdownFormatter:
    """Handles formatting of content into Markdown using Jinja2."""

    def __init__(self):
        """Initialize Jinja2 environment and global variables."""
        template_dir = Path(__file__).parent / "templates"

        if not template_dir.exists():
            raise FileNotFoundError(
                f"Templates directory not found: {template_dir}\n"
                f"If installed via .whl, ensure templates are included in package_data."
            )

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        self.env.globals.update({
            "format_number": format_number,
            "format_file_size": format_file_size,
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": __version__,
            "emoji": EMOJI
        })

    def render(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Helper to render a template with data.

        Args:
            template_name: Name of the .j2 template file.
            data: Dictionary of variables for the template.
        """
        template = self.env.get_template(template_name)
        return template.render(**data)

    def _detect_language(self, file_path: str) -> str:
        """
        Detect the programming language for syntax highlighting.
        Checks extensions first, then falls back to exact filenames.
        """
        path_obj = Path(file_path)
        ext = path_obj.suffix.lower()
        filename = path_obj.name.lower()

        # 1. Try by extension
        lang = LANGUAGE_MAP.get(ext, "text")

        # 2. Fallback for special filenames if lang is still 'text'
        if lang == "text":
            if filename == "dockerfile":
                lang = "dockerfile"
            elif filename == "makefile":
                lang = "makefile"
            elif filename == "procfile":
                lang = "ruby"
            elif filename.startswith(".env"):
                lang = "bash"
            elif filename == "cmakelists.txt":
                lang = "cmake"

        return lang

    def format_file_block(self, file_path: str, content: str, depth: int = 0,
                          size_bytes: int = 0, line_count: int = 0) -> str:
        """Format a file's content using the file_block template."""
        lang = self._detect_language(file_path)  # Utilisation de la nouvelle méthode

        data = {
            "header_level": "#" * (2 + depth),
            "filename": Path(file_path).name,
            "anchor": slugify_path(file_path),
            "path": file_path,
            "size": format_file_size(size_bytes),
            "lines": format_number(line_count),
            "lang": lang,
            "content": content
        }
        return self.render("components/file_block.md.j2", data)

    def format_directory_header(self, dir_path: str, depth: int = 0) -> str:
        """Format a directory header."""
        header_level = "#" * (1 + depth)
        dirname = Path(dir_path).name
        return f'{header_level} `{dirname}/`\n\n'

    def format_readme_context(self, readme_content: str, depth: int = 0) -> str:
        """Format README content using the readme_context template."""
        data = {
            "header_level": "#" * (1 + depth),
            "content": readme_content
        }
        return self.render("components/readme_context.md.j2", data)

    def generate_toc(self, entries: List[FileEntry]) -> str:
        """Generate table of contents using the toc template."""
        toc_data = []
        for e in entries:
            mtime = ""
            if e.is_file:
                try:
                    mtime = datetime.fromtimestamp(
                        os.path.getmtime(e.path)
                    ).strftime("%Y-%m-%d %H:%M")
                except OSError:
                    mtime = ""

            toc_data.append({
                "depth": e.depth,
                "is_directory": e.is_directory,
                "is_file": e.is_file,
                "name": e.name,
                "anchor": slugify_path(e.path),
                "size": format_file_size(e.size_bytes) if e.is_file else "",
                "lines": format_number(e.line_count) if e.is_file else "",
                "mtime": mtime,
            })

        return self.render("components/toc.md.j2", {"entries": toc_data})

    def generate_stats_table(self, stats: CodebaseStats, config: AssemblerConfig) -> str:
        """Generate statistics table using the stats_table template."""
        largest_file_name = "N/A"
        largest_file_size = "N/A"

        if stats.largest_file:
            largest_file_name = Path(stats.largest_file[0]).name
            largest_file_size = format_file_size(stats.largest_file[1])

        clean_extensions = sorted(list(set(
            ext.replace('*', '').lstrip('.') for ext in config.extensions
        )))

        data = {
            "total_files": format_number(stats.total_files),
            "total_lines": format_number(stats.total_lines),
            "total_chars": format_number(stats.total_chars),
            "estimated_tokens": format_number(stats.estimated_tokens),
            "extensions": clean_extensions,
            "largest_file_name": largest_file_name,
            "largest_file_size": largest_file_size,
            "max_depth": stats.max_depth,
            "paths": config.paths,
            "exclude_patterns": config.exclude_patterns[:10],
            "skipped_count": len(stats.skipped_files)
        }
        return self.render("components/stats_table.md.j2", data)

    def generate_header(self, stats: CodebaseStats, config: AssemblerConfig, toc: str, arch_md: str) -> str:
        """Generate complete document header using the main_header template."""
        data = {
            "now_short": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "toc": toc,
            "architecture": arch_md,
            "total_files": format_number(stats.total_files),
            "estimated_tokens": format_number(stats.estimated_tokens),
            "skipped_count": len(stats.skipped_files),
            "stats_table": self.generate_stats_table(stats, config)
        }
        return self.render("main_header.md.j2", data)

    def generate_metadata_block(self, entries: List[FileEntry]) -> str:
        """
        Generate a hidden JSON metadata block at the end of the Markdown file.

        This block stores exact relative paths (relative to the current working directory)
        and modification times. Using the CWD ensures path consistency across
        full and partial (delta) assembly runs.
        """
        meta_files = {}

        # Use Current Working Directory as the stable root for all relative paths
        common_root = os.getcwd()

        for e in entries:
            if e.is_file:
                try:
                    # Calculate path relative to the execution root
                    # We normalize to forward slashes for cross-platform compatibility
                    rel_path = os.path.relpath(e.path, common_root).replace('\\', '/')

                    # Get modification time formatted to the minute (matching TOC display)
                    mtime = datetime.fromtimestamp(
                        os.path.getmtime(e.path)
                    ).strftime("%Y-%m-%d %H:%M")

                    meta_files[rel_path] = mtime
                except (OSError, ValueError):
                    # Skip files that cannot be accessed or are on different drives (Windows)
                    continue

        metadata = {
            "version": __version__,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "files": meta_files
        }

        # Wrap the JSON string in an HTML comment to keep it invisible in UI/Renderers
        # indent=2 makes it readable for debugging in raw text mode
        return f"\n\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(metadata, indent=2)}\n-->"

```

### `src\code_assembler\interactive.py`

```python
"""
Interactive wizard mode for Code Assembler Pro.

This module provides a user-friendly interactive interface for configuring
and running the assembler without memorizing CLI arguments.
"""

import os
from typing import List, Optional, Dict, Any

from .constants import LANGUAGE_MAP, DEFAULT_EXCLUDE_PATTERNS, EMOJI
from .core import assemble_codebase


class InteractiveWizard:
    """
    Interactive configuration wizard for Code Assembler Pro.

    Guides users through the configuration process with smart defaults
    and contextual help.
    """

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.available_extensions = self._get_available_extensions()

    def _get_available_extensions(self) -> List[str]:
        """Get list of supported extensions from LANGUAGE_MAP."""
        return sorted(list(set(LANGUAGE_MAP.keys())))

    def _print_banner(self):
        """Print welcome banner."""
        print("\n" + "=" * 70)
        print(f"{EMOJI['rocket']}  Code Assembler Pro - Interactive Mode")
        print("=" * 70)
        print("\nWelcome! This wizard will help you configure your codebase assembly.")
        print("Press Ctrl+C at any time to cancel.\n")

    def _print_section(self, title: str):
        """Print section header."""
        print(f"\n{EMOJI['target']} {title}")
        print("-" * 70)

    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """
        Ask a yes/no question.

        Args:
            question: Question to ask
            default: Default answer if user just presses Enter

        Returns:
            True for yes, False for no
        """
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{question} [{default_str}]: ").strip().lower()

            if not response:
                return default

            if response in ['y', 'yes', 'oui']:
                return True
            elif response in ['n', 'no', 'non']:
                return False
            else:
                print(f"{EMOJI['warning']}  Please answer 'y' or 'n'")

    def _ask_number(self, question: str, default: float, min_val: float = 0.0) -> float:
        """
        Ask for a number with validation.

        Args:
            question: Question to ask
            default: Default value
            min_val: Minimum allowed value

        Returns:
            User's number or default
        """
        while True:
            response = input(f"{question} [default: {default}]: ").strip()

            if not response:
                return default

            try:
                value = float(response)
                if value < min_val:
                    print(f"{EMOJI['warning']}  Value must be >= {min_val}")
                    continue
                return value
            except ValueError:
                print(f"{EMOJI['warning']}  Please enter a valid number")

    def _ask_text(self, question: str, default: str = "") -> str:
        """
        Ask for text input.

        Args:
            question: Question to ask
            default: Default value

        Returns:
            User's input or default
        """
        if default:
            response = input(f"{question} [default: {default}]: ").strip()
            return response if response else default
        else:
            response = input(f"{question}: ").strip()
            return response

    def _select_paths(self) -> List[str]:
        """Interactive path selection."""
        self._print_section("Step 1: Select Paths to Analyze")

        print("\nYou can analyze:")
        print("  1. Current directory (.)")
        print("  2. Specific directory/directories")
        print("  3. Specific files")

        paths = []

        choice = input("\nYour choice [1-3]: ").strip()

        if choice == "1":
            paths = ["."]
            print(f"{EMOJI['success']} Selected: current directory")

        elif choice == "2":
            print("\nEnter directory paths (one per line, empty line to finish):")
            while True:
                path = input("  Path: ").strip()
                if not path:
                    break

                if os.path.exists(path):
                    if os.path.isdir(path):
                        paths.append(path)
                        print(f"  {EMOJI['success']} Added: {path}")
                    else:
                        print(f"  {EMOJI['warning']}  '{path}' is not a directory")
                else:
                    print(f"  {EMOJI['warning']}  '{path}' does not exist")

        elif choice == "3":
            print("\nEnter file paths (one per line, empty line to finish):")
            while True:
                path = input("  File: ").strip()
                if not path:
                    break

                if os.path.exists(path) and os.path.isfile(path):
                    paths.append(path)
                    print(f"  {EMOJI['success']} Added: {path}")
                else:
                    print(f"  {EMOJI['warning']}  '{path}' is not a valid file")

        if not paths:
            print(f"{EMOJI['warning']}  No paths selected, using current directory")
            paths = ["."]

        return paths

    def _select_extensions(self) -> List[str]:
        """Interactive extension selection."""
        self._print_section("Step 2: Select File Extensions")

        print("\nCommon presets:")
        presets = {
            "1": ([".py"], "Python projects"),
            "2": ([".py", ".md", ".toml", ".yaml"], "Python + Config + Docs"),
            "3": ([".js", ".ts", ".jsx", ".tsx"], "JavaScript/TypeScript"),
            "4": ([".rs", ".toml"], "Rust projects"),
            "5": ([".go", ".mod"], "Go projects"),
            "6": ([".java"], "Java projects"),
            "7": ([".c", ".cpp", ".h", ".hpp"], "C/C++ projects"),
        }

        for key, (exts, desc) in presets.items():
            print(f"  {key}. {desc} ({', '.join(exts)})")
        print("  8. Custom selection")

        choice = input("\nYour choice [1-8]: ").strip()

        if choice in presets:
            extensions, desc = presets[choice]
            print(f"{EMOJI['success']} Selected: {desc}")
            return extensions

        # Custom selection
        print("\nAvailable extensions:")
        for i, ext in enumerate(self.available_extensions, 1):
            lang = LANGUAGE_MAP.get(ext, "unknown")
            print(f"  {ext:12} ({lang})", end="")
            if i % 4 == 0:
                print()
        print()

        print("\nEnter extensions separated by spaces (e.g., .py .js .md):")
        extensions_input = input("Extensions: ").strip()

        extensions = []
        for ext in extensions_input.replace(',', ' ').split():
            ext = ext.strip().rstrip(',')  # double sécurité
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.append(ext)

        if not extensions:
            print(f"{EMOJI['warning']}  No extensions selected, using .py as default")
            extensions = [".py"]

        return extensions

    def _configure_exclusions(self) -> List[str]:
        """Configure exclusion patterns."""
        self._print_section("Step 3: Configure Exclusions")

        print("\nDefault exclusions:")
        print(f"  {', '.join(DEFAULT_EXCLUDE_PATTERNS[:10])}")
        if len(DEFAULT_EXCLUDE_PATTERNS) > 10:
            print(f"  ... and {len(DEFAULT_EXCLUDE_PATTERNS) - 10} more")

        use_defaults = self._ask_yes_no("\nUse default exclusions?", default=True)

        custom_patterns = []

        if self._ask_yes_no("Add custom exclusion patterns?", default=False):
            print("\nEnter patterns (one per line, empty line to finish):")
            print("Examples: tests/, *.log, secret.py, temp_*")
            while True:
                pattern = input("  Pattern: ").strip()
                if not pattern:
                    break
                custom_patterns.append(pattern)
                print(f"  {EMOJI['success']} Added: {pattern}")

        if use_defaults:
            return list(set(DEFAULT_EXCLUDE_PATTERNS + custom_patterns))
        else:
            return custom_patterns

    def _configure_output(self) -> str:
        """Configure output filename."""
        self._print_section("Step 4: Output Configuration")

        default_name = "codebase.md"
        output = self._ask_text(f"\nOutput filename", default=default_name)

        if not output.endswith('.md'):
            output += '.md'

        # Check if file exists
        if os.path.exists(output):
            if not self._ask_yes_no(f"{EMOJI['warning']}  '{output}' already exists. Overwrite?", default=False):
                counter = 1
                while os.path.exists(f"codebase_{counter}.md"):
                    counter += 1
                output = f"codebase_{counter}.md"
                print(f"{EMOJI['success']} Using: {output}")

        return output

    def _configure_advanced(self) -> Dict[str, Any]:
        """Configure advanced options."""
        self._print_section("Step 5: Advanced Options")

        advanced = {}

        if self._ask_yes_no("\nConfigure advanced options?", default=False):

            advanced['recursive'] = self._ask_yes_no(
                "  Recursively traverse subdirectories?",
                default=True
            )

            advanced['include_readmes'] = self._ask_yes_no(
                "  Automatically include README files?",
                default=True
            )

            print("\n  File size handling:")
            advanced['max_file_size_mb'] = self._ask_number(
                "    Maximum file size (MB)",
                default=10.0,
                min_val=0.1
            )

            advanced['truncate_large_files'] = self._ask_yes_no(
                "    Truncate large files instead of skipping?",
                default=True
            )

            if advanced['truncate_large_files']:
                advanced['truncation_limit_lines'] = int(self._ask_number(
                    "      Keep first N lines when truncating",
                    default=500,
                    min_val=10
                ))
        else:
            # Use sensible defaults
            advanced = {
                'recursive': True,
                'include_readmes': True,
                'max_file_size_mb': 10.0,
                'truncate_large_files': True,
                'truncation_limit_lines': 500,
            }

        advanced['show_progress'] = True

        return advanced

    def _show_summary(self):
        """Display configuration summary."""
        self._print_section("Configuration Summary")

        print(f"\n{EMOJI['folder']} Paths: {', '.join(self.config['paths'])}")
        print(f"{EMOJI['memo']} Extensions: {', '.join(self.config['extensions'])}")
        print(f"{EMOJI['floppy']} Output: {self.config['output']}")
        print(f"{EMOJI['recycle']} Recursive: {self.config.get('recursive', True)}")
        print(f"{EMOJI['book']} Include READMEs: {self.config.get('include_readmes', True)}")
        print(f"{EMOJI['mag']} Max file size: {self.config.get('max_file_size_mb', 10.0)} MB")
        print(f"{EMOJI['warning']}  Truncate large files: {self.config.get('truncate_large_files', True)}")

        if self.config.get('truncate_large_files'):
            print(f"   Keep first {self.config.get('truncation_limit_lines', 500)} lines")

        if self.config.get('exclude_patterns'):
            print(f"\n{EMOJI['error']} Exclusions: {len(self.config['exclude_patterns'])} patterns")
            if len(self.config['exclude_patterns']) <= 5:
                for pattern in self.config['exclude_patterns']:
                    print(f"   - {pattern}")
            else:
                for pattern in self.config['exclude_patterns'][:5]:
                    print(f"   - {pattern}")
                print(f"   ... and {len(self.config['exclude_patterns']) - 5} more")

    def _save_config(self):
        """Optionally save configuration to JSON."""
        if self._ask_yes_no(f"\n{EMOJI['floppy']} Save this configuration for future use?", default=False):
            import json

            config_name = self._ask_text("Configuration filename", default="assembler_config.json")
            if not config_name.endswith('.json'):
                config_name += '.json'

            # Prepare config for JSON (remove runtime flags)
            save_config = {k: v for k, v in self.config.items() if k != 'show_progress'}

            with open(config_name, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=2, ensure_ascii=False)

            print(f"{EMOJI['success']} Configuration saved to: {config_name}")
            print(f"   Reuse it with: code-assembler --config {config_name}")

    def run(self) -> Optional[str]:
        """
        Run the interactive wizard.

        Returns:
            Generated markdown content, or None if cancelled
        """
        try:
            self._print_banner()

            # Step 1: Paths
            self.config['paths'] = self._select_paths()

            # Step 2: Extensions
            self.config['extensions'] = self._select_extensions()

            # Step 3: Exclusions
            exclude_patterns = self._configure_exclusions()
            if exclude_patterns:
                self.config['exclude_patterns'] = exclude_patterns

            # Step 4: Output
            self.config['output'] = self._configure_output()

            # Step 5: Advanced options
            advanced = self._configure_advanced()
            self.config.update(advanced)

            # Summary
            self._show_summary()

            # Confirm
            if not self._ask_yes_no(f"\n{EMOJI['rocket']} Start assembly?", default=True):
                print(f"\n{EMOJI['error']} Assembly cancelled.")
                return None

            # Save config option
            self._save_config()

            # Run assembly
            print(f"\n{EMOJI['rocket']} Starting assembly...\n")

            content = assemble_codebase(**self.config)

            print(f"\n{EMOJI['success']} Assembly completed successfully!")
            print(f"{EMOJI['file']} Output file: {self.config['output']}")

            return content

        except KeyboardInterrupt:
            print(f"\n\n{EMOJI['error']} Wizard cancelled by user.")
            return None
        except Exception as e:
            print(f"\n{EMOJI['error']} An error occurred: {e}")
            import traceback
            traceback.print_exc()
            return None


def run_interactive_mode():
    """
    Entry point for interactive mode.

    Usage:
        code-assembler --interactive
        or
        python -m code_assembler.interactive
    """
    wizard = InteractiveWizard()
    wizard.run()


if __name__ == "__main__":
    run_interactive_mode()

```

### `src\code_assembler\rebuilder.py`

```python
"""
Rebuilder module for Code Assembler Pro.

This module reconstructs a project's directory structure and file contents
from a generated Markdown snapshot, using the embedded JSON metadata.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CodebaseRebuilder:
    """Handles the reconstruction of files from a Markdown codebase."""

    def __init__(self, md_path: str, output_dir: str, dry_run: bool = False):
        self.md_path = Path(md_path)
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.metadata: Dict = {}
        self.md_content: str = ""

    def _extract_metadata(self) -> bool:
        """Extract the hidden JSON metadata from the Markdown file."""
        if not self.md_path.exists():
            return False

        self.md_content = self.md_path.read_text(encoding='utf-8')
        pattern = re.compile(r'<!-- CODE_ASSEMBLER_METADATA\s+(.*?)\s+-->', re.DOTALL)
        match = pattern.search(self.md_content)

        if not match:
            return False

        try:
            self.metadata = json.loads(match.group(1))
            return True
        except json.JSONDecodeError:
            return False

    def _extract_file_content(self, rel_path: str) -> Optional[str]:
        """
        Find and extract the content of a specific file from the Markdown.
        Robust against path separators and blank lines.
        """
        # Normaliser le chemin pour la recherche (accepte / et \)
        normalized_search = re.escape(rel_path).replace(r'\/', r'[\\\/]').replace(r'/', r'[\\\/]')

        # Regex améliorée :
        # \s* après le header pour absorber les lignes vides
        # [a-z0-9]* pour le langage du bloc
        pattern = re.compile(
            rf'#+ `.*?{normalized_search}`.*?\s+```[a-z0-9]*\n(.*?)\n```',
            re.DOTALL | re.IGNORECASE
        )

        match = pattern.search(self.md_content)
        return match.group(1) if match else None

    def rebuild(self) -> Tuple[int, List[str]]:
        """
        Execute the reconstruction process.

        Returns:
            Tuple[int, List[str]]: (number of files created, list of errors)
        """
        if not self._extract_metadata():
            return 0, ["No valid metadata found in the Markdown file. Rebuild impossible."]

        files_to_rebuild = self.metadata.get("files", {})
        created_count = 0
        errors = []

        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        for rel_path in files_to_rebuild:
            content = self._extract_file_content(rel_path)

            if content is None:
                errors.append(f"Content not found for: {rel_path}")
                continue

            # Security: Prevent path traversal
            if ".." in rel_path or rel_path.startswith("/") or rel_path.startswith("\\"):
                errors.append(f"Security skip (invalid path): {rel_path}")
                continue

            target_path = self.output_dir / rel_path

            if self.dry_run:
                print(f"[DRY-RUN] Would create: {target_path}")
                created_count += 1
                continue

            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content, encoding='utf-8')

                # Check for truncation warning
                if "[TRUNCATED]" in content:
                    errors.append(f"Warning: {rel_path} was truncated in the source MD.")

                created_count += 1
            except Exception as e:
                errors.append(f"Failed to write {rel_path}: {str(e)}")

        return created_count, errors

```

## `templates/`

### `components/`

##### `src\code_assembler\templates\components\architecture.md.j2`

```jinja2
## Architecture

**Components:**
{% for comp in components %}
- `{{ comp.name }}/` ({{ comp.count }} file{{ 's' if comp.count > 1 else '' }})
{% endfor %}

**File types:**
{% for item in distribution %}
- `{{ item.ext }}` ({{ item.lang }}): {{ item.count }} — {{ item.percentage }}%
{% endfor %}

```

##### `src\code_assembler\templates\components\file_block.md.j2`

```jinja2
{{ header_level }} `{{ path }}`

```{{ lang }}
{{ content }}
```


```

##### `src\code_assembler\templates\components\readme_context.md.j2`

```jinja2
{{ header_level }} README context

{{ content }}

---

```

##### `src\code_assembler\templates\components\stats_table.md.j2`

```jinja2
## Stats

**{{ total_files }}** files | **{{ total_lines }}** lines | ~**{{ estimated_tokens }}** tokens | Extensions: {{ extensions | join(', ') }}
{% if skipped_count > 0 %}
Skipped: {{ skipped_count }} file(s)
{% endif %}

```

##### `src\code_assembler\templates\components\toc.md.j2`

```jinja2
## Table of Contents

{% for entry in entries %}
{{ "  " * entry.depth }}- {% if entry.is_directory %}`{{ entry.name }}/`{% else %}`{{ entry.name }}` | {{ entry.mtime }}{% endif %}

{% endfor %}
```

#### `src\code_assembler\templates\main_header.md.j2`

```jinja2
# Consolidated Codebase

> **Snapshot:** {{ now_short }} | **Files:** {{ total_files }} | **Tokens:** ~{{ estimated_tokens }}
{% if delta_summary %}
{{ delta_summary }}
{% endif %}

---

{{ toc }}

---

{{ architecture }}

---

{{ stats_table }}

---

{{ total_files }} source files follow below.

---

```

### `src\code_assembler\utils.py`

```python
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

```

## `examples\__init__.py`

```python

```

## `examples\advanced_config.py`

```python
"""
Advanced programmatic usage: JSON configuration and Delta Mode.
This script simulates a real-world workflow: Full assembly followed by an incremental update.
"""
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from code_assembler import assemble_from_config

def run_advanced_demo():
    root = Path(__file__).resolve().parents[1]
    config_path = "demo_config.json"
    output_md = "advanced_snapshot.md"

    # 1. Define a complex configuration
    config = {
        "paths": [str(root / "src")],
        "extensions": [".py", ".j2", "Dockerfile"],
        "output": output_md,
        "exclude_patterns": ["__pycache__", "tests"],
        "truncate_large_files": True,
        "truncation_limit_lines": 100,
        "show_progress": True
    }

    with open(config_path, "w", encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print("--- STEP 1: Full Project Assembly ---")
    assemble_from_config(config_path)

    print("\n" + "="*40)
    print("--- STEP 2: Delta Mode (Incremental) ---")
    print("Only files modified since Step 1 will be included.")

    # We use the 'since' parameter to trigger Delta Mode
    assemble_from_config(config_path, since=output_md)

    # Cleanup
    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"\n🧹 Temporary config {config_path} cleaned.")

if __name__ == "__main__":
    run_advanced_demo()
```

## `examples\basic_usage.py`

```python
"""
Basic programmatic usage of Code Assembler Pro.
Demonstrates how to consolidate code and get the result as a string.
"""
import os
import sys
from pathlib import Path

# Setup path to find code_assembler if not installed via pip
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent / "src"))

from code_assembler import assemble_codebase


def run_demo():
    # On se place mentalement à la racine du projet
    project_root = Path(__file__).resolve().parents[1]

    # On change le répertoire de travail pour que les chemins dans le MD soient propres (src/...)
    os.chdir(project_root)

    print(f"🚀 Assembling context from: src/code_assembler")

    markdown_content = assemble_codebase(
        paths=["src/code_assembler"],  # Chemin relatif propre
        extensions=[".py"],
        output="simple_snapshot.md",
        show_progress=True
    )

if __name__ == "__main__":
    run_demo()
```

## `examples\interactive_demo.py`

```python
"""
Interactive mode demonstration for Code Assembler Pro.

This script shows how to launch the interactive wizard programmatically.
"""
import sys
from pathlib import Path

# Setup path
current_file = Path(__file__).resolve()
project_root = current_file.parents[1]
sys.path.append(str(project_root / "src"))

try:
    from code_assembler import run_interactive_mode
except ImportError:
    print("❌ Error: Could not import 'code_assembler'.")
    sys.exit(1)

if __name__ == "__main__":
    print("=" * 70)
    print("  Code Assembler Pro - Interactive Demo")
    print("=" * 70)
    print("\nThis will launch the interactive wizard.")
    print("You'll be guided through all configuration steps.\n")

    input("Press Enter to start... ")

    # Launch the wizard
    run_interactive_mode()
```

## `examples\rebuild_usage.py`

```python
"""
Rebuild Engine Demo (New in v4.4).
Demonstrates how to reconstruct a project structure from a Markdown snapshot.
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from code_assembler.rebuilder import CodebaseRebuilder

def run_rebuild_demo():
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)
    # 1. We need a source Markdown file with metadata
    # (Run basic_usage.py first to generate 'simple_snapshot.md')
    md_input = "simple_snapshot.md"
    target_dir = "./reconstructed_project"

    if not Path(md_input).exists():
        print(f"❌ Error: '{md_input}' not found.")
        print("Please run 'python basic_usage.py' first to generate a snapshot.")
        return

    print(f"🏗️  Starting reconstruction into: {target_dir}")

    # 2. Initialize the Rebuilder
    rebuilder = CodebaseRebuilder(
        md_path=md_input,
        output_dir=target_dir,
        dry_run=False  # Set to True to preview without writing
    )

    # 3. Execute Rebuild
    count, errors = rebuilder.rebuild()

    if errors:
        print(f"\n⚠️  Rebuild completed with {len(errors)} warnings:")
        for err in errors:
            print(f"   - {err}")

    print(f"\n✅ Done! {count} files reconstructed successfully.")

if __name__ == "__main__":
    run_rebuild_demo()
```

## `tests\__init__.py`

```python

```

## `tests\test_clipboard.py`

```python
"""
Tests for clipboard functionality.
"""
import unittest
import sys
import argparse
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.utils import copy_to_clipboard
from code_assembler.cli import main

class TestClipboard(unittest.TestCase):

    @patch('subprocess.run')
    def test_copy_to_clipboard_windows(self, mock_run):
        """Test clipboard call on Windows using PowerShell with UTF8 forced input."""
        with patch('platform.system', return_value='Windows'):
            test_text = "test content with emoji 🚀"
            result = copy_to_clipboard(test_text)

            self.assertTrue(result)
            # Vérifie la commande complexe et l'encodage utf-8
            mock_run.assert_called_once_with(
                [
                    "powershell", "-NoProfile", "-Command",
                    "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
                    "$input | Out-String | Set-Clipboard"
                ],
                input=test_text,
                encoding='utf-8',
                check=True
            )

    @patch('subprocess.run')
    def test_copy_to_clipboard_mac(self, mock_run):
        """Test clipboard call on macOS using pbcopy."""
        with patch('platform.system', return_value='Darwin'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            mock_run.assert_called_once_with(
                "pbcopy", input="test content", text=True, check=True
            )

    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xclip(self, mock_run):
        """Test clipboard call on Linux using xclip."""
        with patch('platform.system', return_value='Linux'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            mock_run.assert_called_with(
                ["xclip", "-selection", "clipboard"],
                input="test content", text=True, check=True
            )

    @patch('code_assembler.cli.parse_args')
    @patch('code_assembler.cli.assemble_codebase')
    @patch('code_assembler.utils.copy_to_clipboard')
    def test_cli_calls_clipboard(self, mock_copy, mock_assemble, mock_parse):
        """Test that CLI triggers clipboard copy when --clip is set."""

        # Configuration d'un Namespace complet
        args = argparse.Namespace(
            clip=True,
            paths=["src"],
            extensions=[".py"],
            interactive=False,
            config=None,
            rebuild=None,
            show_excludes=False,
            save_config=None,
            output="codebase.md",
            exclude_patterns=[],
            recursive=True,
            include_readmes=True,
            use_default_excludes=True,
            max_size=10.0,
            since=None
        )
        mock_parse.return_value = args

        mock_assemble.return_value = "# Generated Content"
        mock_copy.return_value = True

        # Exécution en capturant stdout
        with patch('sys.stdout', new=StringIO()):
            main()

        # Vérification que la fonction de haut niveau a été appelée
        mock_copy.assert_called_once_with("# Generated Content")

if __name__ == '__main__':
    unittest.main()
```

## `tests\test_config.py`

```python
"""
Tests for configuration module.
"""
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.config import AssemblerConfig


class TestExtensionClassification(unittest.TestCase):
    """Test that extensions and exact filenames are correctly separated."""

    def _make_config(self, extensions):
        """Helper to create config with given extensions."""
        return AssemblerConfig(
            paths=["."],
            extensions=extensions,
            use_default_excludes=False
        )

    def test_bare_extensions(self):
        """Test that bare extensions (py, md, js) get a dot prefix."""
        config = self._make_config(["py", "md", "js"])
        self.assertEqual(sorted(config.extensions), [".js", ".md", ".py"])
        self.assertEqual(config.exact_filenames, [])

    def test_dotted_extensions(self):
        """Test that dotted extensions (.py, .md) stay as-is."""
        config = self._make_config([".py", ".md", ".toml"])
        self.assertEqual(sorted(config.extensions), [".md", ".py", ".toml"])
        self.assertEqual(config.exact_filenames, [])

    def test_exact_filenames(self):
        """Test that uppercase names become exact filenames."""
        config = self._make_config(["Dockerfile", "Makefile"])
        self.assertEqual(config.extensions, [])
        self.assertEqual(sorted(config.exact_filenames), ["Dockerfile", "Makefile"])

    def test_mixed(self):
        """Test mixed extensions and exact filenames."""
        config = self._make_config(["py", ".md", "Dockerfile", "toml", "Makefile"])
        self.assertEqual(sorted(config.extensions), [".md", ".py", ".toml"])
        self.assertEqual(sorted(config.exact_filenames), ["Dockerfile", "Makefile"])

    def test_dotfiles(self):
        """Test dotfiles like .env are treated as extensions."""
        config = self._make_config([".env", ".gitignore"])
        self.assertEqual(sorted(config.extensions), [".env", ".gitignore"])
        self.assertEqual(config.exact_filenames, [])

    def test_compound_extensions(self):
        """Test compound extensions like .env.j2."""
        config = self._make_config([".env.j2", "env.j2"])
        self.assertEqual(sorted(config.extensions), [".env.j2", ".env.j2"])
        self.assertEqual(config.exact_filenames, [])

    def test_realistic_python_project(self):
        """Test a realistic Python project configuration."""
        config = self._make_config(["py", "md", "toml", "yaml", "j2"])
        self.assertIn(".py", config.extensions)
        self.assertIn(".md", config.extensions)
        self.assertIn(".toml", config.extensions)
        self.assertIn(".yaml", config.extensions)
        self.assertIn(".j2", config.extensions)
        self.assertEqual(config.exact_filenames, [])

    def test_realistic_devops_project(self):
        """Test a realistic DevOps project configuration."""
        config = self._make_config([".py", ".yml", "Dockerfile", "Makefile", ".env"])
        self.assertIn(".py", config.extensions)
        self.assertIn(".yml", config.extensions)
        self.assertIn(".env", config.extensions)
        self.assertIn("Dockerfile", config.exact_filenames)
        self.assertIn("Makefile", config.exact_filenames)


if __name__ == "__main__":
    unittest.main()

```

## `tests\test_core.py`

```python
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# --- PATH SETUP ---
# Add the 'src' directory to the search path so 'code_assembler' can be found
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

from code_assembler.core import assemble_codebase, assemble_from_config


class TestCore(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory before each test."""
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        shutil.rmtree(self.test_dir)

    def test_smart_truncation(self):
        """Test if large files are correctly truncated based on configuration."""
        src_dir = self.root / "src"
        src_dir.mkdir()

        large_file = src_dir / "big_data.py"
        # Write 100 lines of dummy content
        content = "\n".join([f"line {i}" for i in range(100)])
        large_file.write_text(content, encoding='utf-8')

        output_file = self.root / "output.md"

        # Run assembly with a tiny size limit to force truncation
        assemble_codebase(
            paths=[str(src_dir)],
            extensions=[".py"],
            output=str(output_file),
            max_file_size_mb=0.0001,  # Very low threshold
            truncate_large_files=True,
            truncation_limit_lines=5,
            show_progress=False
        )

        result = output_file.read_text(encoding='utf-8')

        self.assertIn("line 0", result)
        self.assertIn("line 4", result)
        self.assertNotIn("line 50", result, "File was not truncated!")
        self.assertIn("[TRUNCATED]", result, "Truncation marker is missing")

    def test_exclusion_logic(self):
        """Test if the exclusion logic correctly skips specified patterns."""
        src_dir = self.root / "project"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('main')", encoding='utf-8')

        # Directory to exclude
        tests_dir = src_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("print('test')", encoding='utf-8')

        output_file = self.root / "output.md"

        assemble_codebase(
            paths=[str(src_dir)],
            extensions=[".py"],
            exclude_patterns=["tests"],
            output=str(output_file),
            show_progress=False
        )

        result = output_file.read_text(encoding='utf-8')
        self.assertIn("main.py", result)
        self.assertNotIn("test_main.py", result, "The 'tests' directory should have been excluded")

    def test_json_config_loading(self):
        """Test loading configuration from a JSON file and the output_file mapping."""
        src_dir = self.root / "src"
        src_dir.mkdir()
        (src_dir / "script.py").write_text("print('ok')", encoding='utf-8')

        config_file = self.root / "config.json"
        output_md = self.root / "result_from_json.md"

        # JSON config using 'output' key
        config_data = {
            "paths": [str(src_dir)],
            "extensions": [".py"],
            "output": str(output_md),
            "show_progress": False
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        assemble_from_config(str(config_file))

        self.assertTrue(output_md.exists(), "Output file defined in JSON was not created")


if __name__ == '__main__':
    unittest.main()

```

## `tests\test_delta_scenario.py`

```python
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

# Ajout du src au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.core import assemble_codebase


class TestDeltaScenario(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)

        # Structure complexe pour tester l'indentation
        # root/
        #   ├── api/
        #   │    └── config.py  <-- Fichier A
        #   └── db/
        #        └── config.py  <-- Fichier B (Même nom !)

        (self.root / "api").mkdir()
        (self.root / "db").mkdir()

        self.file_a = self.root / "api" / "config.py"
        self.file_b = self.root / "db" / "config.py"

        self.file_a.write_text("API_CONFIG = 1", encoding="utf-8")
        self.file_b.write_text("DB_CONFIG = 1", encoding="utf-8")

        past_time = time.time() - 300
        os.utime(self.file_a, (past_time, past_time))
        os.utime(self.file_b, (past_time, past_time))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_duplicate_filenames_handling(self):
        """
        Vérifie que modifier db/config.py n'inclut pas api/config.py
        malgré le même nom de fichier.
        """
        ref_md = self.root / "reference.md"
        delta_md = self.root / "delta.md"

        # 1. Générer la référence
        assemble_codebase(
            paths=[str(self.root)],
            extensions=[".py"],
            output=str(ref_md),
            show_progress=False
        )

        # Pause pour garantir un mtime différent (systèmes de fichiers rapides)
        time.sleep(1.1)

        # 2. Modifier SEULEMENT db/config.py
        self.file_b.write_text("DB_CONFIG = 2  # Modified", encoding="utf-8")

        # 3. Générer le delta
        assemble_codebase(
            paths=[str(self.root)],
            extensions=[".py"],
            output=str(delta_md),
            since=str(ref_md),  # <-- Option clé
            show_progress=False
        )

        # 4. Analyser le résultat
        content = delta_md.read_text(encoding="utf-8")

        # VÉRIFICATIONS
        print("\n--- Contenu du Delta ---")
        print(content)
        print("------------------------")

        # Le fichier modifié DOIT être présent
        self.assertIn("DB_CONFIG = 2", content, "Le fichier modifié (db/config.py) est absent !")

        # Le fichier non modifié NE DOIT PAS être présent
        self.assertNotIn("API_CONFIG = 1", content, "Le fichier non modifié (api/config.py) est présent à tort !")

        # Vérifier le header
        self.assertIn("> ✏️  Modified (1): config.py", content)


if __name__ == "__main__":
    unittest.main()

```

## `tests\test_file_io.py`

```python
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from code_assembler.file_io import read_file_head


class TestFileIO(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_path = Path(self.test_dir) / "test_file.txt"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_file_head(self):
        """Test reading only the first N lines of a file."""
        content = "\n".join([f"Line {i}" for i in range(1, 11)])
        self.file_path.write_text(content, encoding='utf-8')

        head = read_file_head(str(self.file_path), max_lines=3)

        lines = head.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], "Line 1")
        self.assertEqual(lines[2], "Line 3")

    def test_read_file_head_small_file(self):
        """Test reading head of a file smaller than the limit."""
        self.file_path.write_text("Single line", encoding='utf-8')

        head = read_file_head(str(self.file_path), max_lines=50)
        self.assertEqual(head, "Single line")


if __name__ == '__main__':
    unittest.main()

```

## `tests\test_formats.py`

```python
"""
Tests for file format detection and syntax highlighting.
"""
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.formatters import MarkdownFormatter


class TestFileFormats(unittest.TestCase):
    def setUp(self):
        self.formatter = MarkdownFormatter()

    def test_standard_extensions(self):
        """Test detection of common extensions."""
        self.assertEqual(self.formatter._detect_language("main.py"), "python")
        self.assertEqual(self.formatter._detect_language("script.js"), "javascript")
        self.assertEqual(self.formatter._detect_language("styles.css"), "css")

    def test_new_formats(self):
        """Test detection of newly added formats like Jinja2."""
        self.assertEqual(self.formatter._detect_language("template.j2"), "jinja2")
        self.assertEqual(self.formatter._detect_language("config.jinja2"), "jinja2")
        self.assertEqual(self.formatter._detect_language("infra.tf"), "hcl")

    def test_special_filenames(self):
        """Test detection of files without extensions or special names."""
        self.assertEqual(self.formatter._detect_language("Dockerfile"), "dockerfile")
        self.assertEqual(self.formatter._detect_language("Makefile"), "makefile")
        self.assertEqual(self.formatter._detect_language(".env"), "bash")
        self.assertEqual(self.formatter._detect_language(".env.local"), "bash")

    def test_case_insensitivity(self):
        """Test that detection is case-insensitive."""
        self.assertEqual(self.formatter._detect_language("MAIN.PY"), "python")
        self.assertEqual(self.formatter._detect_language("DOCKERFILE"), "dockerfile")

    def test_unknown_format(self):
        """Test fallback to 'text' for unknown formats."""
        self.assertEqual(self.formatter._detect_language("data.unknown_ext"), "text")
        self.assertEqual(self.formatter._detect_language("README"), "text")


if __name__ == "__main__":
    unittest.main()

```

## `tests\test_interactive.py`

```python
"""
Tests for interactive wizard mode.
"""
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.interactive import InteractiveWizard


class TestInteractiveWizard(unittest.TestCase):
    """Test cases for the interactive wizard."""

    def setUp(self):
        """Set up test wizard instance."""
        self.wizard = InteractiveWizard()

    def test_yes_no_default_yes(self):
        """Test yes/no question with default Yes."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_yes_no("Test?", default=True)
            self.assertTrue(result)

    def test_yes_no_default_no(self):
        """Test yes/no question with default No."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_yes_no("Test?", default=False)
            self.assertFalse(result)

    def test_yes_no_explicit_yes(self):
        """Test explicit yes answer."""
        with patch('builtins.input', return_value='y'):
            result = self.wizard._ask_yes_no("Test?")
            self.assertTrue(result)

    def test_yes_no_explicit_no(self):
        """Test explicit no answer."""
        with patch('builtins.input', return_value='n'):
            result = self.wizard._ask_yes_no("Test?")
            self.assertFalse(result)

    def test_ask_number_default(self):
        """Test number input with default."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_number("Size?", default=10.0)
            self.assertEqual(result, 10.0)

    def test_ask_number_custom(self):
        """Test number input with custom value."""
        with patch('builtins.input', return_value='5.5'):
            result = self.wizard._ask_number("Size?", default=10.0)
            self.assertEqual(result, 5.5)

    def test_ask_number_validation(self):
        """Test number input validation."""
        # First invalid, then valid
        with patch('builtins.input', side_effect=['invalid', '5.0']):
            result = self.wizard._ask_number("Size?", default=10.0)
            self.assertEqual(result, 5.0)

    def test_ask_text_default(self):
        """Test text input with default."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_text("Name?", default="test.md")
            self.assertEqual(result, "test.md")

    def test_ask_text_custom(self):
        """Test text input with custom value."""
        with patch('builtins.input', return_value='custom.md'):
            result = self.wizard._ask_text("Name?", default="test.md")
            self.assertEqual(result, "custom.md")

    def test_select_paths_current_dir(self):
        """Test selecting current directory."""
        with patch('builtins.input', return_value='1'):
            paths = self.wizard._select_paths()
            self.assertEqual(paths, ['.'])

    def test_select_extensions_preset(self):
        """Test selecting extension preset."""
        with patch('builtins.input', return_value='1'):
            extensions = self.wizard._select_extensions()
            self.assertIn('.py', extensions)

    def test_configure_exclusions_defaults_only(self):
        """Test using default exclusions."""
        with patch('builtins.input', side_effect=['y', 'n']):  # Use defaults, no custom
            patterns = self.wizard._configure_exclusions()
            self.assertIn('__pycache__', patterns)
            self.assertIn('.git', patterns)

    def test_configure_output_default(self):
        """Test output configuration with default."""
        with patch('builtins.input', return_value=''):
            with patch('code_assembler.interactive.os.path.exists', return_value=False):
                output = self.wizard._configure_output()
                self.assertEqual(output, 'codebase.md')

    def test_configure_output_custom(self):
        """Test output configuration with custom name."""
        with patch('builtins.input', return_value='my_project'):
            output = self.wizard._configure_output()
            self.assertEqual(output, 'my_project.md')  # Should auto-add .md

    def test_configure_advanced_all_defaults(self):
        """Test advanced config with all defaults."""
        with patch('builtins.input', return_value='n'):  # Don't configure advanced
            advanced = self.wizard._configure_advanced()
            self.assertTrue(advanced['recursive'])
            self.assertTrue(advanced['include_readmes'])
            self.assertEqual(advanced['max_file_size_mb'], 10.0)

    @patch('builtins.input')
    @patch('code_assembler.interactive.os.path.exists')
    def test_full_wizard_flow(self, mock_exists, mock_input):
        """Test complete wizard flow."""
        # Mock user inputs for entire flow
        mock_input.side_effect = [
            '1',  # Current directory
            '1',  # Python preset
            'y', 'n',  # Use defaults, no custom exclusions
            '',  # Default output name
            'n',  # No advanced config
            'y',  # Confirm assembly
            'n',  # Don't save config
        ]

        # Mock file existence check
        mock_exists.return_value = False

        # Mock assemble_codebase to avoid actual execution
        with patch('code_assembler.interactive.assemble_codebase') as mock_assemble:
            mock_assemble.return_value = "# Mock content"

            # Capture print output
            with patch('sys.stdout', new=StringIO()):
                result = self.wizard.run()

            # Verify assemble was called
            mock_assemble.assert_called_once()

            # Verify result
            self.assertEqual(result, "# Mock content")

    def test_wizard_keyboard_interrupt(self):
        """Test wizard handles Ctrl+C gracefully."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new=StringIO()):
                result = self.wizard.run()
            self.assertIsNone(result)

    def test_available_extensions(self):
        """Test that available extensions are loaded."""
        self.assertGreater(len(self.wizard.available_extensions), 0)
        self.assertIn('.py', self.wizard.available_extensions)
        self.assertIn('.js', self.wizard.available_extensions)

    def test_select_extensions_custom_with_commas(self):
        """Regression test: extensions typed with commas must be cleaned."""
        # Simule l'utilisateur qui tape ".py, .yaml, .tsx,"
        with patch('builtins.input', side_effect=['8', '.py, .yaml, .tsx,']):
            extensions = self.wizard._select_extensions()

        self.assertIn('.py', extensions)
        self.assertIn('.yaml', extensions)
        self.assertIn('.tsx', extensions)
        # S'assurer qu'aucune extension ne contient de virgule
        for ext in extensions:
            self.assertNotIn(',', ext, f"Extension '{ext}' contains a comma!")

    def test_select_extensions_custom_space_separated(self):
        """Normal case: space-separated extensions work correctly."""
        with patch('builtins.input', side_effect=['8', '.py .yaml .tsx']):
            extensions = self.wizard._select_extensions()

        self.assertIn('.py', extensions)
        self.assertIn('.yaml', extensions)
        self.assertIn('.tsx', extensions)


if __name__ == '__main__':
    unittest.main()

```

## `tests\test_rebuild.py`

```python
"""
Tests for the Rebuild functionality of Code Assembler Pro.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.rebuilder import CodebaseRebuilder


class TestRebuild(unittest.TestCase):
    def setUp(self):
        """Create a temporary environment for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.output_dir = self.root / "restored"
        self.md_file = self.root / "snapshot.md"

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def _create_mock_md(self, files_data: dict, metadata_files: dict):
        """
        Helper to create a valid Markdown snapshot with metadata.
        files_data: { "rel/path": "content" }
        metadata_files: { "rel/path": "timestamp" }
        """
        lines = ["# Consolidated Codebase\n", "## Table of Contents\n"]

        # Add TOC
        for path in metadata_files:
            lines.append(f"- `{path}` | 2026-02-17 10:00")

        lines.append("\n---\n")

        # Add File Blocks
        for path, content in files_data.items():
            lines.append(f"# `{path}`\n")
            lines.append("```python")
            lines.append(content)
            lines.append("```\n")

        # Add Metadata Block
        metadata = {
            "version": "4.4.0",
            "generated_at": "2026-02-17 10:00:00",
            "files": metadata_files
        }
        lines.append(f"\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(metadata)}\n-->")

        self.md_file.write_text("\n".join(lines), encoding='utf-8')

    def test_successful_rebuild(self):
        """Test a standard successful reconstruction of multiple files."""
        files = {
            "src/main.py": "print('hello')",
            "config/settings.json": '{"key": "value"}'
        }
        meta = {
            "src/main.py": "2026-02-17 10:00",
            "config/settings.json": "2026-02-17 10:00"
        }
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 2)
        self.assertEqual(len(errors), 0)

        # Verify files exist and content is correct
        self.assertTrue((self.output_dir / "src/main.py").exists())
        self.assertEqual((self.output_dir / "src/main.py").read_text(), "print('hello')")
        self.assertTrue((self.output_dir / "config/settings.json").exists())

    def test_security_path_traversal(self):
        """Test that the rebuilder blocks attempts to write outside the output directory."""
        files = {"../../evil.py": "malicious code"}
        meta = {"../../evil.py": "2026-02-17 10:00"}
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 0)
        self.assertTrue(any("Security skip" in err for err in errors))
        self.assertFalse((self.root / "evil.py").exists())

    def test_dry_run(self):
        """Test that dry_run mode does not write any files."""
        files = {"test.py": "content"}
        meta = {"test.py": "2026-02-17 10:00"}
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir), dry_run=True)
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 1)
        self.assertFalse(self.output_dir.exists())

    def test_truncation_warning(self):
        """Test that the rebuilder detects and warns about truncated files."""
        files = {"large.py": "part 1\n[TRUNCATED]\npart 2"}
        meta = {"large.py": "2026-02-17 10:00"}
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 1)
        self.assertTrue(any("truncated" in err.lower() for err in errors))

    def test_missing_metadata(self):
        """Test behavior when the Markdown file has no metadata block."""
        self.md_file.write_text("# Just some markdown", encoding='utf-8')

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 0)
        self.assertIn("No valid metadata found", errors[0])


if __name__ == "__main__":
    unittest.main()

```

## `tests\test_utils.py`

```python
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from code_assembler.utils import (
    should_exclude,
    normalize_path,
    format_file_size,
    slugify_path
)


class TestUtils(unittest.TestCase):

    def test_normalize_path(self):
        """Test path normalization for cross-platform consistency."""
        # Windows style to POSIX
        self.assertEqual(normalize_path("C:\\Users\\Test"), "c:/users/test")

        # Trailing slash removal
        res = normalize_path("/var/www/html/")
        self.assertTrue(res.endswith("/var/www/html"))

        self.assertEqual(normalize_path(""), "")

    def test_should_exclude(self):
        """Test the exclusion logic with various patterns."""
        patterns = ["__pycache__", ".git", "venv", "secret.py"]

        # Case 1: Parent directory exclusion
        self.assertTrue(should_exclude("/abs/path/to/__pycache__/file.pyc", patterns))

        # Case 2: Root folder exclusion
        self.assertTrue(should_exclude(".git/config", patterns))

        # Case 3: Exact filename exclusion
        self.assertTrue(should_exclude("src/secret.py", patterns))

        # Case 4: Should NOT exclude
        self.assertFalse(should_exclude("src/main.py", patterns))

        # Case 5: Glob pattern (prefix match with wildcard)
        self.assertTrue(should_exclude("tests/test_user.py", ["test_*"]))

        # Case 6: No false positives — "dist" must NOT match "redistribute"
        self.assertFalse(should_exclude("src/redistribute.py", ["dist"]))

        # Case 7: No false positives — "env" must NOT match "environment.py"
        self.assertFalse(should_exclude("src/environment.py", ["env"]))

        # Case 8: Extension pattern
        self.assertTrue(should_exclude("cache/module.pyc", [".pyc"]))

    def test_format_file_size(self):
        """Test human-readable file size formatting."""
        self.assertEqual(format_file_size(0), "0B")
        self.assertEqual(format_file_size(512), "512B")
        self.assertEqual(format_file_size(1024), "1.0KB")
        self.assertEqual(format_file_size(1572864), "1.5MB")

    def test_slugify(self):
        """Test conversion of paths to valid HTML anchors."""
        self.assertEqual(slugify_path("path/to/File.py"), "path_to_file_py")
        self.assertEqual(slugify_path("C:\\My Docs\\script.js"), "c__my_docs_script_js")


if __name__ == '__main__':
    unittest.main()

```



<!-- CODE_ASSEMBLER_METADATA
{
  "version": "4.4.2",
  "generated_at": "2026-05-02 04:39:38",
  "files": {
    "src/code_assembler/__init__.py": "2026-02-17 09:29",
    "src/code_assembler/__main__.py": "2026-02-17 09:29",
    "src/code_assembler/analyzers.py": "2026-02-17 09:28",
    "src/code_assembler/cli.py": "2026-02-17 09:29",
    "src/code_assembler/config.py": "2026-02-17 09:29",
    "src/code_assembler/constants.py": "2026-02-17 11:22",
    "src/code_assembler/core.py": "2026-02-17 09:29",
    "src/code_assembler/delta.py": "2026-02-17 09:28",
    "src/code_assembler/file_io.py": "2026-02-17 09:29",
    "src/code_assembler/formatters.py": "2026-02-17 09:29",
    "src/code_assembler/interactive.py": "2026-02-17 09:29",
    "src/code_assembler/rebuilder.py": "2026-02-17 11:25",
    "src/code_assembler/templates/components/architecture.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/file_block.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/readme_context.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/stats_table.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/toc.md.j2": "2026-02-16 16:43",
    "src/code_assembler/templates/main_header.md.j2": "2026-02-16 16:59",
    "src/code_assembler/utils.py": "2026-02-17 10:10",
    "examples/__init__.py": "2026-01-25 11:22",
    "examples/advanced_config.py": "2026-02-17 11:20",
    "examples/basic_usage.py": "2026-02-17 11:26",
    "examples/interactive_demo.py": "2026-01-25 16:13",
    "examples/rebuild_usage.py": "2026-02-17 11:28",
    "tests/__init__.py": "2026-01-25 11:21",
    "tests/test_clipboard.py": "2026-02-17 10:10",
    "tests/test_config.py": "2026-02-17 09:29",
    "tests/test_core.py": "2026-02-17 09:29",
    "tests/test_delta_scenario.py": "2026-02-17 09:29",
    "tests/test_file_io.py": "2026-02-17 09:29",
    "tests/test_formats.py": "2026-02-17 09:29",
    "tests/test_interactive.py": "2026-02-17 09:29",
    "tests/test_rebuild.py": "2026-02-17 09:29",
    "tests/test_utils.py": "2026-02-17 09:29"
  }
}
-->