# 🗺️ Roadmap — Code Assembler Pro

Planned features and vision for future versions, ranked by their impact on the daily LLM-assisted development workflow.

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
| **v4.5.2** | Code Compression (`--compress`) | 🔴 High | ✅ Done |
| **v4.5.2** | Per-language tree-sitter extras | 🟡 Medium | ✅ Done |
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