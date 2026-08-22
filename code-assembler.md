# Consolidated Codebase

> **Snapshot:** 2026-06-30 14:59 | **Files:** 45 | **Tokens:** ~56,888

---

## Table of Contents

- `code_assembler/`
  - `__init__.py` | 2026-02-17 09:29
  - `__main__.py` | 2026-02-17 09:29
  - `analyzers.py` | 2026-05-02 05:32
  - `cli.py` | 2026-06-30 11:19
  - `compressor.py` | 2026-05-02 04:59
  - `config.py` | 2026-05-02 05:32
  - `constants.py` | 2026-06-30 11:19
  - `core.py` | 2026-05-02 05:53
  - `delta.py` | 2026-05-02 05:33
  - `file_io.py` | 2026-02-17 09:29
  - `formatters.py` | 2026-02-17 09:29
  - `interactive.py` | 2026-05-02 05:33
  - `rebuilder.py` | 2026-06-30 11:16
  - `templates/`
    - `components/`
      - `architecture.md.j2` | 2026-02-14 19:44
      - `file_block.md.j2` | 2026-02-14 19:44
      - `readme_context.md.j2` | 2026-02-14 19:44
      - `stats_table.md.j2` | 2026-02-14 19:44
      - `toc.md.j2` | 2026-02-16 16:43
    - `main_header.md.j2` | 2026-02-16 16:59
  - `utils.py` | 2026-05-02 05:33
- `__init__.py` | 2026-01-25 11:22
- `advanced_config.py` | 2026-02-17 11:20
- `basic_usage.py` | 2026-02-17 11:26
- `interactive_demo.py` | 2026-01-25 16:13
- `rebuild_usage.py` | 2026-02-17 11:28
- `INTERACTIVE_DEMO.md` | 2026-01-25 16:17
- `__init__.py` | 2026-01-25 11:21
- `test_clipboard.py` | 2026-05-02 05:40
- `test_compressor.py` | 2026-05-02 05:11
- `test_config.py` | 2026-02-17 09:29
- `test_core.py` | 2026-02-17 09:29
- `test_delta_scenario.py` | 2026-02-17 09:29
- `test_file_io.py` | 2026-02-17 09:29
- `test_formats.py` | 2026-02-17 09:29
- `test_interactive.py` | 2026-02-17 09:29
- `test_rebuild.py` | 2026-06-30 11:23
- `test_robustness.py` | 2026-05-02 05:37
- `test_utils.py` | 2026-02-17 09:29
- `ROADMAP.md` | 2026-06-30 11:19
- `README.md` | 2026-06-30 11:19
- `QUICKSTART_INTERACTIVE.md` | 2026-02-17 09:22
- `INTERACTIVE_MODE.md` | 2026-02-17 09:20
- `BUILD_AND_RELEASE.md` | 2026-06-30 11:19
- `CHANGELOG.md` | 2026-06-30 14:40
- `AGENTS.md` | 2026-06-30 14:59


---

## Architecture

**Components:**
- `docs/` (1 file)
- `examples/` (5 files)
- `src/` (20 files)
- `tests/` (12 files)

**File types:**
- `.py` (python): 31 — 68.9%
- `.md` (markdown): 8 — 17.8%
- `.j2` (jinja2): 6 — 13.3%


---

## Stats

**45** files | **6,219** lines | ~**56,888** tokens | Extensions: j2, md, py


---

45 source files follow below.

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
        self.entries = entries
        self.stats = stats

    def analyze_data(self) -> Dict[str, Any]:
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

        # FIX: os.path.commonpath raises ValueError on Windows when paths span
        # multiple drives (e.g. C:\ and D:\). Fall back gracefully to CWD.
        all_paths = [Path(e.path) for e in self.entries]
        try:
            root_path = Path(os.path.commonpath([str(p) for p in all_paths]))
        except ValueError:
            root_path = Path(os.getcwd())

        results = []
        top_dirs: Set[str] = set()

        for entry in self.entries:
            try:
                rel_path = Path(entry.path).relative_to(root_path)
                if len(rel_path.parts) > 1:
                    top_dirs.add(rel_path.parts[0])
            except ValueError:
                continue

        for dir_name in sorted(top_dirs):
            count = sum(1 for e in self.entries if e.is_file and dir_name in Path(e.path).parts)
            results.append({"name": dir_name, "count": count})

        return results

    def _get_depth_distribution(self) -> Dict[int, int]:
        """Count files at each directory depth level and sync max_depth."""
        depth_counts: Dict[int, int] = defaultdict(int)
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

New in v4.5.2:
    - --compress / -z: Reduce files to signatures + docstrings only.
    - --compress-level: Control compression depth.
    - CLI flags (--compress, --since) now work when combined with --config.
"""

import argparse
import json
import sys
from typing import List, Optional

from .constants import (
    __version__,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_EXCLUDE_PATTERNS,
    EMOJI
)
from .core import assemble_codebase, assemble_from_config


def _show_excludes() -> None:
    """Print the default exclusion patterns to stdout."""
    print(f"\n{EMOJI['mag']} Default exclusion patterns ({len(DEFAULT_EXCLUDE_PATTERNS)}):\n")
    for pattern in sorted(DEFAULT_EXCLUDE_PATTERNS):
        print(f"  - {pattern}")
    print(
        f"\nThese are added automatically unless you pass --no-default-excludes.\n"
        f"Add extra patterns with: --exclude pattern1 pattern2"
    )


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

    # --- Compression Mode ---
    compress_group = parser.add_argument_group(
        "Compression Mode",
        description=(
            "Reduce source files to their structural skeleton "
            "(signatures + docstrings). Python is always supported via stdlib ast. "
            "Other languages require: pip install tree-sitter tree-sitter-<lang>. "
            "Works with both direct paths and --config."
        )
    )
    compress_group.add_argument(
        "--compress", "-z",
        action="store_true",
        help="Compress files to signatures and docstrings only"
    )
    compress_group.add_argument(
        "--compress-level",
        dest="compress_level",
        default="signatures",
        choices=["signatures", "docstrings_only"],
        help="Compression depth (default: signatures)"
    )

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


def _save_config(args: argparse.Namespace, extensions: List[str]) -> None:
    """Save CLI arguments as a JSON config file."""
    config = {
        "paths": args.paths,
        "extensions": extensions,
        "output": args.output,
        "recursive": args.recursive,
        "include_readmes": args.include_readmes,
        "max_file_size_mb": args.max_size,
        "use_default_excludes": args.use_default_excludes,
        "compress": args.compress,
        "compress_level": args.compress_level,
    }
    if args.exclude_patterns:
        config["exclude_patterns"] = args.exclude_patterns

    with open(args.save_config, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Main entry point."""
    args = parse_args()
    content: Optional[str] = None

    try:
        if args.show_excludes:
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
            if errors:
                print(f"\n{EMOJI['warning']} Rebuild completed with {len(errors)} warning(s):")
                for err in errors:
                    print(f"   - {err}")
            if not args.dry_run:
                print(f"\n{EMOJI['success']} {count} file(s) reconstructed in: {args.output_dir}")
            return

        if args.config:
            # FIX: CLI flags now propagate as overrides into the JSON config path.
            # Previously --compress (and --since) were silently ignored when
            # --config was also passed, because assemble_from_config was called
            # without them.  Now we pass them explicitly; assemble_from_config
            # merges them on top of the JSON values so CLI always wins.
            cli_overrides = {}
            if args.compress:
                cli_overrides["compress"] = True
                cli_overrides["compress_level"] = args.compress_level

            content = assemble_from_config(
                args.config,
                since=args.since,
                **cli_overrides,
            )
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
                compress=args.compress,
                compress_level=args.compress_level,
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

### `src\code_assembler\compressor.py`

