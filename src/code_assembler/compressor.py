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