# 🗺️ Roadmap — Code Assembler Pro

Planned features and vision for future versions, ranked by their impact on the daily LLM-assisted development workflow.

---

## ✅ Completed in v4.4.0 — The "Round-Trip" Milestone

We have successfully closed the loop between local code and AI interfaces.

*   **♻️ Rebuild Mode (`--rebuild`)**: Reconstruct an entire project structure from a Markdown snapshot.
*   **⏱️ Delta Mode (`--since`)**: Incremental updates using a hidden **Metadata Manifest** (JSON) for 100% accuracy.
*   **📋 Clipboard Support (`--clip`)**: Direct ingestion into LLMs without intermediate files.
*   **📝 Enhanced Syntax**: Native support for Jinja2, Terraform, and smart detection for `Dockerfile`/`Makefile`.
*   **🛡️ Metadata Manifest**: Injected JSON block that makes the Markdown file a "self-describing" project container.

---

## ✅ Completed in v4.5.0 — The "Skeleton" Milestone

Code compression reduces third-party libraries to pure API surface, dramatically cutting token usage when giving an LLM context about a dependency.

*   **🗜️ Code Compression (`--compress` / `-z`)**: Reduces source files to structural skeletons — signatures and docstrings only, with bodies replaced by `...`. Python always supported via stdlib `ast` (zero extra dependencies). Other languages (JS, TS, Rust, Go, Java, C, C++…) use individually installed `tree-sitter-<lang>` packages.
*   **Per-language optional extras**: `compress-web`, `compress-systems`, `compress-all` bundles in `pyproject.toml`.
*   **CLI override on `--config`**: `--compress` and `--since` now work correctly when combined with `--config`, with CLI flags taking precedence over JSON values.

---

## ✅ Completed in v4.5.1 — Bug Fix & Robustness Release

Code review identified and fixed several production issues.

*   **`constants.py`**: Removed duplicate keys (`.properties`, `.graphql`, `recycle`). Removed dead code `HEADER_LEVELS`.
*   **`cli.py`**: Implemented `_show_excludes()` (was referenced but never defined → crash). Rebuild errors now displayed to the user.
*   **`config.py`**: Guard against empty extension strings (`IndexError` on `ext[0]`). `compress_level` validation.
*   **`analyzers.py`**: `os.path.commonpath()` now handles Windows multi-drive paths gracefully.
*   **`delta.py`**: Replaced bare `except Exception: pass` with typed handlers that surface real errors.
*   **`utils.py`**: Linux clipboard `xsel` fallback now triggers on `CalledProcessError` and `TimeoutExpired`, not only `FileNotFoundError`. Added `timeout=10` to all subprocess calls.
*   **`core.py`**: `write_file_content()` return value checked — write failures now raise `OSError` instead of silently succeeding.
*   **`interactive.py`**: Fixed double-application of `DEFAULT_EXCLUDE_PATTERNS` via `use_default_excludes`.
*   **28 regression tests** added in `test_robustness.py` — one per bug fixed.

---

## 🔴 High Priority — v4.6.0

### 1. Compression — Edge Cases & Stability

The v4.5 compressor handles standard code well. Real-world projects will hit these:

*   **Python edge cases**: decorators (`@property`, `@staticmethod`, `@dataclass`), `TypedDict`, `Protocol`, `match`/`case` (Python 3.10+), lambda assignments, and `__all__` lists need explicit handling and tests.
*   **Decorated functions**: The decorator lines are preserved but the associated `def` detection may misfire in complex stacking scenarios.
*   **`pass`-only bodies**: Should be normalised to `...` for consistency. Currently `pass` may be kept as-is.
*   **tree-sitter package gaps**: `tree-sitter-kotlin`, `tree-sitter-swift`, `tree-sitter-scala` are not reliably published for the 0.21 API. Offer `tree-sitter-languages` (monolithic 0.20) as a `compress-compat` extra with an adapter shim.
*   **Compression ratio in summary**: After `--compress`, show `Original: X tokens → Compressed: Y tokens (Z% reduction)`.

### 2. 🔒 Secret Scanning (`--scan-secrets`)

Scan files before assembly to detect exposed secrets (AWS keys, API tokens, `.env` content).
*   **Why:** The #1 risk of this tool is accidentally pasting a secret into a Cloud LLM.
*   **Feature:** Block assembly or auto-exclude files containing potential secrets.
*   **Implementation:** Regex patterns for common secret formats + configurable allow-list.

### 3. Configuration Hierarchy

The current approach (JSON config + CLI overrides merged manually) is fragile at scale.
*   **Goal:** Formal precedence chain — `JSON config < environment variables < CLI flags`.
*   **Benefit:** Predictable, documented behaviour; eliminates the class of silent-override bugs found in v4.5.1.
*   **Validate unknown JSON keys**: `"extentions"` instead of `"extensions"` currently surfaces as a cryptic `TypeError`. A `validate_config_keys()` guard would give an actionable message.