```python
"""
Code compression module for Code Assembler Pro.

Reduces source files to their structural skeleton — signatures and docstrings —
using tree-sitter parsers (installed individually per language) or the Python
stdlib `ast` module as a zero-dependency fallback for Python files.

Architecture:
    * Python files  → stdlib `ast`  (always available, no install needed)
    * Other languages → tree-sitter with per-language packages (optional)
        pip install tree-sitter tree-sitter-javascript tree-sitter-rust ...

The compressor is initialised once by CodebaseAssembler with the list of
extensions configured by the user. It resolves and loads only the parsers
that are actually needed, then reports which ones are missing so the user
can install them selectively.
"""

import ast
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .constants import LANGUAGE_MAP, EMOJI

# ---------------------------------------------------------------------------
# Mapping: language name → tree-sitter PyPI package / importable module name
# These are the *individual* packages (tree-sitter ≥ 0.21 API).
# ---------------------------------------------------------------------------
TREESITTER_MODULE_MAP: Dict[str, str] = {
    "python":       "tree_sitter_python",
    "javascript":   "tree_sitter_javascript",
    "jsx":          "tree_sitter_javascript",   # same grammar
    "typescript":   "tree_sitter_typescript",
    "tsx":          "tree_sitter_typescript",   # same grammar
    "rust":         "tree_sitter_rust",
    "go":           "tree_sitter_go",
    "java":         "tree_sitter_java",
    "c":            "tree_sitter_c",
    "cpp":          "tree_sitter_cpp",
    "ruby":         "tree_sitter_ruby",
    "php":          "tree_sitter_php",
    "csharp":       "tree_sitter_c_sharp",
    "lua":          "tree_sitter_lua",
    "swift":        "tree_sitter_swift",
    "kotlin":       "tree_sitter_kotlin",
    "scala":        "tree_sitter_scala",
    "r":            "tree_sitter_r",
}

# ---------------------------------------------------------------------------
# Per-language tree-sitter node configuration
# function_types : node types that represent a callable definition
# class_types    : node types that represent a class / struct / impl block
# body_type      : name of the child node that holds the body
# brace_style    : True for { } languages, False for indentation-based
# ---------------------------------------------------------------------------
LANGUAGE_NODE_CONFIG: Dict[str, Dict] = {
    "python": {
        "function_types": {"function_definition"},
        "class_types":    {"class_definition"},
        "body_type":      "block",
        "brace_style":    False,
    },
    "javascript": {
        "function_types": {
            "function_declaration",
            "method_definition",
            "generator_function_declaration",
        },
        "class_types":  {"class_declaration"},
        "body_type":    "statement_block",
        "brace_style":  True,
    },
    "typescript": {
        "function_types": {
            "function_declaration",
            "method_definition",
            "generator_function_declaration",
        },
        "class_types":  {"class_declaration", "interface_declaration"},
        "body_type":    "statement_block",
        "brace_style":  True,
    },
    "rust": {
        "function_types": {"function_item"},
        "class_types":    {"impl_item", "trait_item"},
        "body_type":      "block",
        "brace_style":    True,
    },
    "go": {
        "function_types": {"function_declaration", "method_declaration"},
        "class_types":    set(),
        "body_type":      "block",
        "brace_style":    True,
    },
    "java": {
        "function_types": {"method_declaration", "constructor_declaration"},
        "class_types":    {"class_declaration", "interface_declaration"},
        "body_type":      "block",
        "brace_style":    True,
    },
    "c": {
        "function_types": {"function_definition"},
        "class_types":    {"struct_specifier"},
        "body_type":      "compound_statement",
        "brace_style":    True,
    },
    "cpp": {
        "function_types": {"function_definition"},
        "class_types":    {"class_specifier", "struct_specifier"},
        "body_type":      "compound_statement",
        "brace_style":    True,
    },
}

# Aliases for languages sharing a grammar
LANGUAGE_NODE_CONFIG["jsx"] = LANGUAGE_NODE_CONFIG["javascript"]
LANGUAGE_NODE_CONFIG["tsx"] = LANGUAGE_NODE_CONFIG["typescript"]


# ---------------------------------------------------------------------------

class CodeCompressor:
    """
    Compresses source files to structural skeletons.

    Signatures and docstrings are preserved; implementation bodies are
    replaced with ``...``.

    Python files are always handled via stdlib ``ast`` (zero external deps).
    All other languages require the corresponding ``tree-sitter-<lang>``
    package to be installed. Missing packages are reported once at startup.
    """

    def __init__(self, extensions: List[str]):
        """
        Initialise the compressor and load only the parsers needed.

        Args:
            extensions: Normalised extensions from AssemblerConfig
                        (e.g. ['.py', '.js', '.ts']).
        """
        self.parsers: Dict[str, object] = {}
        self._missing_packages: List[str] = []
        self._load_parsers(extensions)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _ext_to_lang(self, ext: str) -> Optional[str]:
        """Resolve an extension to a language name via LANGUAGE_MAP."""
        return LANGUAGE_MAP.get(ext.lower())

    def _load_parsers(self, extensions: List[str]) -> None:
        """Dynamically import tree-sitter parsers for non-Python extensions."""
        langs_needed: Set[str] = set()
        for ext in extensions:
            lang = self._ext_to_lang(ext)
            if lang and lang != "python" and lang in TREESITTER_MODULE_MAP:
                langs_needed.add(lang)

        if not langs_needed:
            return

        # Check tree-sitter core first
        try:
            from tree_sitter import Language, Parser  # noqa: F401
        except ImportError:
            print(
                f"  {EMOJI['warning']} tree-sitter core not found. "
                "Run: pip install tree-sitter"
            )
            return

        from tree_sitter import Language, Parser

        for lang in sorted(langs_needed):
            module_name = TREESITTER_MODULE_MAP[lang]
            pip_name = module_name.replace("_", "-")
            try:
                module = importlib.import_module(module_name)
                language = Language(module.language())
                self.parsers[lang] = Parser(language)
            except ImportError:
                self._missing_packages.append(pip_name)
            except Exception as exc:
                print(f"  {EMOJI['warning']} Parser load failed for {lang}: {exc}")

        if self._missing_packages:
            pkgs = " ".join(self._missing_packages)
            print(
                f"  {EMOJI['warning']} Some tree-sitter parsers are missing.\n"
                f"    Install them with: pip install {pkgs}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compress(self, content: str, file_path: str) -> str:
        """
        Compress *content* to its structural skeleton.

        Args:
            content:   Raw source code.
            file_path: Original file path (used to detect language).

        Returns:
            Compressed source, or the original content if compression
            is not available for this language.
        """
        ext = Path(file_path).suffix.lower()
        lang = self._ext_to_lang(ext)

        if not lang:
            return content

        if lang == "python":
            return self._compress_python_ast(content)

        if lang in self.parsers:
            try:
                return self._compress_treesitter(content, lang)
            except Exception:
                # Never crash the assembly — silently return original
                return content

        return content

    # ------------------------------------------------------------------
    # Python — stdlib ast (no external dependency)
    # ------------------------------------------------------------------

    def _compress_python_ast(self, source: str) -> str:
        """Compress Python source using stdlib ``ast``."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return source

        lines = source.splitlines(keepends=True)
        suppressions: List[Tuple[int, int, str]] = []

        self._collect_py_suppressions(tree.body, suppressions)

        # Apply replacements from bottom to top to preserve indices
        suppressions.sort(key=lambda x: x[0], reverse=True)
        result = list(lines)
        for start, end, replacement in suppressions:
            result[start:end] = [replacement]

        return "".join(result)

    def _collect_py_suppressions(
        self,
        stmts: list,
        suppressions: List[Tuple[int, int, str]],
    ) -> None:
        """Walk statement list and collect body ranges to suppress."""
        for node in stmts:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._suppress_py_function(node, suppressions)
                # Do NOT recurse: nested functions are suppressed with the body
            elif isinstance(node, ast.ClassDef):
                # Keep class header; recurse to handle each method individually
                self._collect_py_suppressions(node.body, suppressions)

    def _suppress_py_function(
        self,
        node: ast.FunctionDef,
        suppressions: List[Tuple[int, int, str]],
    ) -> None:
        """Record the line range of a function body (after optional docstring)."""
        body = node.body
        first_suppress = 0

        # Keep docstring if it is the very first statement
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            first_suppress = 1

        if first_suppress >= len(body):
            return  # Nothing left to suppress (e.g. body is only a docstring)

        # ast line numbers are 1-indexed; our list is 0-indexed
        start = body[first_suppress].lineno - 1      # inclusive, 0-indexed
        end   = node.end_lineno                       # exclusive, 0-indexed
        indent = " " * (node.col_offset + 4)
        suppressions.append((start, end, f"{indent}...\n"))

    # ------------------------------------------------------------------
    # Generic tree-sitter compression
    # ------------------------------------------------------------------

    def _compress_treesitter(self, source: str, lang: str) -> str:
        """Compress source using a loaded tree-sitter parser."""
        config = LANGUAGE_NODE_CONFIG.get(lang)
        if not config:
            return source

        source_bytes = source.encode("utf-8")
        tree = self.parsers[lang].parse(source_bytes)

        lines = source.splitlines(keepends=True)
        suppressions: List[Tuple[int, int, str]] = []

        self._collect_ts_suppressions(tree.root_node, config, suppressions)

        suppressions.sort(key=lambda x: x[0], reverse=True)
        result = list(lines)
        for start, end, replacement in suppressions:
            result[start:end] = [replacement]

        return "".join(result)

    def _collect_ts_suppressions(self, node, config, suppressions, depth: int = 0) -> None:
        """Recursively collect function body ranges to suppress."""
        for child in node.children:
            if child.type in config["function_types"]:
                self._suppress_ts_body(child, config, suppressions)
                # Do NOT recurse into function body
            elif child.type in config["class_types"]:
                # Recurse into class/struct/impl to handle methods individually
                self._collect_ts_suppressions(child, config, suppressions, depth + 1)
            else:
                self._collect_ts_suppressions(child, config, suppressions, depth)

    def _suppress_ts_body(self, func_node, config, suppressions) -> None:
        """Find the body child of a function node and queue its suppression."""
        body_node = next(
            (c for c in func_node.children if c.type == config["body_type"]),
            None,
        )
        if body_node is None:
            return

        # start_point / end_point are (row, col), 0-indexed
        body_start_row = body_node.start_point[0]
        body_end_row   = body_node.end_point[0]

        if config["brace_style"]:
            # { ... } — keep opening and closing braces, replace inner lines
            if body_end_row <= body_start_row + 1:
                return  # Already a one-liner brace block, skip

            func_col = func_node.start_point[1]
            inner_indent = " " * (func_col + 4)
            # Replace lines strictly between '{' and '}'
            suppressions.append(
                (body_start_row + 1, body_end_row, f"{inner_indent}...\n")
            )
        else:
            # Indentation-based (Python via tree-sitter path, future langs)
            func_col = func_node.start_point[1]
            indent = " " * (func_col + 4)

            first_suppress_row = body_start_row

            # Skip docstring-like first child (expression_statement)
            if body_node.child_count > 0:
                first_child = body_node.children[0]
                if first_child.type == "expression_statement":
                    first_suppress_row = first_child.end_point[0] + 1

            end_row = body_end_row + 1
            if first_suppress_row < end_row:
                suppressions.append((first_suppress_row, end_row, f"{indent}...\n"))
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
        compress: If True, reduces files to signatures + docstrings only
        compress_level: Compression depth — "signatures" keeps function/class
                        headers and docstrings; "docstrings_only" is reserved
                        for a future stricter mode.
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
    __version__ = "4.5.2"  # Fallback for dev mode without pip install

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

    # Config & misc  (FIX: .properties, .graphql, .gql were duplicated — kept here only)
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

    # Modern Web & Data
    ".astro": "astro",
    ".prisma": "prisma",
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
# FIX: removed duplicate "recycle" key — 🔄 was silently overwritten by ♻️
_EMOJI_ICONS = {
    "folder":    "\U0001f4c1",       # 📁
    "file":      "\U0001f4c4",       # 📄
    "readme":    "\u2139\ufe0f",     # ℹ️
    "success":   "\u2705",           # ✅
    "warning":   "\u26a0\ufe0f",     # ⚠️
    "error":     "\u274c",           # ❌
    "rocket":    "\U0001f680",       # 🚀
    "chart":     "\U0001f4ca",       # 📊
    "target":    "\U0001f3af",       # 🎯
    "building":  "\U0001f3db\ufe0f", # 🏛️
    "map":       "\U0001f5fa\ufe0f", # 🗺️
    "book":      "\U0001f4d6",       # 📖
    "bug":       "\U0001f41b",       # 🐛
    "memo":      "\U0001f4dd",       # 📝
    "mag":       "\U0001f50d",       # 🔍
    "test":      "\U0001f9ea",       # 🧪
    "recycle":   "\u267b\ufe0f",     # ♻️
    "bulb":      "\U0001f4a1",       # 💡
    "floppy":    "\U0001f4be",       # 💾
    "clipboard": "\U0001f4cb",       # 📋
}

# ASCII fallbacks for terminals that don't support emoji
# FIX: removed duplicate "recycle" key — "[R]" was silently overwritten by "[REBUILD]"
_ASCII_ICONS = {
    "folder":    "[DIR]",
    "file":      "[FILE]",
    "readme":    "[i]",
    "success":   "[OK]",
    "warning":   "[!]",
    "error":     "[X]",
    "rocket":    "[>>]",
    "chart":     "[#]",
    "target":    "[*]",
    "building":  "[B]",
    "map":       "[M]",
    "book":      "[B]",
    "bug":       "[bug]",
    "memo":      "[N]",
    "mag":       "[?]",
    "test":      "[T]",
    "recycle":   "[RECYCLE]",
    "bulb":      "[!]",
    "floppy":    "[S]",
    "clipboard": "[CLIP]",
}

# Select the right icon set for the current terminal
EMOJI = _EMOJI_ICONS if _supports_emoji() else _ASCII_ICONS
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
from typing import List, Optional, Set

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

        # Compression (v4.5) — initialised once so parsers load a single time
        self.compressor = None
        if config.compress:
            from .compressor import CodeCompressor
            self.compressor = CodeCompressor(config.extensions)

    def _collect_all_files(self) -> Set[str]:
        """Collect all candidate files without processing them."""
        result: Set[str] = set()
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
        When compression is active, reduces content to signatures + docstrings.
        """
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

        # Compression injection — skipped for truncated files to avoid double-mangling
        if self.compressor is not None and not is_truncated:
            content = self.compressor.compress(content, file_path)

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
            compress_tag = " [compressed]" if self.compressor else ""
            print(f"  {EMOJI['success']} {Path(file_path).name} ({line_count:,} lines{compress_tag})")

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
            compress_info = f" (compress={self.config.compress_level})" if self.config.compress else ""
            print(f"\n{EMOJI['rocket']} Starting assembly{compress_info}...\n")

        for path in self.config.paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                if self._matches_file(Path(path)):
                    self.process_file(path)
            elif os.path.isdir(path):
                self.process_directory(path)

        full_content = "".join(self.content_buffer)
        self.stats.total_chars = len(full_content)
        self.stats.estimated_tokens = estimate_tokens(full_content)

        toc = self.formatter.generate_toc(self.toc_entries)
        analyzer = ArchitectureAnalyzer(self.toc_entries, self.stats)
        archi_data = analyzer.analyze_data()
        architecture_md = self.formatter.render("components/architecture.md.j2", archi_data)

        header = self.formatter.generate_header(self.stats, self.config, toc, architecture_md)
        if delta_summary:
            header = header.replace("---", f"{delta_summary}\n\n---", 1)

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
        if self.config.compress:
            print(f"   {EMOJI['recycle']} Compression: {self.config.compress_level}")


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

    if not write_file_content(output, content):
        raise OSError(f"Failed to write output file: {output}")

    if config.show_progress:
        print(f"\n{EMOJI['floppy']} Saved: {output}\n")

    return content


def assemble_from_config(
        config_file: str,
        since: Optional[str] = None,
        **cli_overrides
) -> str:
    """
    Assemble codebase using a JSON configuration file.

    CLI flags passed as keyword arguments take precedence over values
    in the JSON config file. This allows combining --config with flags
    like --compress without modifying the config file.

    Example:
        assemble_from_config("config.json", since="prev.md", compress=True)
    """
    import json
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # Normalise output key
    if 'output_file' in config_data and 'output' not in config_data:
        config_data['output'] = config_data.pop('output_file')
    elif 'output_file' in config_data:
        config_data.pop('output_file')

    # CLI overrides win over JSON values — only apply truthy/explicit values
    # so that a bare --compress=False doesn't accidentally disable JSON compress:true
    for key, value in cli_overrides.items():
        if value is not None:
            config_data[key] = value

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
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Tuple

_METADATA_RE = re.compile(r'<!-- CODE_ASSEMBLER_METADATA\s+(.*?)\s+-->', re.DOTALL)


def extract_metadata(md_file: str) -> Dict[str, datetime]:
    """Extract the {path: datetime} dict from the hidden metadata block."""
    result: Dict[str, datetime] = {}
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        match = _METADATA_RE.search(content)
        if not match:
            # Old snapshot without metadata — caller treats all files as new
            return result

        data = json.loads(match.group(1))
        for path, date_str in data.get('files', {}).items():
            try:
                result[path] = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                continue

    except FileNotFoundError:
        pass  # Safe: caller checks existence before calling in most paths
    except PermissionError as exc:
        # FIX: was bare `except Exception: pass` — real errors now surface
        print(f"  [!] Cannot read snapshot (permission denied): {exc}")
    except json.JSONDecodeError as exc:
        print(f"  [!] Snapshot metadata is corrupted (invalid JSON): {exc}")
    except Exception as exc:
        print(f"  [!] Unexpected error reading snapshot metadata: {exc}")

    return result


def normalize_key(path: str) -> str:
    """Normalize a path to lowercase forward-slash form."""
    return str(Path(path)).replace('\\', '/').lower().strip('/')


def get_delta(md_file: str, current_files: Set[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    snapshot = extract_metadata(md_file)

    # No metadata → treat everything as new (backwards compat with old snapshots)
    if not snapshot:
        return set(current_files), set(current_files), set()

    modified: Set[str] = set()
    added: Set[str] = set()
    deleted: Set[str] = set()
    matched_keys: Set[str] = set()

    if current_files:
        try:
            common_root = os.path.commonpath(list(current_files))
            if os.path.isfile(common_root):
                common_root = os.path.dirname(common_root)
        except ValueError:
            common_root = os.getcwd()
    else:
        common_root = os.getcwd()

    for abs_path in current_files:
        try:
            rel_path = os.path.relpath(abs_path, common_root).replace('\\', '/')
            if rel_path.startswith('./'):
                rel_path = rel_path[2:]
        except ValueError:
            rel_path = normalize_key(abs_path)

        match_key = None

        if rel_path in snapshot:
            match_key = rel_path
        else:
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

    for snap_key in snapshot:
        if snap_key not in matched_keys:
            deleted.add(snap_key)

    return modified, added, deleted


def _has_changed(abs_path: str, snapshot_dt: datetime) -> bool:
    try:
        current_mtime = datetime.fromtimestamp(
            os.path.getmtime(abs_path)
        ).replace(second=0, microsecond=0)
        snapshot_mtime = snapshot_dt.replace(second=0, microsecond=0)
        return current_mtime != snapshot_mtime
    except OSError:
        return True


def filter_changed_files(md_file: str, all_files: Set[str]) -> Tuple[Set[str], Set[str]]:
    modified, added, deleted = get_delta(md_file, all_files)
    return modified | added, deleted


def format_delta_summary(modified: Set[str], added: Set[str], deleted: Set[str]) -> str:
    lines = []

    def _fmt(files: Set[str], label: str, icon: str) -> None:
        if not files:
            return
        count = len(files)
        names = sorted(Path(p).name for p in files)
        disp = ', '.join(names[:5]) + (f", ... (+{count - 5})" if count > 5 else "")
        lines.append(f"> {icon} {label} ({count}): {disp}")

    _fmt(modified, "Modified", "✏️ ")
    _fmt(added, "Added", "➕")
    _fmt(deleted, "Deleted", "❌")

    if not lines:
        lines.append("> ✅ No changes detected since last snapshot")
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
    """Interactive configuration wizard for Code Assembler Pro."""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.available_extensions = self._get_available_extensions()

    def _get_available_extensions(self) -> List[str]:
        return sorted(list(set(LANGUAGE_MAP.keys())))

    def _print_banner(self):
        print("\n" + "=" * 70)
        print(f"{EMOJI['rocket']}  Code Assembler Pro - Interactive Mode")
        print("=" * 70)
        print("\nWelcome! This wizard will help you configure your codebase assembly.")
        print("Press Ctrl+C at any time to cancel.\n")

    def _print_section(self, title: str):
        print(f"\n{EMOJI['target']} {title}")
        print("-" * 70)

    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
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
        if default:
            response = input(f"{question} [default: {default}]: ").strip()
            return response if response else default
        else:
            return input(f"{question}: ").strip()

    def _select_paths(self) -> List[str]:
        self._print_section("Step 1: Select Paths to Analyze")
        print("\nYou can analyze:")
        print("  1. Current directory (.)")
        print("  2. Specific directory/directories")
        print("  3. Specific files")

        paths: List[str] = []
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
            ext = ext.strip().rstrip(',')
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.append(ext)

        if not extensions:
            print(f"{EMOJI['warning']}  No extensions selected, using .py as default")
            extensions = [".py"]
        return extensions

    def _configure_exclusions(self) -> List[str]:
        """
        Configure exclusion patterns.

        FIX: previously the wizard merged DEFAULT_EXCLUDE_PATTERNS here, but
        AssemblerConfig also added them again (use_default_excludes defaults to
        True), causing double-inclusion. The wizard now owns the full list and
        signals AssemblerConfig to skip its own merge (use_default_excludes=False
        is set in run()).
        """
        self._print_section("Step 3: Configure Exclusions")
        print("\nDefault exclusions:")
        print(f"  {', '.join(DEFAULT_EXCLUDE_PATTERNS[:10])}")
        if len(DEFAULT_EXCLUDE_PATTERNS) > 10:
            print(f"  ... and {len(DEFAULT_EXCLUDE_PATTERNS) - 10} more")

        use_defaults = self._ask_yes_no("\nUse default exclusions?", default=True)

        custom_patterns: List[str] = []
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
        return custom_patterns

    def _configure_output(self) -> str:
        self._print_section("Step 4: Output Configuration")
        output = self._ask_text("\nOutput filename", default="codebase.md")
        if not output.endswith('.md'):
            output += '.md'

        if os.path.exists(output):
            if not self._ask_yes_no(
                f"{EMOJI['warning']}  '{output}' already exists. Overwrite?", default=False
            ):
                counter = 1
                while os.path.exists(f"codebase_{counter}.md"):
                    counter += 1
                output = f"codebase_{counter}.md"
                print(f"{EMOJI['success']} Using: {output}")
        return output

    def _configure_advanced(self) -> Dict[str, Any]:
        self._print_section("Step 5: Advanced Options")
        advanced: Dict[str, Any] = {}

        if self._ask_yes_no("\nConfigure advanced options?", default=False):
            advanced['recursive'] = self._ask_yes_no(
                "  Recursively traverse subdirectories?", default=True
            )
            advanced['include_readmes'] = self._ask_yes_no(
                "  Automatically include README files?", default=True
            )
            print("\n  File size handling:")
            advanced['max_file_size_mb'] = self._ask_number(
                "    Maximum file size (MB)", default=10.0, min_val=0.1
            )
            advanced['truncate_large_files'] = self._ask_yes_no(
                "    Truncate large files instead of skipping?", default=True
            )
            if advanced['truncate_large_files']:
                advanced['truncation_limit_lines'] = int(self._ask_number(
                    "      Keep first N lines when truncating", default=500, min_val=10
                ))
        else:
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
            patterns = self.config['exclude_patterns']
            print(f"\n{EMOJI['error']} Exclusions: {len(patterns)} patterns")
            for pattern in patterns[:5]:
                print(f"   - {pattern}")
            if len(patterns) > 5:
                print(f"   ... and {len(patterns) - 5} more")

    def _save_config(self):
        if self._ask_yes_no(
            f"\n{EMOJI['floppy']} Save this configuration for future use?", default=False
        ):
            import json
            config_name = self._ask_text("Configuration filename", default="assembler_config.json")
            if not config_name.endswith('.json'):
                config_name += '.json'

            save_config = {k: v for k, v in self.config.items() if k != 'show_progress'}
            with open(config_name, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=2, ensure_ascii=False)

            print(f"{EMOJI['success']} Configuration saved to: {config_name}")
            print(f"   Reuse it with: code-assembler --config {config_name}")

    def run(self) -> Optional[str]:
        """Run the interactive wizard."""
        try:
            self._print_banner()

            self.config['paths'] = self._select_paths()
            self.config['extensions'] = self._select_extensions()

            exclude_patterns = self._configure_exclusions()
            self.config['exclude_patterns'] = exclude_patterns
            # FIX: wizard manages the full exclusion list itself (with or without
            # defaults). Tell AssemblerConfig not to add DEFAULT_EXCLUDE_PATTERNS
            # a second time, which would cause silent duplication.
            self.config['use_default_excludes'] = False

            self.config['output'] = self._configure_output()

            advanced = self._configure_advanced()
            self.config.update(advanced)

            self._show_summary()

            if not self._ask_yes_no(f"\n{EMOJI['rocket']} Start assembly?", default=True):
                print(f"\n{EMOJI['error']} Assembly cancelled.")
                return None

            self._save_config()

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
    """Entry point for interactive mode."""
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

    def _find_real_file_headers(self) -> List[Tuple[str, int, int]]:
        """
        Scan the whole document once for genuine file-header blocks:
        a '#+ `path`' line immediately followed (at most one blank line
        between) by an opening code fence.

        That tight anchoring — no free-form text allowed between the
        header and the fence — is what filters out prose headings that
        merely *wrap* an identifier in backticks (e.g. "#### `@Contract.
        validate` and `self` in tests"), since those are followed by
        ordinary paragraph text, not directly by a fence. It deliberately
        does NOT require `path` to be a key in the embedded metadata: some
        real header blocks are directory-level README context sections
        (e.g. "#### `behavioral/`" → "##### README context") rather than
        individual files, and excluding them would make this scan skip
        over a real document boundary, silently swallowing the README
        section into whatever file happens to precede it.

        Returns a list of (path, header_start, content_start) ordered by
        position in the document. Used both to locate a specific file's
        content and to bound where each block ends (the next entry's start
        is the bound for the previous one).
        """
        header_re = re.compile(
            r'#+ `([^`]+)`[ \t]*\r?\n(?:[ \t]*\r?\n)?```[a-z0-9]*\r?\n',
            re.IGNORECASE
        )
        return [
            (m.group(1).strip().replace('\\', '/'), m.start(), m.end())
            for m in header_re.finditer(self.md_content)
        ]

    def _extract_file_content(self, rel_path: str) -> Optional[str]:
        """
        Find and extract the content of a specific file from the Markdown.
        Robust against path separators, blank lines, duplicate filenames at
        different paths, and nested ``` fences inside the file's own content
        (a markdown file documenting code blocks, a README showing
        examples, etc. — see `_find_real_file_headers` for why a single
        validated scan is used instead of a per-call regex search).
        """
        target_normalized = rel_path.replace('\\', '/').strip()
        headers = self._find_real_file_headers()

        match_index = next(
            (i for i, (path, _, _) in enumerate(headers) if path == target_normalized),
            None
        )
        if match_index is None:
            return None

        _, _, content_start = headers[match_index]
        content_end_bound = (
            headers[match_index + 1][1] if match_index + 1 < len(headers) else len(self.md_content)
        )
        search_zone = self.md_content[content_start:content_end_bound]

        # True closing fence = the LAST bare ``` line in the window, since
        # earlier ones may be nested fences belonging to the file's own
        # content rather than the block's real terminator.
        closing_candidates = list(re.finditer(r'\r?\n```[ \t]*(?:\r?\n|$)', search_zone))
        if not closing_candidates:
            return None

        last_closing = closing_candidates[-1]
        return search_zone[:last_closing.start()]

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

# Timeout (seconds) for clipboard subprocess calls.
# Prevents infinite blocking if a clipboard manager hangs.
_CLIPBOARD_TIMEOUT = 10


def normalize_path(path: str) -> str:
    """
    Normalize a path to a consistent POSIX-style lowercase string.
    Does NOT resolve against CWD to avoid environment-dependent behavior.
    """
    if not path:
        return ""
    return str(PurePosixPath(path)).replace("\\", "/").lower().rstrip("/")


def slugify_path(path: str) -> str:
    """Convert a file path to a valid HTML anchor identifier."""
    return re.sub(r'[^a-zA-Z0-9]', '_', path).lower()


def should_exclude(path: str, exclude_patterns: List[str]) -> bool:
    """Determine if a path should be excluded based on patterns."""
    if not exclude_patterns:
        return False

    path_norm = normalize_path(path)
    path_parts: List[str] = [p for p in path_norm.split("/") if p]

    for pattern in exclude_patterns:
        if not pattern:
            continue

        clean_pattern = pattern.lower().rstrip("/")

        if "/" in clean_pattern or "\\" in clean_pattern:
            pattern_norm = normalize_path(clean_pattern)
            if path_norm == pattern_norm:
                return True
            if ("/" + pattern_norm + "/") in ("/" + path_norm + "/"):
                return True
            continue

        for part in path_parts:
            if part == clean_pattern:
                return True
            if "*" in clean_pattern or "?" in clean_pattern:
                if fnmatch.fnmatch(part, clean_pattern):
                    return True
            if clean_pattern.startswith(".") and part.endswith(clean_pattern):
                return True

    return False


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text (~4 chars per token)."""
    return len(text) // CHARS_PER_TOKEN


def format_file_size(size_bytes: int) -> str:
    """Format a file size in human-readable format."""
    if size_bytes == 0:
        return "0B"
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}" if unit != 'B' else f"{int(size)}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


def format_number(num: int) -> str:
    """Format a number with thousands separators."""
    return f"{num:,}"


def get_file_extension(path: str) -> str:
    """Get the file extension from a path."""
    return Path(path).suffix


def count_lines(text: str) -> int:
    """Count the number of lines in a text."""
    return len(text.splitlines())


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to the system clipboard without external dependencies.
    Handles Unicode characters correctly on Windows, macOS, and Linux.
    """
    system = platform.system()
    try:
        if system == "Windows":
            command = [
                "powershell", "-NoProfile", "-Command",
                "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
                "$input | Out-String | Set-Clipboard"
            ]
            subprocess.run(
                command, input=text, encoding='utf-8',
                check=True, timeout=_CLIPBOARD_TIMEOUT
            )

        elif system == "Darwin":  # macOS
            subprocess.run(
                "pbcopy", input=text, text=True,
                check=True, timeout=_CLIPBOARD_TIMEOUT
            )

        elif system == "Linux":
            # FIX: previously only fell back to xsel on FileNotFoundError.
            # If xclip is installed but fails (no DISPLAY, permission, etc.),
            # CalledProcessError was caught by the outer except, returning False
            # without ever trying xsel. Now ANY failure from xclip triggers xsel.
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text, text=True,
                    check=True, timeout=_CLIPBOARD_TIMEOUT
                )
            except (FileNotFoundError, subprocess.CalledProcessError,
                    subprocess.TimeoutExpired):
                subprocess.run(
                    ["xsel", "--clipboard", "--input"],
                    input=text, text=True,
                    check=True, timeout=_CLIPBOARD_TIMEOUT
                )

        return True

    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired, OSError):
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

## `docs\INTERACTIVE_DEMO.md`

```markdown
# 🎬 Interactive Mode - Visual Demo

This document shows a complete interactive wizard session from start to finish.

---

## 📺 Complete Session Recording

```
$ code-assembler --interactive

══════════════════════════════════════════════════════════════════════
🚀  Code Assembler Pro - Interactive Mode
══════════════════════════════════════════════════════════════════════

Welcome! This wizard will help you configure your codebase assembly.
Press Ctrl+C at any time to cancel.


🎯 Step 1: Select Paths to Analyze
──────────────────────────────────────────────────────────────────────

You can analyze:
  1. Current directory (.)
  2. Specific directory/directories
  3. Specific files

Your choice [1-3]: 2

Enter directory paths (one per line, empty line to finish):
  Path: ./src
  ✅ Added: ./src
  Path: ./docs
  ✅ Added: ./docs
  Path: 


🎯 Step 2: Select File Extensions
──────────────────────────────────────────────────────────────────────

Common presets:
  1. Python projects (.py)
  2. Python + Config + Docs (.py, .md, .toml, .yaml)
  3. JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
  4. Rust projects (.rs, .toml)
  5. Go projects (.go, .mod)
  6. Java projects (.java)
  7. C/C++ projects (.c, .cpp, .h, .hpp)
  8. Custom selection

Your choice [1-8]: 2
✅ Selected: Python + Config + Docs


🎯 Step 3: Configure Exclusions
──────────────────────────────────────────────────────────────────────

Default exclusions:
  __pycache__, .pyc, .pyo, .pyd, .so, .dll, .dylib, .egg-info, .eggs, dist

Use default exclusions? [Y/n]: y

Add custom exclusion patterns? [y/N]: y

Enter patterns (one per line, empty line to finish):
Examples: tests/, *.log, secret.py, temp_*
  Pattern: experiments/
  ✅ Added: experiments/
  Pattern: *.backup
  ✅ Added: *.backup
  Pattern: 


🎯 Step 4: Output Configuration
──────────────────────────────────────────────────────────────────────

Output filename [default: codebase.md]: project_context.md


🎯 Step 5: Advanced Options
──────────────────────────────────────────────────────────────────────

Configure advanced options? [y/N]: y

  Recursively traverse subdirectories? [Y/n]: y
  Automatically include README files? [Y/n]: y

  File size handling:
    Maximum file size (MB) [default: 10.0]: 5.0
    Truncate large files instead of skipping? [Y/n]: y
      Keep first N lines when truncating [default: 500]: 300


🎯 Configuration Summary
──────────────────────────────────────────────────────────────────────

📂 Paths: ./src, ./docs
📝 Extensions: .py, .md, .toml, .yaml
💾 Output: project_context.md
🔧 Recursive: True
📖 Include READMEs: True
📏 Max file size: 5.0 MB
✂️  Truncate large files: True
   Keep first 300 lines

🚫 Exclusions: 13 patterns
   - __pycache__
   - .pyc
   - .git
   - .venv
   - node_modules
   ... and 8 more

🚀 Start assembly? [Y/n]: y

💾 Save this configuration for future use? [y/N]: y
Configuration filename [default: assembler_config.json]: my_project_config.json
✅ Configuration saved to: my_project_config.json
   Reuse it with: code-assembler --config my_project_config.json

🚀 Starting assembly...

📂 Processing: ./src

  📁 code_assembler
  ℹ️  README found: README.md
  ✅ __init__.py (14 lines)
  ✅ config.py (136 lines)
  ✅ constants.py (201 lines)
  ✅ core.py (278 lines)
  ✅ file_io.py (83 lines)
  ✅ formatters.py (136 lines)
  ✅ utils.py (110 lines)
  ✅ analyzers.py (152 lines)
  ✅ cli.py (141 lines)
  ✅ interactive.py (425 lines)

📂 Processing: ./docs

  ✅ ARCHITECTURE.md (89 lines)
  ✅ API.md (124 lines)

✅ Assembly completed!

📊 Summary:
   📄 Files: 12
   📏 Lines: 1,889
   💾 Size: 67.3KB
   🎯 Tokens: ~16,825

💾 Saved: project_context.md

```

---

## 🎨 Key Features Demonstrated

### 1. **Smart Path Selection**
- Multiple directories (`./src`, `./docs`)
- Validation of existing paths
- Clear feedback on each addition

### 2. **Extension Presets**
- One-click selection for common project types
- Preset #2 chosen: Python + Config + Docs
- Includes: `.py`, `.md`, `.toml`, `.yaml`

### 3. **Flexible Exclusions**
- Default patterns automatically applied
- Custom additions: `experiments/`, `*.backup`
- Clear count in summary (13 patterns total)

### 4. **Advanced Configuration**
- Custom file size limit (5 MB instead of 10 MB)
- Truncation enabled with 300-line limit
- All options clearly explained

### 5. **Configuration Saving**
- Saved as `my_project_config.json`
- Clear instructions for reuse
- Reusable for future assemblies

### 6. **Real-time Progress**
- Folder-by-folder breakdown
- README detection notifications
- Per-file success indicators
- Final statistics summary

---

## 📋 Generated Configuration File

The wizard created this `my_project_config.json`:

```json
{
  "paths": [
    "./src",
    "./docs"
  ],
  "extensions": [
    ".py",
    ".md",
    ".toml",
    ".yaml"
  ],
  "exclude_patterns": [
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
    ".venv",
    "node_modules",
    "experiments/",
    "*.backup"
  ],
  "output": "project_context.md",
  "recursive": true,
  "include_readmes": true,
  "max_file_size_mb": 5.0,
  "truncate_large_files": true,
  "truncation_limit_lines": 300
}
```

**Reuse it:**
```bash
code-assembler --config my_project_config.json
```

---

## 🔁 Variations

### Quick Start (All Defaults)

```
Your choice [1-3]: 1
Your choice [1-8]: 1
Use default exclusions? [Y/n]: 
Add custom exclusion patterns? [y/N]: 
Output filename [default: codebase.md]: 
Configure advanced options? [y/N]: 
🚀 Start assembly? [Y/n]: 
💾 Save this configuration for future use? [y/N]: 
```

Just 7 Enter presses! ⚡

### Minimal Input (Current Dir + Python)

```
$ code-assembler -i
[Step 1] Your choice: 1         # Current directory
[Step 2] Your choice: 1         # Python only
[Step 3] Use defaults: <Enter>  # Yes to defaults
[Step 3] Custom patterns: <Enter> # No custom
[Step 4] Filename: <Enter>      # Use default
[Step 5] Advanced: <Enter>      # Use defaults
[Confirm] Start: <Enter>        # Yes, start
[Save] Config: <Enter>          # Don't save

Done! → codebase.md created
```

---

## 💡 Tips from the Demo

1. **Start with Presets** - Preset #2 (Python + Config) covers 80% of Python projects
2. **Always Use Default Exclusions** - They filter out build artifacts and dependencies
3. **Add Custom Exclusions Sparingly** - Only add project-specific patterns
4. **Save Configurations** - Reuse them for regular project updates
5. **Enable Truncation** - Keeps token count manageable for large codebases

---

## 🎓 Next Steps

Try it yourself:
```bash
code-assembler --interactive
```

Or run the demo script:
```bash
python examples/interactive_demo.py
```

---

**Interactive Mode** — *Configuration in under 60 seconds.* ⚡
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
                check=True,
                timeout=10
            )

    @patch('subprocess.run')
    def test_copy_to_clipboard_mac(self, mock_run):
        """Test clipboard call on macOS using pbcopy."""
        with patch('platform.system', return_value='Darwin'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            mock_run.assert_called_once_with(
                "pbcopy", input="test content", text=True, check=True, timeout=10
            )

    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xclip(self, mock_run):
        """Test clipboard call on Linux using xclip."""
        with patch('platform.system', return_value='Linux'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            mock_run.assert_called_with(
                ["xclip", "-selection", "clipboard"],
                input="test content", text=True, check=True, timeout=10
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
            since=None,
            compress=False,
            compress_level="signatures"
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

## `tests\test_compressor.py`

```python
"""
Tests for the compression module (CodeCompressor).

Python compression via stdlib ast is always tested (no external deps).
Tree-sitter paths are tested via mocks to avoid requiring installed parsers.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.compressor import CodeCompressor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_compressor(extensions=None) -> CodeCompressor:
    """Create a CodeCompressor without loading any tree-sitter parsers."""
    extensions = extensions or [".py"]
    # Patch _load_parsers to avoid real imports during unit tests
    with patch.object(CodeCompressor, "_load_parsers"):
        c = CodeCompressor(extensions)
    return c


# ---------------------------------------------------------------------------
# Python AST compression — no external dependency needed
# ---------------------------------------------------------------------------

class TestPythonASTCompression(unittest.TestCase):

    def setUp(self):
        self.c = make_compressor([".py"])

    def _compress(self, source: str) -> str:
        return self.c._compress_python_ast(source)

    # --- Basic function ---

    def test_function_body_replaced(self):
        source = (
            "def add(a, b):\n"
            "    result = a + b\n"
            "    return result\n"
        )
        result = self._compress(source)
        self.assertIn("def add(a, b):", result)
        self.assertIn("...", result)
        self.assertNotIn("result = a + b", result)
        self.assertNotIn("return result", result)

    def test_function_signature_preserved(self):
        source = (
            "def greet(name: str, greeting: str = 'Hello') -> str:\n"
            "    return f'{greeting}, {name}!'\n"
        )
        result = self._compress(source)
        self.assertIn("def greet(name: str, greeting: str = 'Hello') -> str:", result)

    def test_docstring_preserved(self):
        source = (
            "def compute(x):\n"
            "    \"\"\"Compute the result.\"\"\"\n"
            "    return x * 2\n"
        )
        result = self._compress(source)
        self.assertIn("Compute the result.", result)
        self.assertIn("...", result)
        self.assertNotIn("x * 2", result)

    def test_function_only_docstring(self):
        """A function whose body IS only a docstring should not add '...'."""
        source = (
            "def documented():\n"
            "    \"\"\"This function is abstract.\"\"\"\n"
        )
        result = self._compress(source)
        self.assertIn("This function is abstract.", result)
        # No extra ... needed — body is only the docstring
        lines = [l.strip() for l in result.splitlines() if l.strip()]
        self.assertNotIn("...", lines)

    def test_async_function(self):
        source = (
            "async def fetch(url: str):\n"
            "    response = await client.get(url)\n"
            "    return response.json()\n"
        )
        result = self._compress(source)
        self.assertIn("async def fetch(url: str):", result)
        self.assertIn("...", result)
        self.assertNotIn("response = await", result)

    # --- Class handling ---

    def test_class_methods_compressed(self):
        source = (
            "class Calculator:\n"
            "    def add(self, a, b):\n"
            "        return a + b\n"
            "    def sub(self, a, b):\n"
            "        return a - b\n"
        )
        result = self._compress(source)
        self.assertIn("class Calculator:", result)
        self.assertIn("def add(self, a, b):", result)
        self.assertIn("def sub(self, a, b):", result)
        self.assertNotIn("return a + b", result)
        self.assertNotIn("return a - b", result)

    def test_class_docstring_preserved(self):
        source = (
            "class MyClass:\n"
            "    \"\"\"Class-level docstring.\"\"\"\n"
            "    def method(self):\n"
            "        pass\n"
        )
        result = self._compress(source)
        self.assertIn("Class-level docstring.", result)

    def test_class_method_docstring_preserved(self):
        source = (
            "class Foo:\n"
            "    def bar(self):\n"
            "        \"\"\"Method doc.\"\"\"\n"
            "        x = 1\n"
            "        return x\n"
        )
        result = self._compress(source)
        self.assertIn("Method doc.", result)
        self.assertNotIn("x = 1", result)

    # --- Top-level code ---

    def test_imports_preserved(self):
        source = (
            "import os\n"
            "from pathlib import Path\n"
            "\n"
            "def foo():\n"
            "    return 42\n"
        )
        result = self._compress(source)
        self.assertIn("import os", result)
        self.assertIn("from pathlib import Path", result)

    def test_module_constants_preserved(self):
        source = (
            "VERSION = '1.0.0'\n"
            "DEBUG = False\n"
            "\n"
            "def main():\n"
            "    print(VERSION)\n"
        )
        result = self._compress(source)
        self.assertIn("VERSION = '1.0.0'", result)
        self.assertIn("DEBUG = False", result)
        self.assertNotIn("print(VERSION)", result)

    # --- Edge cases ---

    def test_syntax_error_returns_original(self):
        """Invalid Python should be returned as-is without raising."""
        source = "def broken(\n    missing closing\n"
        result = self._compress(source)
        self.assertEqual(result, source)

    def test_empty_source(self):
        result = self._compress("")
        self.assertEqual(result, "")

    def test_indentation_correct(self):
        """The '...' placeholder must be at the right indentation level."""
        source = (
            "class Outer:\n"
            "    def method(self):\n"
            "        x = 1\n"
            "        return x\n"
        )
        result = self._compress(source)
        # '...' should be indented 8 spaces (class 0 + method 4 + body 4)
        self.assertIn("        ...", result)


# ---------------------------------------------------------------------------
# compress() dispatcher
# ---------------------------------------------------------------------------

class TestCompressDispatcher(unittest.TestCase):

    def setUp(self):
        self.c = make_compressor([".py", ".js"])

    def test_python_file_dispatched_to_ast(self):
        source = "def foo():\n    return 1\n"
        result = self.c.compress(source, "script.py")
        self.assertIn("def foo():", result)
        self.assertIn("...", result)

    def test_unknown_extension_returns_original(self):
        source = "some content"
        result = self.c.compress(source, "file.xyz")
        self.assertEqual(result, source)

    def test_no_parser_for_lang_returns_original(self):
        """JS file without a loaded parser should pass through unchanged."""
        source = "function foo() { return 1; }"
        # No parsers loaded (mocked _load_parsers), so JS falls through
        result = self.c.compress(source, "app.js")
        self.assertEqual(result, source)

    def test_treesitter_exception_returns_original(self):
        """If tree-sitter raises, compress() must return the original content."""
        source = "function broken() {}"
        # Inject a fake parser that raises
        bad_parser = MagicMock()
        bad_parser.parse.side_effect = RuntimeError("parser exploded")
        self.c.parsers["javascript"] = bad_parser

        result = self.c.compress(source, "app.js")
        self.assertEqual(result, source)


# ---------------------------------------------------------------------------
# Parser loading — mocked to avoid requiring installed packages
# ---------------------------------------------------------------------------

class TestParserLoading(unittest.TestCase):

    def test_missing_package_reported(self):
        """Missing tree-sitter language package should be recorded, not raise."""
        try:
            from tree_sitter import Language, Parser  # noqa
            ts_available = True
        except ImportError:
            ts_available = False

        if not ts_available:
            self.skipTest("tree-sitter core not installed — skipping")

        # Patch only the compressor module's import_module, not the global one
        with patch(
            "code_assembler.compressor.importlib.import_module",
            side_effect=ImportError("no module"),
        ):
            with patch("builtins.print"):  # suppress console output
                c = CodeCompressor([".js"])

        self.assertNotIn("javascript", c.parsers)
        self.assertTrue(len(c._missing_packages) > 0)

    def test_python_never_needs_treesitter(self):
        """Python extension should not trigger any tree-sitter load attempt."""
        with patch("importlib.import_module") as mock_import:
            c = CodeCompressor([".py"])
            # tree-sitter modules should NOT have been imported for Python
            ts_calls = [
                call for call in mock_import.call_args_list
                if "tree_sitter" in str(call)
            ]
            self.assertEqual(len(ts_calls), 0)


if __name__ == "__main__":
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


class TestRebuildRegressions(unittest.TestCase):
    """
    Regression tests for three bugs found in _extract_file_content() while
    rebuilding real-world snapshots:

      1. A non-greedy '(.*?)\\n```' capture stopped at the FIRST closing
         fence, even when that fence was nested inside the file's own
         content (e.g. a .md file documenting a code example).
      2. An unanchored '.*?' between a file's header and its opening fence
         let the search latch onto a prose heading that merely wraps an
         identifier in backticks (e.g. "#### `@Contract.validate` and
         `self` in tests"), followed later by an unrelated code block.
      3. Matching by filename substring caused collisions between files
         sharing the same name at different paths (multiple
         `pyproject.toml` in one monorepo snapshot, for example).

    These tests build raw Markdown snapshots directly (rather than going
    through `_create_mock_md`, whose helper always wraps a single flat
    string in one fence per file) because reproducing the bugs requires
    nested fences and multi-block documents that helper cannot express.
    """

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.output_dir = self.root / "restored"
        self.md_file = self.root / "snapshot.md"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _write(self, raw_markdown: str, files: dict):
        """Write a raw snapshot body plus a matching metadata block."""
        metadata = {
            "version": "4.5.1",
            "generated_at": "2026-01-01 10:00:00",
            "files": files,
        }
        full = raw_markdown + f"\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(metadata)}\n-->\n"
        self.md_file.write_text(full, encoding='utf-8')

    def test_nested_fence_inside_file_content(self):
        """
        A markdown file whose own content contains a fenced code example
        must be extracted in full, not truncated at the first nested
        closing fence.
        """
        raw = (
            "# Consolidated Codebase\n\n"
            "## Table of Contents\n\n"
            "- `docs/guide.md` | 2026-01-01 10:00\n"
            "- `src/next_file.py` | 2026-01-01 10:00\n\n"
            "---\n\n"
            "### `docs/guide.md`\n\n"
            "```markdown\n"
            "# Guide\n\n"
            "Here is an example:\n\n"
            "```python\n"
            "print(\"nested fence\")\n"
            "```\n\n"
            "End of guide.\n"
            "```\n\n"
            "### `src/next_file.py`\n\n"
            "```python\n"
            "print(\"next file content\")\n"
            "```\n"
        )
        self._write(raw, {
            "docs/guide.md": "2026-01-01 10:00",
            "src/next_file.py": "2026-01-01 10:00",
        })

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

        guide = (self.output_dir / "docs/guide.md").read_text()
        self.assertIn("End of guide.", guide)
        self.assertIn('print("nested fence")', guide)

        next_file = (self.output_dir / "src/next_file.py").read_text()
        self.assertEqual(next_file, 'print("next file content")')

    def test_prose_heading_with_backticks_is_not_a_file_boundary(self):
        """
        A markdown sub-heading that wraps an identifier in backticks (and
        is itself followed, later in the same paragraph, by an unrelated
        code block) must not be mistaken for the next file's header — the
        first file's content must include everything up to its own real
        closing fence.
        """
        raw = (
            "# Consolidated Codebase\n\n"
            "## Table of Contents\n\n"
            "- `core/contracts.md` | 2026-01-01 10:00\n"
            "- `core/next.py` | 2026-01-01 10:00\n\n"
            "---\n\n"
            "### `core/contracts.md`\n\n"
            "```markdown\n"
            "# Contracts\n\n"
            "#### `@Contract.validate` and `self` in tests\n\n"
            "When used at module level this works as expected. Example:\n\n"
            "```python\n"
            "def my_rule(inputs, output):\n"
            "    pass\n"
            "```\n\n"
            "End of section.\n"
            "```\n\n"
            "### `core/next.py`\n\n"
            "```python\n"
            "print(\"real next file\")\n"
            "```\n"
        )
        self._write(raw, {
            "core/contracts.md": "2026-01-01 10:00",
            "core/next.py": "2026-01-01 10:00",
        })

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

        contracts = (self.output_dir / "core/contracts.md").read_text()
        self.assertIn("End of section.", contracts)
        self.assertNotIn("real next file", contracts)

        next_file = (self.output_dir / "core/next.py").read_text()
        self.assertEqual(next_file, 'print("real next file")')

    def test_duplicate_filename_at_different_paths(self):
        """
        Two files sharing the same name at different paths (a common
        monorepo pattern, e.g. several pyproject.toml) must each resolve
        to their own content — not whichever header the search happens to
        reach first.
        """
        raw = (
            "# Consolidated Codebase\n\n"
            "## Table of Contents\n\n"
            "- `pyproject.toml` | 2026-01-01 10:00\n"
            "- `sub/pyproject.toml` | 2026-01-01 10:00\n\n"
            "---\n\n"
            "### `sub/pyproject.toml`\n\n"
            "```toml\n"
            "[project]\n"
            "name = \"sub-package\"\n"
            "```\n\n"
            "### `pyproject.toml`\n\n"
            "```toml\n"
            "[project]\n"
            "name = \"root-package\"\n"
            "```\n"
        )
        self._write(raw, {
            "pyproject.toml": "2026-01-01 10:00",
            "sub/pyproject.toml": "2026-01-01 10:00",
        })

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

        root_toml = (self.output_dir / "pyproject.toml").read_text()
        sub_toml = (self.output_dir / "sub/pyproject.toml").read_text()

        self.assertIn("root-package", root_toml)
        self.assertNotIn("sub-package", root_toml)
        self.assertIn("sub-package", sub_toml)
        self.assertNotIn("root-package", sub_toml)


if __name__ == "__main__":
    unittest.main()
```

## `tests\test_robustness.py`

```python
"""
Robustness tests for Code Assembler Pro.

One test per bug fixed in the review — these are regression guards.
If any of these fail, a previously fixed bug has been reintroduced.

Bugs covered:
    [1] constants   — duplicate keys in LANGUAGE_MAP and EMOJI dicts
    [2] cli         — _show_excludes() missing → AttributeError
    [3] cli         — rebuild errors never displayed
    [4] config      — empty extension string → IndexError on ext[0]
    [5] analyzers   — os.path.commonpath crash on Windows multi-drive paths
    [6] delta       — bare except swallowing PermissionError and JSONDecodeError
    [7] utils       — Linux clipboard: xsel fallback only on FileNotFoundError
    [8] utils       — no timeout on subprocess → potential infinite hang
    [9] core        — write_file_content return value ignored → silent data loss
    [10] interactive — use_default_excludes double-application
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch, call

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# ---------------------------------------------------------------------------
# [1] constants — no duplicate keys
# ---------------------------------------------------------------------------

class TestConstantsNoDuplicates(unittest.TestCase):

    def test_language_map_no_duplicate_dot_properties(self):
        """'.properties' must appear exactly once in LANGUAGE_MAP."""
        from code_assembler.constants import LANGUAGE_MAP
        # Python dicts can't hold duplicate keys at runtime (last wins),
        # so we verify the value is what we expect and that the key exists.
        self.assertIn(".properties", LANGUAGE_MAP)
        self.assertEqual(LANGUAGE_MAP[".properties"], "properties")

    def test_language_map_no_duplicate_graphql(self):
        """'.graphql' and '.gql' must each map to 'graphql'."""
        from code_assembler.constants import LANGUAGE_MAP
        self.assertEqual(LANGUAGE_MAP[".graphql"], "graphql")
        self.assertEqual(LANGUAGE_MAP[".gql"], "graphql")

    def test_emoji_recycle_key_is_unique_and_correct(self):
        """
        'recycle' key must not be silently overwritten.
        The surviving value should be the recycling symbol ♻️ (u267b).
        """
        from code_assembler.constants import _EMOJI_ICONS, _ASCII_ICONS
        # Verify 'recycle' exists exactly once (Python dicts guarantee uniqueness
        # of keys, so if it was defined twice the count is still 1 — but we can
        # inspect the value to confirm the right one survived).
        self.assertIn("recycle", _EMOJI_ICONS)
        self.assertIn("recycle", _ASCII_ICONS)
        # The correct final value (not the overwritten 🔄)
        self.assertIn("\u267b", _EMOJI_ICONS["recycle"])  # ♻️
        # ASCII fallback should be a single predictable string, not "[R]" (overwritten)
        self.assertNotEqual(_ASCII_ICONS["recycle"], "[R]")

    def test_no_dead_header_levels_constant(self):
        """HEADER_LEVELS was dead code — it should no longer be exported."""
        import code_assembler.constants as c
        self.assertFalse(
            hasattr(c, "HEADER_LEVELS"),
            "HEADER_LEVELS is dead code and should have been removed"
        )


# ---------------------------------------------------------------------------
# [2] cli — _show_excludes must be callable without error
# ---------------------------------------------------------------------------

class TestCliShowExcludes(unittest.TestCase):

    def test_show_excludes_is_defined(self):
        """_show_excludes must exist in cli module (was missing → AttributeError)."""
        from code_assembler import cli
        self.assertTrue(
            callable(getattr(cli, "_show_excludes", None)),
            "_show_excludes is not defined in cli.py"
        )

    def test_show_excludes_prints_patterns(self):
        """_show_excludes must print at least some of the default patterns."""
        from code_assembler.cli import _show_excludes
        from code_assembler.constants import DEFAULT_EXCLUDE_PATTERNS

        with patch("sys.stdout", new=StringIO()) as fake_out:
            _show_excludes()
            output = fake_out.getvalue()

        # At least one default pattern should appear in the output
        self.assertTrue(
            any(p in output for p in DEFAULT_EXCLUDE_PATTERNS),
            "_show_excludes output doesn't mention any default exclusion pattern"
        )

    def test_main_show_excludes_does_not_crash(self):
        """--show-excludes via main() must not raise AttributeError."""
        from code_assembler.cli import main

        args = argparse.Namespace(
            show_excludes=True,
            interactive=False, config=None, rebuild=None,
            paths=[], extensions=None, output="codebase.md",
            exclude_patterns=None, recursive=True, include_readmes=True,
            use_default_excludes=True, max_size=10.0, since=None,
            clip=False, save_config=None, compress=False,
            compress_level="signatures",
        )
        with patch("code_assembler.cli.parse_args", return_value=args):
            with patch("sys.stdout", new=StringIO()):
                # Must not raise
                main()


# ---------------------------------------------------------------------------
# [3] cli — rebuild errors must be displayed
# ---------------------------------------------------------------------------

class TestCliRebuildErrorDisplay(unittest.TestCase):

    def test_rebuild_errors_are_printed(self):
        """Errors returned by rebuilder.rebuild() must be displayed to the user."""
        from code_assembler.cli import main

        args = argparse.Namespace(
            show_excludes=False, interactive=False, config=None,
            rebuild="fake.md", output_dir="./out", dry_run=False,
            paths=[], extensions=None, output="codebase.md",
            exclude_patterns=None, recursive=True, include_readmes=True,
            use_default_excludes=True, max_size=10.0, since=None,
            clip=False, save_config=None, compress=False,
            compress_level="signatures",
        )

        mock_rebuilder = MagicMock()
        mock_rebuilder.rebuild.return_value = (1, ["Content not found for: src/lost.py"])

        with patch("code_assembler.cli.parse_args", return_value=args):
            # FIX: CodebaseRebuilder is imported lazily inside main() so patch
            # the class in its source module, not in cli's namespace
            with patch("code_assembler.rebuilder.CodebaseRebuilder", return_value=mock_rebuilder):
                with patch("sys.stdout", new=StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()

        self.assertIn("lost.py", output, "Rebuild error was not printed to stdout")

    def test_rebuild_success_count_is_printed(self):
        """Successful rebuild should display file count."""
        from code_assembler.cli import main

        args = argparse.Namespace(
            show_excludes=False, interactive=False, config=None,
            rebuild="snap.md", output_dir="./restored", dry_run=False,
            paths=[], extensions=None, output="codebase.md",
            exclude_patterns=None, recursive=True, include_readmes=True,
            use_default_excludes=True, max_size=10.0, since=None,
            clip=False, save_config=None, compress=False,
            compress_level="signatures",
        )

        mock_rebuilder = MagicMock()
        mock_rebuilder.rebuild.return_value = (5, [])

        with patch("code_assembler.cli.parse_args", return_value=args):
            with patch("code_assembler.rebuilder.CodebaseRebuilder", return_value=mock_rebuilder):
                with patch("sys.stdout", new=StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()

        self.assertIn("5", output)


# ---------------------------------------------------------------------------
# [4] config — empty extension string must not crash
# ---------------------------------------------------------------------------

class TestConfigEmptyExtension(unittest.TestCase):

    def test_empty_string_extension_is_skipped(self):
        """An empty string in extensions must be silently skipped, not crash."""
        from code_assembler.config import AssemblerConfig

        # This must not raise IndexError on ext[0]
        config = AssemblerConfig(
            paths=["."],
            extensions=["", ".py", ""],
            use_default_excludes=False,
        )
        self.assertIn(".py", config.extensions)
        self.assertNotIn("", config.extensions)

    def test_only_empty_extensions_produces_no_match(self):
        """All-empty extensions: no crash, but assembler will find no files."""
        from code_assembler.config import AssemblerConfig

        # The initial check `if not self.extensions` runs BEFORE normalization,
        # so [""] passes. After normalization extensions=[] which is valid config
        # (just matches nothing). Should not raise.
        try:
            config = AssemblerConfig(
                paths=["."],
                extensions=[""],
                use_default_excludes=False,
            )
            self.assertEqual(config.extensions, [])
        except Exception as exc:
            self.fail(f"AssemblerConfig raised unexpectedly on empty extension: {exc}")

    def test_invalid_compress_level_raises(self):
        """An invalid compress_level must raise ValueError with a clear message."""
        from code_assembler.config import AssemblerConfig

        with self.assertRaises(ValueError) as ctx:
            AssemblerConfig(
                paths=["."],
                extensions=[".py"],
                use_default_excludes=False,
                compress_level="full",  # invalid
            )
        self.assertIn("compress_level", str(ctx.exception))


# ---------------------------------------------------------------------------
# [5] analyzers — commonpath must not crash on multi-drive Windows paths
# ---------------------------------------------------------------------------

class TestAnalyzersCommonPath(unittest.TestCase):

    def test_commonpath_value_error_fallback(self):
        """
        When os.path.commonpath raises ValueError (Windows multi-drive),
        _get_components must return an empty list gracefully.
        """
        from code_assembler.analyzers import ArchitectureAnalyzer
        from code_assembler.config import FileEntry, CodebaseStats

        entries = [
            FileEntry(path="C:\\src\\main.py", type="file", depth=1),
            FileEntry(path="D:\\lib\\utils.py", type="file", depth=1),
        ]
        stats = CodebaseStats(total_files=2)

        analyzer = ArchitectureAnalyzer(entries, stats)

        with patch("os.path.commonpath", side_effect=ValueError("Paths don't have same drive")):
            # Must not raise
            result = analyzer._get_components()

        # Result should be a list (possibly empty) — not an exception
        self.assertIsInstance(result, list)

    def test_analyze_data_survives_commonpath_error(self):
        """Full analyze_data() call must survive a commonpath failure."""
        from code_assembler.analyzers import ArchitectureAnalyzer
        from code_assembler.config import FileEntry, CodebaseStats

        entries = [FileEntry(path="/a/file.py", type="file", depth=1)]
        stats = CodebaseStats(total_files=1, files_by_ext={".py": 1})

        analyzer = ArchitectureAnalyzer(entries, stats)

        with patch("os.path.commonpath", side_effect=ValueError("bad paths")):
            result = analyzer.analyze_data()

        self.assertIn("components", result)
        self.assertIn("distribution", result)


# ---------------------------------------------------------------------------
# [6] delta — errors in extract_metadata must surface, not be swallowed
# ---------------------------------------------------------------------------

class TestDeltaErrorSurfacing(unittest.TestCase):

    def test_permission_error_is_reported(self):
        """PermissionError on the snapshot file must print a warning, not silently pass."""
        from code_assembler.delta import extract_metadata

        with patch("builtins.open", side_effect=PermissionError("access denied")):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("fake.md")

        self.assertEqual(result, {})
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        # Message contains "Cannot read snapshot (permission denied)"
        self.assertIn("cannot read snapshot", printed.lower())

    def test_corrupted_json_is_reported(self):
        """Invalid JSON in the metadata block must print a warning, not silently pass."""
        from code_assembler.delta import extract_metadata

        bad_md = "<!-- CODE_ASSEMBLER_METADATA\n{not valid json}\n-->"
        with patch("builtins.open", unittest.mock.mock_open(read_data=bad_md)):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("fake.md")

        self.assertEqual(result, {})
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        # Message contains "corrupted (invalid JSON)"
        self.assertIn("corrupted", printed.lower())

    def test_missing_metadata_block_returns_empty_silently(self):
        """A snapshot without a metadata block returns {} without printing anything."""
        from code_assembler.delta import extract_metadata

        plain_md = "# Consolidated Codebase\n\nSome content, no metadata block."
        with patch("builtins.open", unittest.mock.mock_open(read_data=plain_md)):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("fake.md")

        self.assertEqual(result, {})
        mock_print.assert_not_called()

    def test_file_not_found_returns_empty_silently(self):
        """Missing snapshot file returns {} silently (expected caller behaviour)."""
        from code_assembler.delta import extract_metadata

        with patch("builtins.open", side_effect=FileNotFoundError()):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("does_not_exist.md")

        self.assertEqual(result, {})
        mock_print.assert_not_called()


# ---------------------------------------------------------------------------
# [7] utils — Linux clipboard xsel fallback on ANY xclip failure
# ---------------------------------------------------------------------------

class TestClipboardLinuxFallback(unittest.TestCase):

    def _linux_clip(self, text, xclip_exc):
        """Helper: run copy_to_clipboard under Linux with a given xclip exception."""
        from code_assembler.utils import copy_to_clipboard
        from code_assembler.utils import _CLIPBOARD_TIMEOUT

        with patch("platform.system", return_value="Linux"):
            with patch("subprocess.run") as mock_run:
                # First call (xclip) raises the given exception
                # Second call (xsel) succeeds
                mock_run.side_effect = [xclip_exc, MagicMock()]
                result = copy_to_clipboard(text)

        return result, mock_run

    def test_xsel_fallback_on_file_not_found(self):
        """xclip missing (FileNotFoundError) → try xsel."""
        result, mock_run = self._linux_clip("hello", FileNotFoundError())
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)
        xsel_call = mock_run.call_args_list[1]
        self.assertIn("xsel", str(xsel_call))

    def test_xsel_fallback_on_called_process_error(self):
        """
        xclip installed but failing (e.g. no DISPLAY) → CalledProcessError.
        Previously this was caught by the outer except and returned False
        without ever trying xsel. Now xsel must be attempted.
        """
        exc = subprocess.CalledProcessError(1, "xclip")
        result, mock_run = self._linux_clip("hello", exc)
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)
        xsel_call = mock_run.call_args_list[1]
        self.assertIn("xsel", str(xsel_call))

    def test_xsel_fallback_on_timeout(self):
        """xclip timing out → TimeoutExpired → try xsel."""
        exc = subprocess.TimeoutExpired(cmd="xclip", timeout=10)
        result, mock_run = self._linux_clip("hello", exc)
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)


# ---------------------------------------------------------------------------
# [8] utils — subprocess calls must include a timeout
# ---------------------------------------------------------------------------

class TestClipboardTimeout(unittest.TestCase):

    def _capture_run_kwargs(self, system: str, text: str = "test"):
        """Run copy_to_clipboard and capture all kwargs passed to subprocess.run."""
        from code_assembler.utils import copy_to_clipboard

        calls_kwargs = []

        def fake_run(*args, **kwargs):
            calls_kwargs.append(kwargs)
            return MagicMock()

        with patch("platform.system", return_value=system):
            with patch("subprocess.run", side_effect=fake_run):
                copy_to_clipboard(text)

        return calls_kwargs

    def test_windows_clipboard_has_timeout(self):
        kwargs_list = self._capture_run_kwargs("Windows")
        self.assertTrue(len(kwargs_list) > 0)
        self.assertIn("timeout", kwargs_list[0], "subprocess.run on Windows has no timeout")

    def test_macos_clipboard_has_timeout(self):
        kwargs_list = self._capture_run_kwargs("Darwin")
        self.assertTrue(len(kwargs_list) > 0)
        self.assertIn("timeout", kwargs_list[0], "subprocess.run on macOS has no timeout")

    def test_linux_xclip_has_timeout(self):
        kwargs_list = self._capture_run_kwargs("Linux")
        self.assertTrue(len(kwargs_list) > 0)
        self.assertIn("timeout", kwargs_list[0], "subprocess.run for xclip has no timeout")


# ---------------------------------------------------------------------------
# [9] core — write failure must raise OSError (not silently succeed)
# ---------------------------------------------------------------------------

class TestCoreWriteFailure(unittest.TestCase):

    def test_write_failure_raises_oserror(self):
        """
        If write_file_content returns False, assemble_codebase must raise OSError.
        Previously the return value was ignored and a false "Saved" message shown.
        """
        from code_assembler.core import assemble_codebase

        test_dir = tempfile.mkdtemp()
        try:
            src = Path(test_dir) / "src"
            src.mkdir()
            (src / "hello.py").write_text("print('hi')", encoding="utf-8")

            # FIX: write_file_content is imported lazily inside assemble_codebase(),
            # so patch it in the file_io module, not in core's namespace.
            with patch("code_assembler.file_io.write_file_content", return_value=False):
                with self.assertRaises(OSError):
                    assemble_codebase(
                        paths=[str(src)],
                        extensions=[".py"],
                        output=str(Path(test_dir) / "out.md"),
                        show_progress=False,
                    )
        finally:
            shutil.rmtree(test_dir)

    def test_write_success_does_not_raise(self):
        """Normal write path must not raise any exception."""
        from code_assembler.core import assemble_codebase

        test_dir = tempfile.mkdtemp()
        try:
            src = Path(test_dir) / "src"
            src.mkdir()
            (src / "hello.py").write_text("print('hi')", encoding="utf-8")

            # Patch write to succeed (returns True) — we just verify no exception
            with patch("code_assembler.file_io.write_file_content", return_value=True):
                try:
                    assemble_codebase(
                        paths=[str(src)],
                        extensions=[".py"],
                        output=str(Path(test_dir) / "out.md"),
                        show_progress=False,
                    )
                except OSError:
                    self.fail("assemble_codebase raised OSError on a successful write")
        finally:
            shutil.rmtree(test_dir)


# ---------------------------------------------------------------------------
# [10] interactive — use_default_excludes must be False after wizard run
# ---------------------------------------------------------------------------

class TestInteractiveUseDefaultExcludes(unittest.TestCase):

    def test_wizard_sets_use_default_excludes_false(self):
        """
        The wizard manages exclusions itself. It must pass use_default_excludes=False
        to assemble_codebase so AssemblerConfig doesn't add defaults a second time.
        """
        from code_assembler.interactive import InteractiveWizard

        wizard = InteractiveWizard()

        inputs = [
            "1",    # Current directory
            "1",    # Python preset
            "y",    # Use default exclusions
            "n",    # No custom patterns
            "",     # Default output name
            "n",    # No advanced config
            "y",    # Confirm assembly
            "n",    # Don't save config
        ]

        captured_kwargs = {}

        def fake_assemble(**kwargs):
            captured_kwargs.update(kwargs)
            return "# mock content"

        with patch("builtins.input", side_effect=inputs):
            with patch("code_assembler.interactive.os.path.exists", return_value=False):
                with patch("code_assembler.interactive.assemble_codebase", side_effect=fake_assemble):
                    with patch("sys.stdout", new=StringIO()):
                        wizard.run()

        self.assertIn("use_default_excludes", captured_kwargs,
                      "use_default_excludes was not passed to assemble_codebase")
        self.assertFalse(
            captured_kwargs["use_default_excludes"],
            "use_default_excludes must be False when wizard manages exclusions itself"
        )

    def test_wizard_exclusions_not_doubled(self):
        """
        Default patterns must not appear twice when use_default_excludes=False
        and the wizard already merged them into exclude_patterns.
        """
        from code_assembler.interactive import InteractiveWizard
        from code_assembler.constants import DEFAULT_EXCLUDE_PATTERNS

        wizard = InteractiveWizard()
        inputs = ["1", "1", "y", "n", "", "n", "y", "n"]
        captured_kwargs = {}

        def fake_assemble(**kwargs):
            captured_kwargs.update(kwargs)
            return "# mock"

        with patch("builtins.input", side_effect=inputs):
            with patch("code_assembler.interactive.os.path.exists", return_value=False):
                with patch("code_assembler.interactive.assemble_codebase", side_effect=fake_assemble):
                    with patch("sys.stdout", new=StringIO()):
                        wizard.run()

        patterns = captured_kwargs.get("exclude_patterns", [])
        # No pattern should appear more than once
        for p in DEFAULT_EXCLUDE_PATTERNS:
            count = patterns.count(p)
            self.assertLessEqual(
                count, 1,
                f"Pattern '{p}' appears {count} times — use_default_excludes double-application bug"
            )


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

## `ROADMAP.md`

```markdown
# 🗺️ Roadmap — Code Assembler Pro

Planned features and vision for future versions, ranked by their impact on the daily LLM-assisted development workflow.

---

## 🔴 High Priority — v4.6.0

### 1. Compression — Edge Cases & Stability

The v4.5 compressor handles standard code well. Real-world projects will hit these:

*   **Python edge cases**: decorators (`@property`, `@staticmethod`, `@dataclass`), `TypedDict`, `Protocol`, `match`/`case` (Python 3.10+), lambda assignments, and `__all__` lists need explicit handling and tests.
*   **Decorated functions**: The decorator lines are preserved but the associated `def` detection may misfire in complex stacking scenarios.
*   **`pass`-only bodies**: Should be normalised to `...` for consistency. Currently `pass` may be kept as-is.
*   **tree-sitter package gaps**: `tree-sitter-kotlin`, `tree-sitter-swift`, `tree-sitter-scala` are not reliably published for the 0.21 API. Offer `tree-sitter-languages` (monolithic 0.20) as a `compress-compat` extra with an adapter shim.
*   **Compression ratio in summary**: After `--compress`, show `Original: X tokens → Compressed: Y tokens (Z% reduction)`.

### 2. 🔒 Secret Scanning (`--scan-secrets`)

Scan files before assembly to detect exposed secrets (AWS keys, API tokens, `.env` content).
*   **Why:** The #1 risk of this tool is accidentally pasting a secret into a Cloud LLM.
*   **Feature:** Block assembly or auto-exclude files containing potential secrets.
*   **Implementation:** Regex patterns for common secret formats + configurable allow-list.

### 3. Configuration Hierarchy

The current approach (JSON config + CLI overrides merged manually) is fragile at scale.
*   **Goal:** Formal precedence chain — `JSON config < environment variables < CLI flags`.
*   **Benefit:** Predictable, documented behaviour; eliminates the class of silent-override bugs found in v4.5.1.
*   **Validate unknown JSON keys**: `"extentions"` instead of `"extensions"` currently surfaces as a cryptic `TypeError`. A `validate_config_keys()` guard would give an actionable message.

---

## 🟡 Medium Priority — v5.0.0

### 4. Project Profiles (`--profile`)

Store named configurations to switch between projects with a single word.
*   **Usage:** `code-assembler --profile mlops`
*   **Why:** Faster than managing multiple JSON config files.
*   **Storage:** `~/.code-assembler/profiles/<name>.json`

### 5. Dependency Summary

Automatically extract dependencies from manifest files (`pyproject.toml`, `package.json`, `go.mod`, etc.).
*   **Why:** Gives the LLM immediate technical stack context without reading every file. Essential for migration or debugging advice.

### 6. Token Budgeting (`--max-tokens`)

Intelligent file selection to stay within a specific token limit.
*   **Strategies:** `recent` (modified first), `entry` (main files first), or `small` (maximise file count).
*   **Why:** Large projects exceed context windows. Smart selection rather than blind truncation.

### 7. Import Graph & Mermaid Support

Static analysis of imports to generate a dependency map.
*   **Why:** Helps the LLM understand the architecture and detect circular dependencies without reading the full source.

---

## 🟠 Long Term — v5.x & Beyond

### 8. 🤖 Claude Skill / MCP Tool

Transform Code Assembler into a tool that Claude can trigger directly.
*   **Concept:** Claude runs the tool, reads the codebase, and applies fixes via `--rebuild` automatically.
*   **Status:** Feasible today via Claude's computer use — worth prototyping.

### 9. Web Interface (Viewer, Assembler & Chat)

A tripartite GUI to assemble projects, navigate the generated Markdown, and chat with an LLM directly on the code.
*   **Viewer:** Interactive file tree on the left, syntax-highlighted code in the center.
*   **Integrated Chat:** A chat panel where the LLM has the full `.md` as context. "Apply fix" button modifies the code in the viewer.

### 10. Watch Mode (`--watch`)

Automatic regeneration whenever a source file changes.
*   **Why:** Perfect for "Live Coding" sessions with an AI. Combine with `--since` for true incremental live mode.

---

## 📋 Roadmap Summary

| Version | Feature | Impact | Status |
|---------|---------|--------|--------|
| **v4.4.0** | Rebuild Mode (`--rebuild`) | 🔴 Critical | ✅ Done |
| **v4.4.0** | Delta Mode (`--since`) | 🔴 Critical | ✅ Done |
| **v4.4.0** | Clipboard Support (`--clip`) | 🔴 High | ✅ Done |
| **v4.5.2** | Code Compression (`--compress`) | 🔴 High | ✅ Done |
| **v4.5.2** | Per-language tree-sitter extras | 🟡 Medium | ✅ Done |
| **v4.5.1** | Bug fix & robustness (8 bugs, 28 tests) | 🔴 Critical | ✅ Done |
| **v4.6.0** | Compression edge cases & stability | 🔴 High | 📋 Planned |
| **v4.6.0** | 🔒 Secret Scanning (`--scan-secrets`) | 🔴 Critical | 📋 Planned |
| **v4.6.0** | Configuration hierarchy & validation | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Project Profiles (`--profile`) | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Dependency Summary | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Token Budgeting (`--max-tokens`) | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Import Graph (Mermaid) | 🟡 Medium | 📋 Planned |
| **v5.x** | Claude Skill (MCP) | 🟠 High | 💡 Concept |
| **v5.x** | Web UI (Viewer & Chat) | 🟠 High | 💡 Concept |
| **v5.x** | Watch Mode (`--watch`) | 🟠 Medium | 💡 Concept |

---

## 🎯 Vision: The "Semantic Zip" for AI

Code Assembler Pro aims to be more than a concatenator; it is a **Semantic Zip** format.

| Feature | Standard `.zip` | Code Assembler `.md` |
|---|---|---|
| **Human Readable** | ❌ Binary | ✅ Native Markdown |
| **AI Optimized** | ❌ Opaque | ✅ Structured Context |
| **Metadata** | Names/Sizes | Architecture, Stats, Manifest |
| **Compression** | Binary deflate | ✅ Semantic skeleton (`--compress`) |
| **Secret Safety** | ❌ None | ✅ Scanning (planned v4.6) |
| **Workflow** | One-way | ✅ Bidirectional (`--rebuild`) |

### The Full Cycle
```
Code ↔ [code-assembler] ↔ Markdown ↔ [LLM]
```
The Markdown file becomes the **universal exchange format** between developers and AI — compressed for token efficiency, secured by secret scanning, and verified by integrity manifests.

---
*Last updated: May 2026 — v4.5.1*
```

## `README.md`

```markdown
# 🏛️ Code Assembler Pro

> **Turn your codebase into structured, LLM-ready context—and rebuild it from AI suggestions.**

![Version](https://img.shields.io/badge/version-4.5.2-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Code Assembler Pro** is a high-grade engineering utility designed to bridge the gap between your source code and Large Language Models (Claude, GPT-4o, Gemini, DeepSeek).

It doesn't just concatenate files; it generates a **contextual technical document** optimized for LLM ingestion, and provides a **reliable rebuild engine** to reconstruct projects from AI-modified Markdown files.

---

## 🎯 Why Code Assembler Pro?

Copy-pasting raw files into a chat window leads to context loss. **Code Assembler Pro solves this by:**

1.  **🗺️ Project Mapping:** Automatically generates a clickable Table of Contents and architectural overview.
2.  **♻️ Bidirectional Workflow:** Use `--rebuild` to turn an AI's Markdown response back into a physical directory structure.
3.  **⏱️ Token Efficiency:** Use `--since` (Delta Mode) to send only modified files, saving thousands of tokens.
4.  **✂️ Smart Compression:** Use `--compress` to reduce a dependency's code to signatures + docstrings only — dramatically shrinking token count while preserving full structural context.
5.  **🛡️ Metadata Manifest:** Injects a hidden JSON manifest for 100% reliable project reconstruction and change tracking.

---

## ✨ Key Features

- **♻️ Rebuild Mode (`--rebuild`):** Reconstruct an entire project from a Markdown snapshot. Perfect for applying AI-generated refactors instantly.
- **⏱️ Delta Mode (`--since`):** Generate updates containing only files modified, added, or deleted since a previous assembly.
- **🗜️ Compression Mode (`--compress`):** Reduce source files to structural skeletons — signatures and docstrings only. Python always works out of the box; other languages use individually installed tree-sitter packages.
- **📋 Clipboard Integration (`--clip`):** Direct copy to system clipboard for instant ingestion into LLMs.
- **🧠 Architecture Analysis:** Detects design patterns (MVC, API, Testing) and provides file distribution stats.
- **📊 Token Metrics:** Real-time estimation of token count to stay within model context windows.
- **📝 Enhanced Syntax Highlighting:** Support for 50+ extensions including **Jinja2**, **Terraform**, and smart detection for `Dockerfile`, `Makefile`, and `.env`.
- **🖥️ Cross-Platform:** Native support for Windows, macOS, and Linux with automatic emoji/ASCII adaptation.

---

## 🚀 Installation

### Standard install (no compression)
```bash
pip install code-assembler-pro
```

### With compression support

Python files are **always supported** via stdlib `ast` — no extra install needed.

For other languages, install the corresponding extra:

```bash
# JavaScript + TypeScript
pip install "code-assembler-pro[compress-web]"

# Rust + Go + C + C++
pip install "code-assembler-pro[compress-systems]"

# A single language
pip install "code-assembler-pro[compress-js]"
pip install "code-assembler-pro[compress-rust]"

# Everything
pip install "code-assembler-pro[compress-all]"
```

### From source (development)
```bash
git clone https://github.com/xmehaut/code-assembler-pro.git
cd code-assembler-pro
pip install -e .
```

---

## 💻 Quick Start (CLI)

### 1. Assemble & Copy (The "One-Shot" Workflow)
Consolidate your code and copy it directly to your clipboard:
```bash
code-assembler . --ext py md --clip
```

### 2. Iterative Update (The "Token-Saver" Workflow)
Only send what changed since your last assembly:
```bash
code-assembler . --ext py --since codebase.md --clip
```

### 3. Rebuild from AI (The "Round-Trip" Workflow)
Restore a project from a Markdown file (e.g., after an AI refactor):
```bash
code-assembler --rebuild refactored_codebase.md --output-dir ./restored_project
```

### 4. Compress a Dependency (The "Skeleton" Workflow)
Generate a lightweight snapshot of a third-party package — full structure, minimal tokens:
```bash
# Your own code — full detail
code-assembler src/ --ext py --output my_package.md

# A dependency — signatures + docstrings only
code-assembler .venv/lib/some_dep/ --ext py --compress --output dep_skeleton.md
```

---

## 📖 CLI Options Reference

| Option | Description |
|--------|-------------|
| `paths` | Files or directories to analyze |
| `--ext` / `-e` | Extensions and filenames to include (e.g., `py md Dockerfile`) |
| `--output` / `-o` | Output file name (default: `codebase.md`) |
| `--since` / `-s` | Delta Mode: Only include changes since this snapshot |
| `--rebuild` | Reconstruct project from a Markdown file |
| `--output-dir` | Target directory for reconstruction |
| `--clip` / `-k` | Copy result directly to clipboard |
| `--dry-run` | Preview rebuild without writing files |
| `--compress` / `-z` | **(v4.5)** Compress to signatures + docstrings only |
| `--compress-level` | **(v4.5)** `signatures` (default) or `docstrings_only` |
| `--interactive` / `-i` | Launch the interactive wizard |
| `--config` / `-c` | Load a JSON configuration file |
| `--exclude` / `-x` | Patterns to exclude (added to defaults) |
| `--max-size` | Maximum file size in MB (default: 10.0) |
| `--version` | Show version and exit |

---

## 🗜️ Compression Mode — How It Works

`--compress` reduces each file to its structural skeleton. The goal is to give an LLM
full context about a codebase's shape and API surface without the implementation noise.

```python
# Original (full file) — ~80 tokens
def connect(host: str, port: int, timeout: float = 30.0) -> Connection:
    """Establish a TCP connection to the server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))
    return Connection(sock)

