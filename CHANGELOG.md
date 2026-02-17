# Changelog

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
- 
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
    preserved the commas inside the strings (e.g. `".py,"`) causing zero files to match
  - `_select_extensions()` in `interactive.py` now strips commas before parsing:
    `extensions_input.replace(',', ' ').split()` + `rstrip(',')` as double safety
  - Regression test added: `test_select_extensions_custom_with_commas` in `test_interactive.py`