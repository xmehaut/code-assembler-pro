---
type: source-bundle
generator: code-assembler-pro
generator_version: "4.5.2"
source_repo: https://github.com/xmehaut/code-assembler-pro
agents_doc: https://github.com/xmehaut/code-assembler-pro/blob/v4.5.2/AGENTS.md
rebuild: "pip install code-assembler-pro && code-assembler --rebuild <this-file> --output-dir <dir>"
generated_at: "2026-08-22T11:37:17"
files: 14
tokens_estimate: 24765
---

# Consolidated Codebase

> **Snapshot:** 2026-08-22 11:37 | **Files:** 14 | **Tokens:** ~24,765

---

## Table of Contents

- `__init__.py` | 2026-02-17 09:29
- `__main__.py` | 2026-02-17 09:29
- `analyzers.py` | 2026-05-02 05:32
- `cli.py` | 2026-06-30 11:19
- `compressor.py` | 2026-05-02 04:59
- `config.py` | 2026-05-02 05:32
- `constants.py` | 2026-08-22 11:19
- `core.py` | 2026-08-22 11:19
- `delta.py` | 2026-05-02 05:33
- `file_io.py` | 2026-02-17 09:29
- `formatters.py` | 2026-08-22 11:19
- `interactive.py` | 2026-05-02 05:33
- `rebuilder.py` | 2026-08-22 11:19
- `templates/`
  - `components/`
- `utils.py` | 2026-05-02 05:33


---

## Architecture

**Components:**
- `templates/` (0 file)

**File types:**
- `.py` (python): 14 — 100.0%


---

## Stats

**14** files | **2,677** lines | ~**24,765** tokens | Extensions: py


---

14 source files follow below.

---


## `src\code_assembler\__init__.py`

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

## `src\code_assembler\__main__.py`

```python
"""
Entry point for: python -m code_assembler
"""
from .cli import main

if __name__ == "__main__":
    main()

```

## `src\code_assembler\analyzers.py`

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

## `src\code_assembler\cli.py`

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

## `src\code_assembler\compressor.py`

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

## `src\code_assembler\config.py`

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

## `src\code_assembler\constants.py`

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

# Canonical source repository, used in the frontmatter block (source_repo,
# agents_doc) so an agent reading a generated snapshot can locate the
# rebuild instructions without depending on network access to resolve them.
REPO_URL = "https://github.com/xmehaut/code-assembler-pro"

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

## `src\code_assembler\core.py`

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

        # Generated separately from generate_header() and prepended only
        # here, i.e. after the delta_summary substitution above: this
        # block starts and ends with its own "---" delimiters, and doing
        # the substitution first (on `header` alone) guarantees it can
        # never mistake the frontmatter's own "---" for the header's.
        frontmatter = self.formatter.generate_frontmatter(self.stats)

        metadata_block = self.formatter.generate_metadata_block(self.toc_entries)

        if self.config.show_progress:
            self._print_summary()

        return frontmatter + header + "\n\n" + full_content + metadata_block

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

## `src\code_assembler\delta.py`

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

## `src\code_assembler\file_io.py`

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

## `src\code_assembler\formatters.py`

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
from .constants import LANGUAGE_MAP, EMOJI, __version__, REPO_URL
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

    def generate_frontmatter(self, stats: CodebaseStats) -> str:
        """
        Generate a small YAML frontmatter block for the very top of the
        document — loosely inspired by Google's Open Knowledge Format
        (OKF) conventions, kept intentionally minimal since this remains
        a single portable file, not an OKF multi-file bundle.

        Deliberately rendered as its own template, separate from
        `generate_header` / `main_header.md.j2`: that template's first
        bare "---" is the anchor `assemble()` replaces to inject
        `delta_summary`. Prepending a block that starts and ends with
        "---" directly inside that template would shift which "---" is
        the first one in the document and silently misplace the delta
        summary. Kept as a standalone block, added by the caller after
        the delta substitution has already run on the header alone.

        Numeric fields are passed raw (not `format_number`-formatted,
        which adds thousands separators) since this block is meant to be
        machine-parsed as YAML, not read as prose.
        """
        data = {
            "repo_url": REPO_URL,
            "now_iso": datetime.now().isoformat(timespec="seconds"),
            "total_files": stats.total_files,
            "estimated_tokens": stats.estimated_tokens,
        }
        return self.render("components/frontmatter.md.j2", data)

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