# Compressed — ~15 tokens
def connect(host: str, port: int, timeout: float = 30.0) -> Connection:
    """Establish a TCP connection to the server."""
    ...
```

**Language support:**

| Language | Requirement |
|----------|-------------|
| Python | ✅ Always available (stdlib `ast`) |
| JavaScript / JSX | `pip install "code-assembler-pro[compress-js]"` |
| TypeScript / TSX | `pip install "code-assembler-pro[compress-ts]"` |
| Rust | `pip install "code-assembler-pro[compress-rust]"` |
| Go | `pip install "code-assembler-pro[compress-go]"` |
| Java | `pip install "code-assembler-pro[compress-java]"` |
| C | `pip install "code-assembler-pro[compress-c]"` |
| C++ | `pip install "code-assembler-pro[compress-cpp]"` |

Missing parsers are reported at startup with the exact install command — other files are passed through unchanged.

---

## 🔌 Programmatic API

Code Assembler Pro can be integrated into your Python pipelines (CI/CD, custom AI agents).

### Basic Assembly
```python
from code_assembler import assemble_codebase

markdown = assemble_codebase(
    paths=["./src"],
    extensions=[".py", ".js"],
    output="context.md"
)
```

### Compressed snapshot of a dependency
```python
markdown = assemble_codebase(
    paths=[".venv/lib/requests"],
    extensions=[".py"],
    output="requests_skeleton.md",
    compress=True,
)
```

### Incremental Update (Delta Mode)
```python
assemble_codebase(
    paths=["./src"],
    extensions=[".py"],
    since="previous_snapshot.md",
    output="delta_update.md"
)
```

### Project Reconstruction
```python
from code_assembler.rebuilder import CodebaseRebuilder

