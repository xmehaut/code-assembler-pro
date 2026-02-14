# Changelog

All notable changes to Code Assembler Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.3.1] - 2026-02-14

### Changed - LLM-Optimized Templates

- **Templates rewritten for minimal token overhead (-71%)**
  - `main_header.md.j2`: removed Recommended Prompts, Purpose section, tool version, emojis (689 → 61 tokens)
  - `file_block.md.j2`: path + code fence only, removed size/lines/emoji/HTML anchors (45 → 16 tokens per file)
  - `stats_table.md.j2`: one compact line instead of Markdown table (178 → 56 tokens)
  - `architecture.md.j2`: removed naive pattern detection and depth distribution (178 → 66 tokens)
  - `toc.md.j2`: removed emojis and file sizes (70 → 48 tokens)
  - `readme_context.md.j2`: removed blockquote format (27 → 13 tokens)

- **Simplified directory headers** in `formatters.py`
  - Removed emojis and HTML anchors from directory headers
  - Cleaner output: `# \`src/\`` instead of `# 📁 src<a name="...">`

### Added

- **`ROADMAP.md`** — Complete feature roadmap with 19 planned features
  - Rebuild from Markdown, diff mode, clipboard, profiles
  - Security: secret detection, integrity manifest, encryption
  - UI: viewer + assembler + integrated chat
  - Skill Claude for automated workflows
- **`BUILD_AND_RELEASE.md`** — Step-by-step build and publish guide

---

## [4.3.0] - 2026-02-14

### Fixed - 14 Bug Fixes

- **Interactive mode never triggered** (critical): `--interactive` flag was parsed but never checked in `main()`
- **Corrupted Markdown output** (critical): code fence in `file_block.md.j2` was never closed
- **Broken test** (critical): missing `import sys` in `test_file_io.py`
- **Overly aggressive exclusions**: "dist" excluded "redistribute.py", "env" excluded "environment.py"
- **Encoding performance**: file read 3 times; now samples 64KB only
- **normalize_path depends on CWD**: replaced `resolve()` with `PurePosixPath`
- **Fragile `__main__.py`**: simplified from 22 lines to 6
- **output/output_file inconsistency**: normalized in `assemble_from_config()`
- **format_file_size(0)** returned "0.0B" instead of "0B"
- **Version duplicated**: now uses `importlib.metadata`
- **Missing template guard**: `formatters.py` raises clear error if templates dir missing
- **Test mock too broad**: scoped `os.path.exists` mock to module

### Added

- **Exact filename matching**: `Dockerfile`, `Makefile` in extensions config
- **`--show-excludes`**: display default exclusion patterns and exit
- **`--save-config FILE`**: save CLI arguments as reusable JSON config
- **Cross-platform emoji**: Unicode on modern terminals, ASCII fallback on legacy Windows

### Changed

- Exclusion logic rewritten with exact match, glob, and extension modes
- Encoding detection uses 64KB sample instead of full file read

---

## [4.2.0] - 2026-01-25

### Added - Interactive Mode

- **Interactive Wizard Mode** (`--interactive` / `-i`)
  - 5-step guided configuration process
  - Smart defaults and validation
  - Extension presets for common project types (Python, JS/TS, Rust, Go, Java, C/C++)
  - Optional configuration saving to JSON
  - Graceful keyboard interrupt handling

- **New Module:** `code_assembler/interactive.py`

### Changed

- Added `--interactive` / `-i` flag to CLI
- Exported `run_interactive_mode` from `__init__.py`

---

## [4.1.0] - 2026-01-24

### Added

- **Smart File Truncation**
  - `truncate_large_files` option (default: `True`)
  - `truncation_limit_lines` option (default: 500)
  - Preserves imports and key code instead of skipping large files

- **New Function:** `read_file_head()` in `file_io.py`

---

## [4.0.0] - 2026-01-23

### Major Refactor - Multi-Module Architecture

- Modular structure: constants, config, utils, file_io, formatters, analyzers, core
- Jinja2 templates for markdown generation
- Enhanced architecture analysis
- Comprehensive test suite
- `pyproject.toml` for modern packaging

---

## [3.0.0] - 2026-01-20

### Added

- Initial monolithic version
- Basic file concatenation
- Table of contents generation
- Architecture analysis
- Token estimation
