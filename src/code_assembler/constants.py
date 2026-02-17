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
    __version__ = "4.2.1"  # Fallback for dev mode without pip install

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