rebuilder = CodebaseRebuilder("ai_response.md", "./new_src")
rebuilder.rebuild()
```

---

## ⚙️ Advanced Configuration (JSON)

For complex projects, use a JSON configuration file:

```json
{
  "paths": ["./src", "./infra"],
  "extensions": [".py", ".ts", ".j2", "Dockerfile", ".env"],
  "exclude_patterns": ["migrations", "__pycache__", "*.test.ts"],
  "output": "project_context.md",
  "recursive": true,
  "include_readmes": true,
  "max_file_size_mb": 2.0,
  "truncate_large_files": true,
  "truncation_limit_lines": 500,
  "compress": false,
  "compress_level": "signatures"
}
```
Run it using: `code-assembler --config assembler_config.json`

---

## 💡 Recommended Use Cases

### 1. Massive Refactoring Loop
1. Assemble your project: `code-assembler . -e py --clip`
2. Paste into Claude: *"Refactor this project to use Pydantic v2."*
3. Save Claude's response as `refactor.md`.
4. Apply changes: `code-assembler --rebuild refactor.md --output-dir .`

### 2. Dependency Context (new in v4.5)
Give the AI full structural context of a library without burning your token budget:
```bash
code-assembler .venv/lib/pydantic/ -e py --compress --output pydantic_api.md
```

### 3. Incremental Debugging
After fixing a bug, send only the delta to the AI to verify the fix without re-sending the whole codebase:
```bash
code-assembler . -e py --since previous_snapshot.md --clip
```

### 4. Infrastructure Audit
Include `Dockerfile`, `Makefile`, and `.tf` files to give the AI a full view of your deployment stack.

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch.
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Code Assembler Pro** — *Give your AI the context it deserves, then take the code back.* 🚀
```

