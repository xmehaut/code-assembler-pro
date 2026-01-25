"""
Constants for Code Assembler Pro.

This module contains all constant values used throughout the package,
including language mappings, file extensions, and default configurations.
"""

from typing import Dict

# In code_assembler/constants.py

# Version
__version__ = "4.2.0"  # Changed from 4.1.0

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

# Emojis for output formatting
EMOJI = {
    "folder": "📁",
    "file": "📄",
    "readme": "ℹ️",
    "success": "✅",
    "warning": "⚠️",
    "error": "❌",
    "rocket": "🚀",
    "chart": "📊",
    "target": "🎯",
    "building": "🏛️",
    "map": "🗺️",
    "book": "📖",
    "bug": "🐛",
    "memo": "📝",
    "mag": "🔍",
    "test": "🧪",
    "recycle": "🔄",
    "bulb": "💡",
    "floppy": "💾",
}

# Header templates
HEADER_LEVELS = {
    "document": 1,
    "section": 2,
    "subsection": 3,
    "file": 2,
}