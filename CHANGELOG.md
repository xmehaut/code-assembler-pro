# Changelog
 

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