## `QUICKSTART_INTERACTIVE.md`

```markdown
# 🚀 Interactive Mode — 5-Minute Quickstart (v4.4.0)

Get started with Code Assembler Pro's interactive wizard and the new **Round-Trip workflow** in under 5 minutes!

---

## Step 1: Launch the Wizard

```bash
code-assembler -i
```

---

## Step 2: Follow the Prompts

### 📂 Choose What to Analyze
**Choice [1]**: Current directory (`.`) is usually the best start.

### 📝 Pick Your File Types
**Choice [2]**: Python + Config + Docs (includes `.py`, `.md`, `.toml`, `.yaml`, and now `.j2`).
**Choice [8]**: Custom — to include specific files like `Dockerfile`, `Makefile`, or `.tf`.

### 🚫 Exclusions
**Use defaults? [Y]**: Always say **Yes** to filter out noise like `node_modules` or `.venv`.

### 💾 Name Your Output
**Default**: `codebase.md`. In v4.4, this file now automatically includes a **Hidden Metadata Manifest** for reliable project restoration.

---

## Step 3: Confirm & Run

```
[>>] Start assembly? [Y/n]: y
```

---

## 🎯 The v4.4 "Round-Trip" Workflow

Once your `codebase.md` is generated, here is how to use the new pro features:

### 1. Copy to AI (Instant)
Instead of manual copy-pasting, use the built-in clipboard flag:
```bash
code-assembler . --ext py --clip
```
*Then simply paste (`Ctrl+V`) into Claude or ChatGPT.*

### 2. Update with Delta (Token Saver)
When you modify your code, don't resend the whole project. Send only the changes:
```bash
code-assembler . --ext py --since codebase.md --clip
```

### 3. Apply AI Changes (Rebuild)
If the AI provides a refactored version of your project in Markdown, save it as `refactor.md` and restore it instantly:
```bash
code-assembler --rebuild refactor.md --output-dir ./restored_project
```

---

## 💡 What You Get

```
codebase.md (LLM-Ready Context)
├── 📋 Header (timestamp, stats, TOC)
├── 🏛 Architecture Analysis & Patterns
├── 📊 Statistics Table
├── 📄 Full Source Code (with enhanced syntax highlighting)
└── 🔒 Hidden Metadata Manifest (for Rebuild & Delta)
```

---

## 🔥 Pro Tips

1. **Clipboard Shortcut**: Use `-k` as a shortcut for `--clip`.
2. **Jinja2 Support**: Templates (`.j2`, `.jinja`) are now natively recognized for better AI understanding.
3. **Check Token Count**: Look at the **Estimated Tokens** in the stats to ensure you stay within your LLM's context window (e.g., 200k for Claude 3.5).
4. **Smart Truncation**: If your project is huge, enable truncation in "Advanced Options" to keep only the first 500 lines of large files.

---

## ❓ Common Questions

**Q: How do I get my code back from the Markdown file?**
A: Use the `--rebuild` command. It uses the hidden JSON metadata to recreate your exact folder structure.

**Q: Does the clipboard feature work on Linux?**
A: Yes, but ensure you have `xclip` or `xsel` installed. It works natively on Windows and macOS.

**Q: Can I skip the wizard next time?**
A: Yes! Save your config at the end of the wizard and use: `code-assembler --config your_config.json`

---

**Happy assembling!** 🚀
```