---

## 🟡 Medium Priority — v5.0.0

### 4. Project Profiles (`--profile`)

Store named configurations to switch between projects with a single word.
*   **Usage:** `code-assembler --profile mlops`
*   **Why:** Faster than managing multiple JSON config files.
*   **Storage:** `~/.code-assembler/profiles/<name>.json`

### 5. Dependency Summary

Automatically extract dependencies from manifest files (`pyproject.toml`, `package.json`, `go.mod`, etc.).
*   **Why:** Gives the LLM immediate technical stack context without reading every file. Essential for migration or debugging advice.

### 6. Token Budgeting (`--max-tokens`)

Intelligent file selection to stay within a specific token limit.
*   **Strategies:** `recent` (modified first), `entry` (main files first), or `small` (maximise file count).
*   **Why:** Large projects exceed context windows. Smart selection rather than blind truncation.

### 7. Import Graph & Mermaid Support

Static analysis of imports to generate a dependency map.
*   **Why:** Helps the LLM understand the architecture and detect circular dependencies without reading the full source.

---

## 🟠 Long Term — v5.x & Beyond

### 8. 🤖 Claude Skill / MCP Tool

Transform Code Assembler into a tool that Claude can trigger directly.
*   **Concept:** Claude runs the tool, reads the codebase, and applies fixes via `--rebuild` automatically.
*   **Status:** Feasible today via Claude's computer use — worth prototyping.

### 9. Web Interface (Viewer, Assembler & Chat)

A tripartite GUI to assemble projects, navigate the generated Markdown, and chat with an LLM directly on the code.
*   **Viewer:** Interactive file tree on the left, syntax-highlighted code in the center.
*   **Integrated Chat:** A chat panel where the LLM has the full `.md` as context. "Apply fix" button modifies the code in the viewer.

### 10. Watch Mode (`--watch`)

Automatic regeneration whenever a source file changes.
*   **Why:** Perfect for "Live Coding" sessions with an AI. Combine with `--since` for true incremental live mode.

---

## 📋 Roadmap Summary

| Version | Feature | Impact | Status |
|---------|---------|--------|--------|
| **v4.4.0** | Rebuild Mode (`--rebuild`) | 🔴 Critical | ✅ Done |
| **v4.4.0** | Delta Mode (`--since`) | 🔴 Critical | ✅ Done |
| **v4.4.0** | Clipboard Support (`--clip`) | 🔴 High | ✅ Done |
| **v4.5.0** | Code Compression (`--compress`) | 🔴 High | ✅ Done |
| **v4.5.0** | Per-language tree-sitter extras | 🟡 Medium | ✅ Done |
| **v4.5.1** | Bug fix & robustness (8 bugs, 28 tests) | 🔴 Critical | ✅ Done |
| **v4.6.0** | Compression edge cases & stability | 🔴 High | 📋 Planned |
| **v4.6.0** | 🔒 Secret Scanning (`--scan-secrets`) | 🔴 Critical | 📋 Planned |
| **v4.6.0** | Configuration hierarchy & validation | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Project Profiles (`--profile`) | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Dependency Summary | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Token Budgeting (`--max-tokens`) | 🟡 Medium | 📋 Planned |
| **v5.0.0** | Import Graph (Mermaid) | 🟡 Medium | 📋 Planned |
| **v5.x** | Claude Skill (MCP) | 🟠 High | 💡 Concept |
| **v5.x** | Web UI (Viewer & Chat) | 🟠 High | 💡 Concept |
| **v5.x** | Watch Mode (`--watch`) | 🟠 Medium | 💡 Concept |

---

## 🎯 Vision: The "Semantic Zip" for AI

Code Assembler Pro aims to be more than a concatenator; it is a **Semantic Zip** format.

| Feature | Standard `.zip` | Code Assembler `.md` |
|---|---|---|
| **Human Readable** | ❌ Binary | ✅ Native Markdown |
| **AI Optimized** | ❌ Opaque | ✅ Structured Context |
| **Metadata** | Names/Sizes | Architecture, Stats, Manifest |
| **Compression** | Binary deflate | ✅ Semantic skeleton (`--compress`) |
| **Secret Safety** | ❌ None | ✅ Scanning (planned v4.6) |
| **Workflow** | One-way | ✅ Bidirectional (`--rebuild`) |

### The Full Cycle
```
Code ↔ [code-assembler] ↔ Markdown ↔ [LLM]
```
The Markdown file becomes the **universal exchange format** between developers and AI — compressed for token efficiency, secured by secret scanning, and verified by integrity manifests.

---
*Last updated: May 2026 — v4.5.1*