# Changelog
 
## [4.7.0]

### Added

- `depends_on` (per-module, JSON-only, MODULES_SPEC.md §6): a list of
  other module names in the same `modules` block. Purely declarative —
  echoed into the frontmatter, no import analysis. Validated at
  config-parse time: an unknown module name or a module depending on
  itself is a hard error before any file is written. Deliberately not
  inheritable from the config root (a root-level `depends_on` would
  apply to every module including the one it names).
- `siblings` in the frontmatter (§7): every other module in the same
  batch, with its file name, description, and token count — so an
  agent can decide which sibling to open next without opening any of
  them first. Every module in a batch shares one `generated_at`,
  computed once, rather than drifting by the few milliseconds between
  per-module writes.
- `module` in the frontmatter: the current file's own module name,
  present only in batch-mode output.

- `modules` (JSON-only config key, MODULES_SPEC.md §2-4): assemble a
  monorepo's sub-projects in a single pass, one output file per module.
  Each module declares its own `paths`; every other root-level key
  (`extensions`, `exclude_patterns`, `compress`, `description`, …) is
  inherited by default and can be replaced (not merged) per module.
  Output filenames are derived from the root `output`
  (`codebase.md` → `codebase_api.md`), or set explicitly per module.
  `--since` and CLI overrides (`--compress`, `--description`) are
  explicitly rejected on a `modules` config rather than guessed at.
- `config.resolve_module_configs()`: validates a whole `modules` block
  before any file is written — unknown shape, missing `paths`, missing
  `extensions`, or a module name containing a path separator all raise
  immediately.
- `core.assemble_modules()`: one bad module (bad path, permission
  error) does not abort the batch — the rest still get built, and the
  failure is reported in the returned summary.

- New optional `description` field (spec: `MODULES_SPEC.md` §5), exposed
  via `--description` on the CLI and as a root-level `"description"` key
  in JSON configs. Pure passthrough into the frontmatter — no validation
  or generation logic. Free-text content is escaped with `json.dumps()`
  rather than hand-rolled quoting, since a description containing a
  quote, colon, or backslash would otherwise produce invalid or silently
  wrong YAML.
- **Backward compatible by construction**: the field is omitted from the
  frontmatter entirely when not set — never rendered as
  `description: null` or `description: ""` — so a run that doesn't use
  it produces byte-for-byte the same frontmatter as 4.6.x. Covered by
  `tests/test_core.py::TestFrontmatter::test_no_description_keeps_frontmatter_at_4_6_x_shape`.

- First step of the multi-module monorepo feature described in
`MODULES_SPEC.md` — `modules`, `depends_on`, and `siblings` follow in
subsequent steps.

### Fixed

- `assemble_codebase()` never raised on a path that doesn't exist —
  it silently produced a near-empty snapshot. Harmless for a single,
  deliberate call, but wrong for a `modules` batch, where a bad path
  in one module must not look identical to success. `assemble_modules()`
  now checks path existence explicitly before assembling each module.

Second step of the multi-module feature (`MODULES_SPEC.md`). `depends_on`
and `siblings` (frontmatter cross-references) are the remaining step.
- **Fix**: `--description` broke `test_clipboard.py::test_cli_calls_clipboard`
  and, latently, three Namespace fixtures in `test_robustness.py` — all four
  construct `argparse.Namespace` by hand (mocking `parse_args`) rather than
  going through the real parser, so they don't automatically pick up new
  argparse defaults the way a real CLI invocation does. Added
  `description=None` to each.

### Changed

- `formatters.generate_frontmatter()` now takes `total_files` /
  `estimated_tokens` as plain ints instead of a `CodebaseStats`
  instance — internal signature change, no effect on generated output
  for existing callers.

This completes the multi-module monorepo feature described in
`MODULES_SPEC.md` (all of §2-7 now implemented). Suggested version:

## [4.6.1] - 2026-08-23

### Fixed