## `INTERACTIVE_MODE.md`

```markdown
# 🧙‍♂️ Interactive Mode Guide (v4.4.0)

**Code Assembler Pro** includes a powerful interactive wizard that guides you through the configuration process with smart defaults and helpful prompts. In version 4.4.0, the wizard is optimized to prepare your codebase for the full **Round-Trip workflow** (Assemble → AI → Rebuild).

---

## 🚀 Quick Start

### Launch Interactive Mode

```bash
# From command line
code-assembler --interactive

# Or short form
code-assembler -i
```

### Programmatic Usage

```python
from code_assembler import run_interactive_mode

run_interactive_mode()
```

---

## 📋 Wizard Steps

The interactive wizard guides you through 5 main steps:

### Step 1: 📂 Select Paths
Choose what to analyze:
- **Option 1:** Current directory (`.`) — *Most common*
- **Option 2:** Specific directories (e.g., `./src`, `./lib`)
- **Option 3:** Specific files

---

### Step 2: 📝 Select Extensions
Choose file types via presets or custom selection.

**New in v4.4:** Presets now include enhanced support for **Jinja2** (`.j2`), **Terraform** (`.tf`), and automatic syntax highlighting for extensionless files like `Dockerfile` and `Makefile`.

```
Common presets:
  1. Python projects (.py)
  2. Python + Config + Docs (.py, .md, .toml, .yaml, .j2)
  3. JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
  ...
  8. Custom selection
