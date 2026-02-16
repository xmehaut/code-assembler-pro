## [4.4.0] - 2026-02-16

### Added

- **Reliable Delta Mode (`--since`)**
  - Ability to generate a Markdown update containing only files modified, added, or deleted since a previous snapshot.
  - Drastically reduces token usage for iterative LLM sessions by sending only changes.
- **Hidden Metadata Injection**
  - Injects a hidden JSON block (`<!-- CODE_ASSEMBLER_METADATA -->`) at the end of generated files.
  - Stores exact relative paths and modification timestamps (mtime) for 100% reliable change detection.
- **Duplicate Filename Support**
  - Accurate tracking of files with identical names in different directories (e.g., multiple `__init__.py` or `config.py`).
- **New Test Suite**
  - Added `tests/test_delta_scenario.py` to validate complex delta scenarios, including duplicate filenames and cross-platform path handling.

### Fixed

- **Cross-Platform Path Normalization**
  - Fixed a critical bug where Windows backslashes (`\`) and case sensitivity caused delta mismatches.
  - All internal keys are now normalized to lowercase with POSIX forward slashes (`/`).
- **Regex Parsing Fragility**
  - Replaced the experimental visual TOC parsing with structured JSON metadata to avoid errors caused by indentation or date formatting changes.

### Changed

- **`delta.py` Refactor**: Completely rewritten to prioritize metadata-based analysis.
- **`formatters.py`**: Updated to handle JSON metadata generation and injection.
- **`core.py`**: Integrated the delta filtering pipeline and metadata block generation into the main assembly flow.
- **Module Documentation**: Added comprehensive technical docstrings to the `delta.py` module.

---

## [4.3.2] - 2026-02-16

### Fixed

- **Interactive mode: comma-separated extensions corrupted JSON config**
  - When a user typed extensions with commas (e.g. `.py, .yaml, .tsx,`), the wizard
    preserved the commas inside the strings (e.g. `".py,"`) causing zero files to match
  - `_select_extensions()` in `interactive.py` now strips commas before parsing:
    `extensions_input.replace(',', ' ').split()` + `rstrip(',')` as double safety
  - Regression test added: `test_select_extensions_custom_with_commas` in `test_interactive.py`