- `rebuilder.py`: `_extract_metadata()` took the first regex match in
  the document instead of the last. Since `core.py` always appends the
  real metadata block after all file content, it is structurally
  guaranteed to be the last match — but not the only one. Any file
  documenting this exact feature in prose (e.g. a CHANGELOG entry
  reading "Injects a hidden JSON block (`<!-- CODE_ASSEMBLER_METADATA
  ... -->`)...") creates an earlier, non-JSON decoy that made rebuild
  fail with "No valid metadata found" even though a valid block existed
  at the true end of the file. Found by running code-assembler on its
  own source tree.
- `rebuilder.py`: the truncation-warning check used a bare substring
  search (`"[TRUNCATED]" in content`), which false-positived on any file
  whose own legitimate content mentions that string — `core.py` (defines
  the marker), `rebuilder.py` and the test suite (reference it). Now
  anchored on the real marker's exact final line
  ("# Only the first N lines are shown for context.") as a true suffix.
  Same root cause and same discovery path as the metadata fix above.

Regression tests: `tests/test_metadata_last_match.py`,
`tests/test_rebuild.py::TestRebuild::test_truncation_false_positive_on_legitimate_content`
(and `test_truncation_warning` corrected to use the real marker format
instead of an unrealistic hand-crafted one).

- `assemble_modules` was missing from `code_assembler/__init__.py`'s
  exports — `from code_assembler import assemble_modules` raised
  `ImportError`. Now exported alongside `assemble_codebase` /
  `assemble_from_config`.
- `assemble_modules()`'s frontmatter-patching phase (§9 phase 2) passed
  the regenerated frontmatter directly as `re.sub()`'s replacement
  argument. `re.sub()` interprets backslashes in a *string* replacement
  as backreferences, and `json.dumps()` escapes non-ASCII characters as
  `\uXXXX` — a description containing an em-dash (or any non-ASCII
  character) produced `bad escape \u` and crashed the batch. Found by
  running the exact JSON from this release's own README example.
  Fixed by passing a function instead of a string to `re.sub()`.

### Docs

- `README.md`: added the `modules`/`depends_on`/`siblings` feature
  (new "Monorepo Assembly" section, a Programmatic API example, a Key
  Features bullet, a Why point) and `description` (missing from the
  CLI options table and the JSON template/reference despite already
  shipping) — neither had been documented since the feature landed
  across three earlier commits.
- `examples/modules_usage.py`: new, mirrors the style of the four
  existing examples. Verified it runs end-to-end from the project root.

## [4.6.0] - 2026-08-22
### Changed

- Consolidated `README.md`, `QUICKSTART_INTERACTIVE.md`, and
  `INTERACTIVE_MODE.md` into a single `README.md`. The two removed files
  duplicated content already shown live by the tool itself (wizard steps,
  configuration summary) or repeated the "Round-Trip Workflow" narrative
  already covered in README's Quick Start — four independent rewrites of
  the same workflow across the three files, none kept in sync (both
  removed files were still titled "(v4.4.0)" despite the package being at
  4.5.2). The new `## 🧙 Interactive Mode` section keeps only what was
  genuinely unique: the wizard's FAQ, keyboard shortcuts, and the
  `--save-config` bridge to JSON config.
- Removed the `Recommended Use Cases` section from `README.md`: 3 of its
  4 entries repeated the same commands already shown in `Quick Start`
  under different headings.
- `Advanced Configuration (JSON)` section rewritten with a complete,
  directly-runnable template covering every `AssemblerConfig` field
  (the previous example silently omitted `show_progress` and
  `use_default_excludes`), a field-by-field reference table, and an
  explanation of the CLI-flags-override-JSON mechanism — previously
  documented only in `AGENTS.md`, invisible to a human reading the
  README.
- `CLI Options Reference` table completed with five flags that exist in
  `cli.py` but were missing from the table: `--save-config`,
  `--show-excludes`, `--no-recursive`, `--no-readmes`,
  `--no-default-excludes`.

### Added

- Every generated snapshot now starts with a small YAML frontmatter
  block, loosely inspired by Google's Open Knowledge Format (OKF)
  conventions (`type`, `generator`, `source_repo`, timestamp, and a
  small set of producer-defined fields) — kept intentionally minimal
  since this remains a single portable file, not an OKF multi-file
  bundle. Exposes `generator_version`, `source_repo`, `agents_doc`
  (pinned to the `v{version}` tag, not a branch, so it always matches
  the exact release that produced the snapshot), and a `rebuild` field
  with the exact command to reconstruct the project — all readable by
  an agent that only looks at the start of a large file, or that has
  no network access to resolve `agents_doc`. Rendered as its own
  template (`components/frontmatter.md.j2`) and prepended in
  `assemble()` only *after* the existing `delta_summary` substitution
  on the header has already run, so its own `---` delimiters can never
  be mistaken for the header's and steal the delta-summary insertion
  point.
- `constants.py`: added `REPO_URL`, the canonical source repository
  used to build `source_repo` and `agents_doc` in the frontmatter.
- `tests/test_core.py`: `TestFrontmatter` — validates the frontmatter
  is well-formed YAML, its numeric fields (`files`, `tokens_estimate`)
  are raw ints rather than comma-formatted display strings, and that
  it never shifts where `delta_summary` gets inserted.
- `tests/test_rebuild.py`: `TestRebuildWithFrontmatter` — end-to-end
  `assemble()` → `--rebuild` round trip confirming the frontmatter is
  correctly ignored by `_find_real_file_headers()` /
  `_find_boundary_positions()`.
- `tests/test_rebuild.py`: `TestRebuildRegressions
  .test_readme_context_section_with_nested_fence_is_not_absorbed` —
  regression test reproducing the bug above in isolation. 
- `AGENTS.md`: guidance file for AI coding agents (Claude, GPT, Cursor,
  Aider, etc.) working on the repository. Documents the rebuild workflow
  for consuming generated snapshots (`--rebuild`), known architectural
  pitfalls (CLI/`--config` override forwarding, tree-sitter as an optional
  dependency, language detection fallback order, path normalization
  behavior, Windows multi-drive handling), testing conventions, and current
  limitations of the compression feature.

### Fixed

- `rebuilder.py`: root-caused and fixed the known limitation noted in
  [4.5.2] — a file's content block was over-captured when immediately
  followed by a directory-level "README context" section rather than
  another file header. `_find_real_file_headers()` only recognizes a
  boundary when a `` `path` `` heading is immediately followed by an
  opening fence; the `### README context` heading emitted by
  `readme_context.md.j2` never satisfies that (a blank line and prose
  follow, not a fence), so it was never counted as a boundary. When such
  a section's own prose contained a nested ``` example, that example's
  closing fence became the "last bare fence" inside the *preceding*
  file's search window, silently merging the README section — and
  everything up to that nested close — into the wrong file.

  Added `_find_boundary_positions()`, which merges real file headers and
  "README context" headings into a single sorted boundary list;
  `_extract_file_content()` now bounds its search window on the next
  boundary of either kind. Verified against a real 136-file / ~354k-token
  snapshot where 4 files (`tot.py`, `fields.py`, `agent.py`,
  `memory/summarizer.py`) previously failed to compile after rebuild —
  all 4 now round-trip cleanly, with zero compilation errors across the
  full snapshot.


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