```

---

### Step 3: 🚫 Configure Exclusions
Manage what to exclude. The wizard uses a smart exclusion engine that prevents build artifacts and sensitive data from leaking into your AI prompts.

> **Tip:** Use `code-assembler --show-excludes` to see the full list of default exclusions.

---

### Step 4: 💾 Output Configuration
Choose your output filename (default: `codebase.md`).

**v4.4 Feature:** The wizard now automatically enables the **Hidden Metadata Manifest**. This invisible JSON block is injected at the end of your file, enabling:
1.  **Reliable Rebuilds:** Reconstruct your project from the generated file.
2.  **Accurate Deltas:** Track changes precisely between versions.

---

### Step 5: ⚙️ Advanced Options
Fine-tune the assembly:
- **Recursion:** Traverse subdirectories.
- **README Inclusion:** Automatically inject local READMEs for folder-level context.
- **Smart Truncation:** Set size limits and line counts to stay within LLM token windows.

---

## 🎯 Configuration Summary

Before executing, the wizard shows a complete summary using the new v4.4 icon set:

```
[*] Configuration Summary
----------------------------------------------------------------------

[DIR] Paths: ./src, ./docs
[FILE] Extensions: .py, .md, .j2, Dockerfile
[S] Output: codebase.md
[RECYCLE] Rebuild Metadata: Enabled (Hidden JSON)
[R] Recursive: True
[B] Include READMEs: True
[?] Max file size: 10.0 MB
[!] Truncate large files: True (500 lines)

[X] Exclusions: 15 patterns
   - __pycache__
   - .git
   - .venv
   ...

[>>] Start assembly? [Y/n]:
```

---

## 💾 Save & Reuse

After the assembly, you can save your configuration to a JSON file.

**New in v4.4:** You can also save CLI arguments directly without the wizard:
```bash
code-assembler . --ext py md --save-config my_project.json
```

---

## 🎓 The v4.4 Round-Trip Workflow

Interactive mode is the starting point for the most efficient AI coding workflow:

1.  **Assemble:** Run `code-assembler -i`, select your files, and enable the metadata block.
2.  **Consult AI:** Paste the content into your LLM (use `--clip` for speed).
3.  **Iterate:** Use the generated file with `--since` to send only your latest changes.
4.  **Rebuild:** If the AI provides a refactored version of your project, save it and use:
    `code-assembler --rebuild ai_response.md --output-dir ./restored`

---

## ⌨️ Keyboard Shortcuts

- **Enter**: Accept default value.
- **Ctrl+C**: Cancel wizard at any time.
- **Ctrl+D**: End list input (paths, patterns).

---

**Interactive Mode** — *Configuration made simple, AI context made perfect.* ✨
```

## `BUILD_AND_RELEASE.md`

```markdown
# 🚀 Build & Release Guide — Code Assembler Pro

Step-by-step guide to developing, testing, and publishing a new version of the package.

---

## Prerequisites

```bash
pip install build twine pytest
```

Required accounts:
- [PyPI](https://pypi.org/manage/account/) — Production publication
- [TestPyPI](https://test.pypi.org/manage/account/) — Test publication

Configuration file `~/.pypirc` (Windows: `C:\Users\<user>\.pypirc`):
```ini
[testpypi]
  username = __token__
  password = pypi-xxxxxxx   # TestPyPI Token

[pypi]
  username = __token__
  password = pypi-xxxxxxx   # Production PyPI Token
