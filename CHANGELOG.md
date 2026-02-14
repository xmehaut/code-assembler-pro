# Changelog

All notable changes to Code Assembler Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.3.0] - 2026-02-14

### 🐛 Fixed — Critical Bug Fixes

- **Interactive mode was never triggered** (`cli.py`)
  - `--interactive` / `-i` flag was parsed but never checked in `main()`
  - The wizard was completely inaccessible via CLI since v4.2.0

- **Markdown output was corrupted** (`file_block.md.j2`)
  - Code fence ` ``` ` was never closed in the template
  - All files merged into one giant code block in the output

- **`test_file_io.py` crashed on import** — missing `import sys`

- **Exclusion false positives** (`utils.py`)
  - Pattern `"dist"` incorrectly excluded files like `redistribute.py`
  - Pattern `"env"` incorrectly excluded `environment.py`
  - Now uses exact segment matching + `fnmatch` glob patterns

- **`normalize_path()` depended on CWD** (`utils.py`)
  - Used `Path.resolve()` which made behavior environment-dependent
  - Now uses `PurePosixPath` for consistent cross-platform normalization

- **`detect_encoding()` read entire files into memory** (`file_io.py`)
  - Now reads only a 64KB sample for encoding detection

- **`__main__.py` had fragile import logic**
  - Simplified to a clean relative import that works in all contexts

- **`output` / `output_file` parameter confusion** (`core.py`)
  - `assemble_from_config()` now explicitly handles both JSON key names

- **Emoji display corrupted on Windows PowerShell**
  - All hardcoded emoji replaced with `EMOJI` dict references
  - Auto-detection: real emoji on modern terminals, ASCII fallback on legacy
  - File error markers changed from emoji to `[ERROR]` prefix for reliability

### 🎉 Added — New Features

- **Exact filename matching** (e.g., `Dockerfile`, `Makefile`)
  - Extensions like `Dockerfile` are now matched by exact name, not as `.Dockerfile`
  - Works in both JSON config and CLI `--ext`

- **`--show-excludes` flag**
  - Displays all default exclusion patterns and exits
  - `code-assembler --show-excludes`

- **`--save-config FILE` flag**
  - Saves current CLI arguments as a reusable JSON configuration file
  - `code-assembler . --ext py md Dockerfile --save-config my_config.json`

- **`source_chars` tracking** (`CodebaseStats`)
  - Tracks source code characters separately from total output (which includes formatting)

- **Version from `importlib.metadata`** (`constants.py`)
  - Single source of truth: version is read from installed package metadata
  - Fallback to hardcoded value in dev mode

- **Templates directory guard** (`formatters.py`)
  - Clear `FileNotFoundError` if templates are missing from `.whl`

### 🔧 Changed

- **Exclusion patterns now require explicit globs**
  - Old: `"test_"` matched any file starting with `test_` (implicit prefix)
  - New: `"test_*"` required for glob matching, `"test_"` is exact only
  - Extension patterns like `".pyc"` still work via suffix matching

- **`format_file_size(0)`** now returns `"0B"` instead of `"0.0B"`
- **`format_file_size(512)`** now returns `"512B"` instead of `"512.0B"`

### 🧪 Tests

- Fixed `test_file_io.py` — added missing `import sys`
- Updated `test_utils.py` — new exclusion test cases (false positives, globs)
- Updated `test_interactive.py` — scoped `os.path.exists` mocks, output conflict handling

### 📚 Documentation

- Updated README.md — new CLI options, exact filename support, v4.3.0
- Updated CHANGELOG.md — comprehensive v4.3.0 release notes
- Updated INTERACTIVE_MODE.md — exact filenames mention
- Updated QUICKSTART_INTERACTIVE.md — new tips

---

## [4.2.0] - 2026-01-25

### 🎉 Added — Interactive Mode

- **Interactive Wizard Mode** (`--interactive` / `-i`)
  - 5-step guided configuration process
  - Smart defaults and validation
  - Extension presets for common project types (Python, JS/TS, Rust, Go, Java, C/C++)
  - Optional configuration saving to JSON
  - Graceful keyboard interrupt handling
  
- **New Module:** `code_assembler/interactive.py`
  - `InteractiveWizard` class for programmatic use
  - `run_interactive_mode()` function for CLI integration

- **Documentation:**
  - `INTERACTIVE_MODE.md` — Comprehensive guide
  - `QUICKSTART_INTERACTIVE.md` — 5-minute getting started guide
  - `examples/interactive_demo.py` — Example usage

### 🔧 Changed

- **CLI Enhancement:**
  - Added `--interactive` / `-i` flag to launch wizard
  - Updated help text and documentation

- **API Extension:**
  - Exported `run_interactive_mode` from main `__init__.py`
  - Added to `__all__` for clean imports

### 🧪 Tests

- Added `tests/test_interactive.py` with comprehensive test coverage

### 📚 Documentation

- Updated main README.md with Interactive Mode section
- Created dedicated Interactive Mode guide
- Added quickstart guide for new users

---

## [4.1.0] - 2026-01-24

### Added

- **Smart File Truncation**
  - `truncate_large_files` option (default: `True`)
  - `truncation_limit_lines` option (default: 500)
  - Preserves imports and key code instead of skipping large files

- **New Function:** `read_file_head()` in `file_io.py`
  - Efficiently reads first N lines without loading entire file

### Changed

- Improved large file handling logic in `core.py`
- Enhanced progress messages with truncation indicators
- Updated configuration dataclass with new options

---

## [4.0.0] - 2026-01-23

### 🎯 Major Refactor — Multi-Module Architecture

- **Modular Structure:**
  - `constants.py` — All constants and mappings
  - `config.py` — Configuration dataclasses
  - `utils.py` — Utility functions
  - `file_io.py` — File reading/writing
  - `formatters.py` — Jinja2-based markdown generation
  - `analyzers.py` — Architecture analysis
  - `core.py` — Main assembly engine

- **Jinja2 Templates:**
  - Separated presentation from logic
  - Template files in `templates/` and `templates/components/`
  - Cleaner, more maintainable code

- **Enhanced Analysis:**
  - Pattern detection (MVC, Testing, API structures)
  - File distribution statistics
  - Depth analysis

### Added

- Comprehensive test suite (`tests/`)
- Example scripts (`examples/`)
- Professional documentation
- `pyproject.toml` for modern packaging

---

## [3.0.0] - 2026-01-20

### Added

- Initial monolithic version
- Basic file concatenation
- Table of contents generation
- Architecture analysis
- Token estimation

---

## Legend

- 🎉 **Added** — New features
- 🔧 **Changed** — Changes in existing functionality
- 🐛 **Fixed** — Bug fixes
- 🗑️ **Deprecated** — Soon-to-be removed features
- 🔥 **Removed** — Removed features
- 🔒 **Security** — Security fixes
- 🧪 **Tests** — Test additions/changes
- 📚 **Documentation** — Documentation changes