## `src\code_assembler\interactive.py`

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

## `src\code_assembler\rebuilder.py`

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

    def _find_boundary_positions(self) -> List[int]:
        """
        Every position in the document that must bound a file's content
        window: real file headers (path + immediate fence) AND
        directory-level "README context" headings injected by
        `readme_context.md.j2`.

        The latter are not files — they carry no path in backticks, no
        fence immediately follows them, and they are never a key in the
        embedded metadata — so `_find_real_file_headers` never returns
        them. But they are still a real document boundary: if a
        preceding file's search window is bounded only by the *next real
        file header*, it silently extends across an intervening README
        section. When that section's own prose contains a nested ```
        example, the example's closing fence becomes the new "last bare
        fence" inside the preceding file's window, and
        `_extract_file_content` swallows the README section (and
        everything up to that nested close) into the preceding file.
        Regression: CHANGELOG.md [4.5.2] known limitation, ~7 files on a
        real monorepo snapshot; root-caused and fixed here.
        """
        positions = [start for _, start, _ in self._find_real_file_headers()]
        readme_heading_re = re.compile(
            r'^#+[ \t]+README context[ \t]*\r?$',
            re.MULTILINE | re.IGNORECASE
        )
        positions.extend(m.start() for m in readme_heading_re.finditer(self.md_content))
        return sorted(positions)

    def _extract_file_content(self, rel_path: str) -> Optional[str]:
        """
        Find and extract the content of a specific file from the Markdown.
        Robust against path separators, blank lines, duplicate filenames at
        different paths, nested ``` fences inside the file's own content
        (a markdown file documenting code blocks, a README showing
        examples, etc.), and an intervening directory-level "README
        context" section between this file and the next real file header
        — see `_find_real_file_headers` and `_find_boundary_positions` for
        why a single validated scan is used instead of a per-call regex
        search.
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

        # Bound by the next boundary of ANY kind — a real file header or
        # a "README context" heading — not just the next real file
        # header, so an intervening README section can never leak past
        # its own start into this file's window.
        boundaries = self._find_boundary_positions()
        content_end_bound = next(
            (pos for pos in boundaries if pos > content_start),
            len(self.md_content)
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

# `templates/`

## `components/`

## `src\code_assembler\utils.py`

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



<!-- CODE_ASSEMBLER_METADATA
{
  "version": "4.5.2",
  "generated_at": "2026-08-22 11:37:17",
  "files": {
    "src/code_assembler/__init__.py": "2026-02-17 09:29",
    "src/code_assembler/__main__.py": "2026-02-17 09:29",
    "src/code_assembler/analyzers.py": "2026-05-02 05:32",
    "src/code_assembler/cli.py": "2026-06-30 11:19",
    "src/code_assembler/compressor.py": "2026-05-02 04:59",
    "src/code_assembler/config.py": "2026-05-02 05:32",
    "src/code_assembler/constants.py": "2026-08-22 11:19",
    "src/code_assembler/core.py": "2026-08-22 11:19",
    "src/code_assembler/delta.py": "2026-05-02 05:33",
    "src/code_assembler/file_io.py": "2026-02-17 09:29",
    "src/code_assembler/formatters.py": "2026-08-22 11:19",
    "src/code_assembler/interactive.py": "2026-05-02 05:33",
    "src/code_assembler/rebuilder.py": "2026-08-22 11:19",
    "src/code_assembler/utils.py": "2026-05-02 05:33"
  }
}
-->