```

---

## Step 1 — Development Installation

```bash
pip install -e .
```

Installs the package in **editable** mode: changes made to the source code in `src/` are immediately active without reinstallation.

**To test compression with non-Python languages:**
```bash
# Install with extras during development
pip install -e ".[compress-web]"       # JS + TS
pip install -e ".[compress-systems]"   # Rust, Go, C, C++
pip install -e ".[compress-all]"       # Everything
```

**Verifications:**
```bash
code-assembler --version          # Should display 4.5.2
code-assembler --show-excludes    # Test a quick command
code-assembler src/ --ext py --compress --output test_compress.md   # Test compression
```

---

## Step 2 — Run the Test Suite

```bash
pytest tests/ -v
```

**All tests must pass before publishing.** Version 4.5.2 adds compression tests:
```
tests/test_config.py::... PASSED
tests/test_core.py::... PASSED
tests/test_file_io.py::... PASSED
tests/test_interactive.py::... PASSED
tests/test_utils.py::... PASSED
tests/test_delta_scenario.py::... PASSED
tests/test_formats.py::... PASSED
tests/test_rebuild.py::... PASSED
tests/test_clipboard.py::... PASSED
tests/test_compressor.py::... PASSED   # New in v4.5
===== 54+ passed =====
```

> **Note on compression tests:** `test_missing_package_reported` is skipped if
> `tree-sitter` is not installed in the test environment. This is expected and correct.
> The test runs automatically in environments where tree-sitter is available.

> **Rule:** Never publish if a single test fails (skips are acceptable).

---

## Step 3 — Update Version Number

In `pyproject.toml`:
```toml
[project]
version = "4.5.2"
```

Verify that `code-assembler --version` returns the correct version.

---

## Step 4 — Build the Package

```bash
python -m build
```

This generates two files in `dist/`:
```
dist/
├── code_assembler_pro-4.5.2-py3-none-any.whl
└── code_assembler_pro-4.5.2.tar.gz
```

**Verify that Jinja2 templates are included:**
```bash
# Linux/macOS
unzip -l dist/*.whl | grep j2

# Windows PowerShell
Get-ChildItem dist/*.whl | ForEach-Object { tar -tf $_.FullName } | Select-String "j2"
```

The `*.j2` files **must** appear in the list (otherwise the package will crash at runtime).

---

## Step 5 — Publish to TestPyPI

```bash
twine upload --repository testpypi dist/code_assembler_pro-4.5.2*
```

**Test the standard installation:**
```bash
mkdir test_install && cd test_install
python -m venv venv && .\venv\Scripts\activate

pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            code-assembler-pro==4.5.2

code-assembler --version
code-assembler --help
```

**Test compression extras:**
```bash
# Install with web compression support
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            "code-assembler-pro[compress-web]==4.5.2"

# Verify Python compression (no extra needed)
code-assembler src/ --ext py --compress --output skeleton.md
cat skeleton.md   # Check that bodies are replaced with '...'

# Verify JS compression (requires compress-web extra)
code-assembler src/ --ext js --compress --output skeleton_js.md
```

---

## Step 6 — Publish to PyPI (Production)

Once TestPyPI validation is successful:

```bash
twine upload dist/code_assembler_pro-4.5.2*
```

The package will be available at:
`https://pypi.org/project/code-assembler-pro/4.5.2/`

---

## Step 7 — Git Tag & Push

```bash
git add -A
git commit -m "feat: v4.5.2 - Code Compression Mode (--compress) with tree-sitter per-language support"
git tag v4.5.2
git push origin main --tags
```

---

## Quick Checklist

```
[ ] 1. pip install -e .
[ ] 2. pytest tests/ -v              → All tests pass (54+ including new v4.5 compression tests)
[ ] 3. Update version in pyproject.toml to 4.5.2
[ ] 4. python -m build               → .whl + .tar.gz in dist/
[ ] 5. Verify j2 templates inside the .whl
[ ] 6. twine upload --repository testpypi dist/*4.5.2*
[ ] 7. Test standard install + test --compress on Python files (no extra needed)
[ ] 8. Test install with [compress-web] extra + test --compress on .js files
[ ] 9. twine upload dist/*4.5.2*     → Production PyPI
[ ] 10. git commit + tag + push
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `403 Forbidden` on twine | Check the token in `.pypirc` (TestPyPI token ≠ PyPI token) |
| `code-assembler` not found | Run `pip install -e .` to register the entry point |
| Missing templates in .whl | Check `package-data` configuration in `pyproject.toml` |
| Rebuild fails on paths | Ensure you are testing with a file containing the Metadata Block |
| Clipboard fails on Linux | Install `xclip` or `xsel` (`sudo apt install xclip`) |
| `--compress` does nothing on .js | Install `pip install "code-assembler-pro[compress-js]"` |
| `ImportError: tree_sitter` | Run `pip install tree-sitter>=0.21` (core package required) |
| tree-sitter API error | Ensure `tree-sitter>=0.21` — v0.20 has incompatible API |

---

*Last updated: v4.5.2 — June 2026*
```

## `CHANGELOG.md`

```markdown
# Changelog
 
## [Unreleased]

### Added
- `AGENTS.md`: guidance file for AI coding agents (Claude, GPT, Cursor,
  Aider, etc.) working on the repository. Documents the rebuild workflow
  for consuming generated snapshots (`--rebuild`), known architectural
  pitfalls (CLI/`--config` override forwarding, tree-sitter as an optional
  dependency, language detection fallback order, path normalization
  behavior, Windows multi-drive handling), testing conventions, and current
  limitations of the compression feature.

## [4.5.2]

### Fixed

- `rebuilder.py`: `CodebaseRebuilder._extract_file_content()` could silently
  truncate or misattribute a file's content when reconstructing a project
  from a Markdown snapshot (`--rebuild`). Three distinct causes, all in the
  same method:
  - A non-greedy `(.*?)` capture stopped at the first ` ``` ` fence it found,
    which is often a fence nested *inside* a file's own content (a markdown
    file documenting code blocks, a README with examples) rather than the
    block's real terminator.
  - The original header-opening regex used an unanchored `.*?` between the
    file path and its opening fence, which could skip past unrelated
    headers and fences entirely if the target filename happened to appear
    elsewhere in the document (e.g. in a table-of-contents entry).
  - Matching by filename substring caused collisions between files sharing
    the same name at different paths (e.g. several `pyproject.toml` across
    a monorepo's members) — the wrong file's content could be returned.

  Rebuilds are now produced by a single validated scan of all real
  file-header blocks (`_find_real_file_headers`), using exact path matching
  and the last closing fence within each block's bounded window. Verified
  byte-for-byte against three independent snapshots.

### Known limitations

- A handful of edge cases (~7 files across one large monorepo snapshot)
  still over-capture when a file's content block is immediately followed
  by a directory-level "README context" section rather than another file
  header — not yet root-caused, left for a follow-up pass.

## [4.5.1] - 2026-05-02

### Fixed

- **`constants.py`**: Removed duplicate keys in `LANGUAGE_MAP` (`.properties`, `.graphql`,
  `.gql` were defined twice — last value silently overwrote the first). Removed duplicate
  `recycle` key in `_EMOJI_ICONS` and `_ASCII_ICONS` (🔄 was overwritten by ♻️).
  Removed dead code `HEADER_LEVELS` (defined but never used).
- **`cli.py`**: Implemented `_show_excludes()` which was referenced by `--show-excludes`
  but never defined, causing an `AttributeError` at runtime. Rebuild errors returned
  by `CodebaseRebuilder.rebuild()` are now displayed to the user before returning.
- **`config.py`**: Added guard against empty string extensions — `ext[0].isupper()`
  raised `IndexError` when an empty string was passed in the extensions list.
- **`analyzers.py`**: Wrapped `os.path.commonpath()` in `try/except ValueError` to
  handle Windows paths spanning multiple drives (e.g. `C:\` and `D:\`).
- **`delta.py`**: Replaced bare `except Exception: pass` in `extract_metadata()` with
  distinct handlers for `PermissionError`, `json.JSONDecodeError`, and the general case,
  each printing an explicit warning. `FileNotFoundError` remains silent (expected path).
- **`utils.py`**: Fixed Linux clipboard fallback — `xsel` was only attempted on
  `FileNotFoundError` from `xclip`; it now also triggers on `CalledProcessError` and
  `TimeoutExpired` (e.g. xclip installed but failing due to no DISPLAY). Added
  `timeout=10` to all `subprocess.run` calls to prevent infinite blocking.
- **`core.py`**: `write_file_content()` return value is now checked — a `False` return
  (disk full, invalid path) now raises `OSError` instead of silently showing a false
  success message.
- **`interactive.py`**: Fixed double-application of `DEFAULT_EXCLUDE_PATTERNS` — the
  wizard now passes `use_default_excludes=False` to `AssemblerConfig` since it already
  manages the full exclusion list itself.

### Added

- **`tests/test_robustness.py`**: 28 regression tests — one per bug fixed above —
  to prevent reintroduction. Covers constants integrity, CLI behaviour, config
  validation, analyzer resilience, delta error surfacing, clipboard fallback logic,
  subprocess timeouts, write failure detection, and wizard exclusion logic.

### Changed

- **`tests/test_clipboard.py`**: Updated subprocess assertions to include `timeout=10`
  to match the new timeout parameter added to all clipboard calls.
- **`pyproject.toml`**: Bumped version to `4.5.1`.

## [4.5.2] - 2026-05-02

### Added

- **Code Compression Mode (`--compress` / `-z`)**
  - New `--compress` flag reduces source files to their structural skeleton:
    function/class signatures and docstrings only, with bodies replaced by `...`.
  - **Python is always supported** via stdlib `ast` — zero additional dependencies.
  - Other languages (JS, TS, Rust, Go, Java, C, C++, Ruby, PHP, C#, Lua, Swift…)
    use individually installed `tree-sitter-<lang>` packages (tree-sitter ≥ 0.21 API).
  - `--compress-level` option: `signatures` (default) keeps signatures + docstrings.
  - Parsers are resolved once at startup based on the extensions configured by the user
    — only the packages actually needed are loaded.
  - Graceful degradation: if a parser is missing, the file is passed through unchanged.
    Missing packages are reported with the exact `pip install` command to fix them.
  - Truncated files (from `--max-size`) are deliberately excluded from compression
    to avoid double-mangling.

- **New module: `src/code_assembler/compressor.py`**
  - `CodeCompressor` class with `_compress_python_ast()` (stdlib) and
    `_compress_treesitter()` (generic, brace-style and indentation-based languages).
  - `TREESITTER_MODULE_MAP`: extension → PyPI package name mapping.
  - `LANGUAGE_NODE_CONFIG`: per-language tree-sitter node type configuration.

- **Optional dependencies in `pyproject.toml`**
  - Per-language extras: `compress-js`, `compress-ts`, `compress-rust`, `compress-go`,
    `compress-java`, `compress-c`, `compress-cpp`, `compress-rb`, `compress-php`, `compress-cs`.
  - Convenience bundles: `compress-web` (JS + TS), `compress-systems` (Rust, Go, C, C++),
    `compress-all` (all supported languages).

- **New test file: `tests/test_compressor.py`** — 19 tests covering:
  - Python AST: function body suppression, docstring preservation, `async def`,
    class method handling, imports/constants preserved, indentation correctness,
    SyntaxError fallback, empty source.
  - Dispatcher: extension routing, unknown extension pass-through, missing parser
    pass-through, tree-sitter exception recovery.
  - Parser loading: missing package reporting, Python never triggers tree-sitter.

### Changed

- **`config.py`**: Added `compress: bool = False` and `compress_level: str = "signatures"`
  fields to `AssemblerConfig`, with validation in `__post_init__` and export in `to_dict()`.
- **`core.py`**: `CodeCompressor` is instantiated once in `CodebaseAssembler.__init__`
  when `config.compress=True`; compression is injected in `process_file()` after reading,
  before formatting. Progress output shows `[compressed]` tag when active.
- **`cli.py`**: Added `--compress / -z` and `--compress-level` flags (new "Compression Mode"
  argument group). Both flags are persisted via `--save-config`.
- **`pyproject.toml`**: Bumped version to `4.5.2`. Added `[project.optional-dependencies]`
  section with individual and bundle extras for compression support.
- **`tests/test_clipboard.py`**: Updated Windows, macOS, and Linux xclip assertions
  to include `timeout=10` following the subprocess timeout fix in `utils.py`.

---

## [4.4.2] - 2026-02-17

### Added
- **Programmatic Rebuild Example**: Added `examples/rebuild_usage.py` to demonstrate project reconstruction via API.
- **Library Documentation**: Added a dedicated "Python Library Usage" section to the README.

### Fixed
- **Rebuilder Regex Robustness**: Improved the content extraction logic in `rebuilder.py` to be agnostic of path separators (`/` vs `\`) and flexible with whitespace/newlines in Markdown snapshots.
- **Path Traversal Security**: Refined the security check to better handle relative paths while maintaining protection against directory traversal attacks.
- **Example Execution Context**: Fixed path resolution in `examples/` scripts by standardizing the working directory to the project root, ensuring clean metadata generation.

### Changed
- **Modernized Examples**: Updated `basic_usage.py` and `advanced_config.py` to showcase Delta Mode and string-based returns.
- **Documentation Polish**: General improvement of CLI and Library documentation for a better developer experience.

---

## [4.4.1] - 2026-02-17

### Fixed
- **Windows Clipboard Unicode Support**: Switched from legacy `clip.exe` to PowerShell `Set-Clipboard` to correctly handle emojis and special characters without encoding errors.
- **Clipboard Test Suite**: Updated tests to validate the new PowerShell-based copy logic and UTF-8 encoding.

---

## [4.4.0] - 2026-02-17

### Added

- **Rebuild Mode (`--rebuild`)**
  - Ability to reconstruct a project's entire directory structure and file contents from a Markdown snapshot.
  - Includes `--output-dir` to specify the restoration target and `--dry-run` for safe previews.
  - Security features: Blocks path traversal attacks and warns about truncated files.
- **Clipboard Support (`--clip` / `-k`)**
  - Direct copy of the generated Markdown to the system clipboard for immediate ingestion into LLMs.
  - Cross-platform support (Windows, macOS, Linux) without external dependencies.
- **Reliable Delta Mode (`--since`)**
  - Incremental updates: generate Markdown containing only files modified, added, or deleted since a previous snapshot.
  - Uses a new hidden Metadata Manifest for 100% accuracy.
- **Hidden Metadata Injection**
  - Injects a hidden JSON block (`<!-- CODE_ASSEMBLER_METADATA -->`) at the end of generated files.
  - Stores exact relative paths and modification timestamps (mtime) for reliable delta and rebuild operations.
- **Enhanced Syntax Highlighting**
  - Added support for **Jinja2 templates** (`.j2`, `.jinja`, `.jinja2`).
  - Added support for modern formats: **HCL/Terraform** (`.tf`), **Astro**, **Prisma**, and **GraphQL**.
  - Smart detection for extensionless files: `Dockerfile`, `Makefile`, `Procfile`, and `.env` files now get proper syntax highlighting.
- **Comprehensive Test Suite**
  - `tests/test_rebuild.py`: Validates project reconstruction and security boundaries.
  - `tests/test_clipboard.py`: Validates cross-platform clipboard commands and CLI integration.
  - `tests/test_delta_scenario.py`: Validates complex delta scenarios and duplicate filenames.
  - `tests/test_formats.py`: Validates language detection logic.

### Fixed

- **Cross-Platform Path Normalization**
  - Fixed a critical bug where Windows backslashes (`\`) and case sensitivity caused delta mismatches.
  - All internal keys are now normalized to lowercase with POSIX forward slashes (`/`).
- **Regex Parsing Fragility**
  - Replaced experimental visual TOC parsing with structured JSON metadata to avoid errors caused by indentation or date formatting changes.

### Changed

- **`cli.py` Refactor**: Completely rewritten to support multiple execution modes (Assembly, Rebuild, Interactive).
- **`rebuilder.py`**: New module dedicated to project reconstruction.
- **`delta.py` Refactor**: Rewritten to prioritize metadata-based analysis.
- **`formatters.py` Refactor**:
  - Isolated language detection into a dedicated `_detect_language` method.
  - Updated to handle JSON metadata generation and injection.
- **Module Documentation**: Added comprehensive technical docstrings to `delta.py`, `rebuilder.py`, and `cli.py`.

---

## [4.3.2] - 2026-02-16

### Fixed

- **Interactive mode: comma-separated extensions corrupted JSON config**
  - When a user typed extensions with commas (e.g. `.py, .yaml, .tsx,`), the wizard
    preserved the commas inside the strings (e.g. `".py,"`) causing zero files to match.
  - `_select_extensions()` in `interactive.py` now strips commas before parsing.
  - Regression test added: `test_select_extensions_custom_with_commas` in `test_interactive.py`.
```

## `AGENTS.md`

```markdown
# AGENTS.md — code-assembler-pro

This file serves two different audiences. If you're an agent discovering
this repository as a potential tool to use, read **Part 1** only. If you're
an agent contributing to or modifying this codebase, read **Part 2** as well.

---

# Part 1 — Using this tool

## What it does

`code-assembler-pro` consolidates a codebase into a single structured
Markdown file, optimized for LLM ingestion — pasting an entire project into
a chat, feeding it to a context window, or archiving a reviewable snapshot.
It is an alternative to tools like Repomix.

```bash
pip install code-assembler-pro
code-assembler src/ --ext .py --output codebase.md
```

## What makes it different

**Modular tree-sitter parsers, not a monolithic dependency.** Optional code
compression (`--compress`) reduces files to signatures and docstrings only.
Python is supported out of the box via stdlib `ast` (no extra install).
Other languages use individual tree-sitter packages, installed via named
extras instead of one heavy all-languages bundle:

```bash
pip install "code-assembler-pro[compress-web]"      # JS + TS
pip install "code-assembler-pro[compress-systems]"  # Rust + Go + C + C++
pip install "code-assembler-pro[compress-js]"        # a single language
pip install "code-assembler-pro[compress-all]"       # everything
```

**Reversible: it can rebuild a project from its own output.** Unlike most
"dump codebase to text" tools, the generated Markdown embeds a hidden
metadata block that makes the snapshot reconstructable:

```bash
code-assembler --rebuild snapshot.md --output-dir ./restored
```

If you (an agent) receive a `.md` file generated by code-assembler-pro —
recognizable by the `# Consolidated Codebase` header and a
`<!-- CODE_ASSEMBLER_METADATA ... -->` block at the end — use `--rebuild`
instead of parsing the markdown yourself. The rebuilder already handles
tricky cases via regression tests (nested code fences inside `.md` files,
files sharing the same name at different paths, prose headers that merely
resemble filenames). Manual regex parsing risks reconstructing the project
incorrectly.

Other useful flags: `--since snapshot.md` for incremental/delta updates,
`--config file.json` for repeatable configurations, `--clip` to copy
straight to the clipboard, `--dry-run` (with `--rebuild`) to preview without
writing to disk.

---

# Part 2 — Contributing to this repo

## Quick start

```bash
pytest tests/
```

The suite sits at around **~98 passed, 1 skipped**. The skip is **expected**:
it corresponds to a tree-sitter test that only runs when the optional
tree-sitter packages are installed. Do not try to "fix" it or make it
mandatory.

If you're asked to add a feature or fix a bug, default to preserving the two
properties described in Part 1 — modular per-language parsers and
rebuild reversibility — unless the user explicitly asks to change them.

A v5.x direction is already on the roadmap: exposing this tool as a Claude
Skill / MCP tool so an agent can trigger it directly rather than going
through the CLI. Keep this in mind if you're touching the public API
surface (`assemble_codebase`, `assemble_from_config`, `CodebaseRebuilder`) —
favor designs that would work cleanly as a callable tool, not just a CLI
wrapper.

## Known pitfalls / rules to follow

**CLI + `--config`: overrides must be forwarded explicitly.**
The `--config file.json` + additional CLI flags pattern (`--compress`,
`--since`, etc.) is fragile by design: a CLI flag does NOT automatically
apply on top of the JSON. Any new option must be explicitly passed through
to `assemble_from_config`, with the CLI value taking precedence over the JSON
value. This is already the case for `--compress` and `--since`; if you add a
CLI option, verify that this forwarding exists for it too.

**Tree-sitter is an optional dependency, never mandatory.**
Compression (`--compress`) relies on stdlib `ast` for Python (always
available) and on individual per-language tree-sitter packages for everything
else (`tree-sitter-javascript`, `tree-sitter-rust`, etc.). If a tree-sitter
parser is missing, `compress()` must return the original content without
raising an exception — never let the assembly crash because of a missing
parser.

**`_detect_language` (formatters.py): extension first, filename as
fallback.** Language detection for syntax highlighting first tries the
extension via `LANGUAGE_MAP`, then falls back to a list of exact filenames
(`Dockerfile`, `Makefile`, `Procfile`, `.env*`, `CMakeLists.txt`). If you
modify this function, rerun `tests/test_formats.py` to verify these special
cases are still covered.

**`normalize_path` (utils.py): no resolution against CWD.**
Normalization converts to POSIX lowercase but deliberately never resolves
the path against the current working directory, in order to remain
independent of the execution environment. Do not replace it with
`Path.resolve()` or equivalent.

**`os.path.commonpath`: keep the Windows multi-drive fallback.**
On Windows, `commonpath` raises a `ValueError` if the analyzed paths are on
different drive letters (`C:\` and `D:\`). The current fallback falls back
to `os.getcwd()` — keep this if you touch `analyzers.py`.

**`--dry-run` : ni écriture de fichiers, ni création du dossier de sortie.**
`CodebaseRebuilder.rebuild()` n'appelle `output_dir.mkdir()` que si
`dry_run` est `False`. En mode dry-run, chaque fichier déclenche un simple
`print("[DRY-RUN] Would create: ...")` et incrémente le compteur, sans
aucune opération d'I/O — le dossier `output_dir` ne doit pas exister à la
fin. Si vous ajoutez une étape au pipeline de rebuild (ex. écriture d'un
rapport, copie d'assets), placez-la après la vérification `if self.dry_run`
et assurez-vous qu'elle ne déclenche pas de création de répertoire ou de
fichier. Couvert par `test_dry_run` dans `test_rebuild.py`.

## Testing conventions

A fixed bug = a regression test added to `tests/test_robustness.py`, named
in a way that explicitly identifies the bug it covers (not a generic name
like `test_edge_case_1`). The test's docstring should explain the scenario
that caused the bug, not just what it checks.

Encoding: always use explicit `encoding='utf-8'` on file operations, with no
exceptions. This is already systematic in the existing code — keep it that
way.

## Known limitations — do not oversell

- Compression on complex Python patterns (nested decorators, dataclasses,
  metaclasses) is not yet covered by dedicated tests. Treat `--compress` as
  "best-effort" on these cases, not as guaranteed robust, until real-world
  feedback or tests confirm it.
- Individual tree-sitter parsers (0.21+ API) are not all equally mature
  across languages. Do not assume uniform compression quality between
  Python (ast, reliable) and tree-sitter-based languages.
```



<!-- CODE_ASSEMBLER_METADATA
{
  "version": "4.5.2",
  "generated_at": "2026-06-30 14:59:32",
  "files": {
    "src/code_assembler/__init__.py": "2026-02-17 09:29",
    "src/code_assembler/__main__.py": "2026-02-17 09:29",
    "src/code_assembler/analyzers.py": "2026-05-02 05:32",
    "src/code_assembler/cli.py": "2026-06-30 11:19",
    "src/code_assembler/compressor.py": "2026-05-02 04:59",
    "src/code_assembler/config.py": "2026-05-02 05:32",
    "src/code_assembler/constants.py": "2026-06-30 11:19",
    "src/code_assembler/core.py": "2026-05-02 05:53",
    "src/code_assembler/delta.py": "2026-05-02 05:33",
    "src/code_assembler/file_io.py": "2026-02-17 09:29",
    "src/code_assembler/formatters.py": "2026-02-17 09:29",
    "src/code_assembler/interactive.py": "2026-05-02 05:33",
    "src/code_assembler/rebuilder.py": "2026-06-30 11:16",
    "src/code_assembler/templates/components/architecture.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/file_block.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/readme_context.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/stats_table.md.j2": "2026-02-14 19:44",
    "src/code_assembler/templates/components/toc.md.j2": "2026-02-16 16:43",
    "src/code_assembler/templates/main_header.md.j2": "2026-02-16 16:59",
    "src/code_assembler/utils.py": "2026-05-02 05:33",
    "examples/__init__.py": "2026-01-25 11:22",
    "examples/advanced_config.py": "2026-02-17 11:20",
    "examples/basic_usage.py": "2026-02-17 11:26",
    "examples/interactive_demo.py": "2026-01-25 16:13",
    "examples/rebuild_usage.py": "2026-02-17 11:28",
    "docs/INTERACTIVE_DEMO.md": "2026-01-25 16:17",
    "tests/__init__.py": "2026-01-25 11:21",
    "tests/test_clipboard.py": "2026-05-02 05:40",
    "tests/test_compressor.py": "2026-05-02 05:11",
    "tests/test_config.py": "2026-02-17 09:29",
    "tests/test_core.py": "2026-02-17 09:29",
    "tests/test_delta_scenario.py": "2026-02-17 09:29",
    "tests/test_file_io.py": "2026-02-17 09:29",
    "tests/test_formats.py": "2026-02-17 09:29",
    "tests/test_interactive.py": "2026-02-17 09:29",
    "tests/test_rebuild.py": "2026-06-30 11:23",
    "tests/test_robustness.py": "2026-05-02 05:37",
    "tests/test_utils.py": "2026-02-17 09:29",
    "ROADMAP.md": "2026-06-30 11:19",
    "README.md": "2026-06-30 11:19",
    "QUICKSTART_INTERACTIVE.md": "2026-02-17 09:22",
    "INTERACTIVE_MODE.md": "2026-02-17 09:20",
    "BUILD_AND_RELEASE.md": "2026-06-30 11:19",
    "CHANGELOG.md": "2026-06-30 14:40",
    "AGENTS.md": "2026-06-30 14:59"
  }
}
-->