# Changelog

All notable changes to Code Assembler Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.2.0] - 2026-01-25

### 🎉 Added - Interactive Mode

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
  - `INTERACTIVE_MODE.md` - Comprehensive guide
  - `QUICKSTART_INTERACTIVE.md` - 5-minute getting started guide
  - `examples/interactive_demo.py` - Example usage

### 🔧 Changed

- **CLI Enhancement:**
  - Added `--interactive` / `-i` flag to launch wizard
  - Updated help text and documentation

- **API Extension:**
  - Exported `run_interactive_mode` from main `__init__.py`
  - Added to `__all__` for clean imports

### 🧪 Tests

- Added `tests/test_interactive.py` with comprehensive test coverage:
  - Yes/No question handling
  - Number input validation
  - Text input with defaults
  - Path selection logic
  - Extension preset selection
  - Full wizard flow simulation
  - Keyboard interrupt handling

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

### 🎯 Major Refactor - Multi-Module Architecture

- **Modular Structure:**
  - `constants.py` - All constants and mappings
  - `config.py` - Configuration dataclasses
  - `utils.py` - Utility functions
  - `file_io.py` - File reading/writing
  - `formatters.py` - Jinja2-based markdown generation
  - `analyzers.py` - Architecture analysis
  - `core.py` - Main assembly engine

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

- 🎉 **Added** - New features
- 🔧 **Changed** - Changes in existing functionality
- 🐛 **Fixed** - Bug fixes
- 🗑️ **Deprecated** - Soon-to-be removed features
- 🔥 **Removed** - Removed features
- 🔒 **Security** - Security fixes
- 🧪 **Tests** - Test additions/changes
- 📚 **Documentation** - Documentation changes
