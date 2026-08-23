# 🏛️ Code Assembler Pro

> **Turn your codebase into structured, LLM-ready context—and rebuild it from AI suggestions.**

![Version](https://img.shields.io/badge/version-4.6.1-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Code Assembler Pro** is a high-grade engineering utility designed to bridge the gap between your source code and Large Language Models (Claude, GPT-4o, Gemini, DeepSeek).

It doesn't just concatenate files; it generates a **contextual technical document** optimized for LLM ingestion, and provides a **reliable rebuild engine** to reconstruct projects from AI-modified Markdown files.

---

## 🎯 Why Code Assembler Pro?

Copy-pasting raw files into a chat window leads to context loss. **Code Assembler Pro solves this by:**

1.  **🗺️ Project Mapping:** Automatically generates a clickable Table of Contents and architectural overview.
2.  **♻️ Bidirectional Workflow:** Use `--rebuild` to turn an AI's Markdown response back into a physical directory structure.
3.  **⏱️ Token Efficiency:** Use `--since` (Delta Mode) to send only modified files, saving thousands of tokens.
4.  **✂️ Smart Compression:** Use `--compress` to reduce a dependency's code to signatures + docstrings only — dramatically shrinking token count while preserving full structural context.
5.  **🛡️ Metadata Manifest:** Injects a hidden JSON manifest for 100% reliable project reconstruction and change tracking.

---

## ✨ Key Features

- **♻️ Rebuild Mode (`--rebuild`):** Reconstruct an entire project from a Markdown snapshot. Perfect for applying AI-generated refactors instantly.
- **⏱️ Delta Mode (`--since`):** Generate updates containing only files modified, added, or deleted since a previous assembly.
- **🗜️ Compression Mode (`--compress`):** Reduce source files to structural skeletons — signatures and docstrings only. Python always works out of the box; other languages use individually installed tree-sitter packages.
- **📋 Clipboard Integration (`--clip`):** Direct copy to system clipboard for instant ingestion into LLMs.
- **🧠 Architecture Analysis:** Detects design patterns (MVC, API, Testing) and provides file distribution stats.
- **📊 Token Metrics:** Real-time estimation of token count to stay within model context windows.
- **📝 Enhanced Syntax Highlighting:** Support for 50+ extensions including **Jinja2**, **Terraform**, and smart detection for `Dockerfile`, `Makefile`, and `.env`.
- **🖥️ Cross-Platform:** Native support for Windows, macOS, and Linux with automatic emoji/ASCII adaptation.

---

## 🚀 Installation

### Standard install (no compression)
```bash
pip install code-assembler-pro
```

### With compression support

Python files are **always supported** via stdlib `ast` — no extra install needed.

For other languages, install the corresponding extra:

```bash
# JavaScript + TypeScript
pip install "code-assembler-pro[compress-web]"

# Rust + Go + C + C++
pip install "code-assembler-pro[compress-systems]"

# A single language
pip install "code-assembler-pro[compress-js]"
pip install "code-assembler-pro[compress-rust]"

# Everything
pip install "code-assembler-pro[compress-all]"
```

### From source (development)
```bash
git clone https://github.com/xmehaut/code-assembler-pro.git
cd code-assembler-pro
pip install -e .
```

---

## 💻 Quick Start (CLI)

### 1. Assemble & Copy (The "One-Shot" Workflow)
Consolidate your code and copy it directly to your clipboard:
```bash
code-assembler . --ext py md --clip
```

### 2. Iterative Update (The "Token-Saver" Workflow)
Only send what changed since your last assembly:
```bash
code-assembler . --ext py --since codebase.md --clip
```

### 3. Rebuild from AI (The "Round-Trip" Workflow)
Restore a project from a Markdown file (e.g., after an AI refactor):
```bash
code-assembler --rebuild refactored_codebase.md --output-dir ./restored_project
```
The full loop: assemble → paste into your LLM → ask for changes → save the response → `--rebuild` it back into place. Every generated snapshot carries a hidden metadata manifest, so this round-trip works even weeks later.

### 4. Compress a Dependency (The "Skeleton" Workflow)
Generate a lightweight snapshot of a third-party package — full structure, minimal tokens:
```bash
# Your own code — full detail
code-assembler src/ --ext py --output my_package.md

# A dependency — signatures + docstrings only
code-assembler .venv/lib/some_dep/ --ext py --compress --output dep_skeleton.md
```

---

## 🧙 Interactive Mode

Prefer a guided setup over remembering flags? Launch the wizard — it shows its own live prompts and a full configuration summary before running, so there's nothing to memorize here:

```bash
code-assembler -i
```

Answer its questions once, then save them to skip the wizard on every future run:

```bash
code-assembler . --ext py md --save-config my_project.json
code-assembler --config my_project.json   # reruns with no prompts — see JSON config below
```

**Keyboard shortcuts:** `Enter` accepts the default value · `Ctrl+C` cancels at any point · `Ctrl+D` ends a list input (paths, patterns).

**FAQ**

- **How do I get my code back from the Markdown file?** `--rebuild` — it uses the hidden JSON metadata to recreate your exact folder structure (see workflow 3 above).
- **Does `--clip` work on Linux?** Yes, but install `xclip` or `xsel` first. Works natively on Windows and macOS.
- **Can I skip the wizard next time?** Yes — see `--save-config` above.

---

## 📖 CLI Options Reference

| Option | Description |
|--------|-------------|
| `paths` | Files or directories to analyze |
| `--ext` / `-e` | Extensions and filenames to include (e.g., `py md Dockerfile`) |
| `--output` / `-o` | Output file name (default: `codebase.md`) |
| `--since` / `-s` | Delta Mode: Only include changes since this snapshot |
| `--rebuild` | Reconstruct project from a Markdown file |
| `--output-dir` | Target directory for reconstruction |
| `--clip` / `-k` | Copy result directly to clipboard |
| `--dry-run` | Preview rebuild without writing files |
| `--compress` / `-z` | **(v4.5)** Compress to signatures + docstrings only |
| `--compress-level` | **(v4.5)** `signatures` (default) or `docstrings_only` |
| `--interactive` / `-i` | Launch the interactive wizard |
| `--config` / `-c` | Load a JSON configuration file |
| `--save-config` | Save the current CLI flags to a JSON file (no wizard needed) |
| `--exclude` / `-x` | Patterns to exclude (added to defaults) |
| `--show-excludes` | Print the full list of default exclusion patterns |
| `--no-recursive` | Disable recursion into subdirectories (default: recursive) |
| `--no-readmes` | Disable automatic README inclusion for folder context |
| `--no-default-excludes` | Disable the built-in exclusion patterns entirely |
| `--max-size` | Maximum file size in MB (default: 10.0) |
| `--version` | Show version and exit |

---

## 🗜️ Compression Mode — How It Works

`--compress` reduces each file to its structural skeleton. The goal is to give an LLM
full context about a codebase's shape and API surface without the implementation noise.

```python
# Original (full file) — ~80 tokens
def connect(host: str, port: int, timeout: float = 30.0) -> Connection:
    """Establish a TCP connection to the server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))
    return Connection(sock)

# Compressed — ~15 tokens
def connect(host: str, port: int, timeout: float = 30.0) -> Connection:
    """Establish a TCP connection to the server."""
    ...
```

**Language support:**

| Language | Requirement |
|----------|-------------|
| Python | ✅ Always available (stdlib `ast`) |
| JavaScript / JSX | `pip install "code-assembler-pro[compress-js]"` |
| TypeScript / TSX | `pip install "code-assembler-pro[compress-ts]"` |
| Rust | `pip install "code-assembler-pro[compress-rust]"` |
| Go | `pip install "code-assembler-pro[compress-go]"` |
| Java | `pip install "code-assembler-pro[compress-java]"` |
| C | `pip install "code-assembler-pro[compress-c]"` |
| C++ | `pip install "code-assembler-pro[compress-cpp]"` |

Missing parsers are reported at startup with the exact install command — other files are passed through unchanged.

---

## 🔌 Programmatic API

Code Assembler Pro can be integrated into your Python pipelines (CI/CD, custom AI agents).

### Basic Assembly
```python
from code_assembler import assemble_codebase

markdown = assemble_codebase(
    paths=["./src"],
    extensions=[".py", ".js"],
    output="context.md"
)
```

### Compressed snapshot of a dependency
```python
markdown = assemble_codebase(
    paths=[".venv/lib/requests"],
    extensions=[".py"],
    output="requests_skeleton.md",
    compress=True,
)
```

### Incremental Update (Delta Mode)
```python
assemble_codebase(
    paths=["./src"],
    extensions=[".py"],
    since="previous_snapshot.md",
    output="delta_update.md"
)
```

### Project Reconstruction
```python
from code_assembler.rebuilder import CodebaseRebuilder

rebuilder = CodebaseRebuilder("ai_response.md", "./new_src")
rebuilder.rebuild()
```

---

## ⚙️ Advanced Configuration (JSON)

For complex or repeated setups, save your configuration to a JSON file instead of retyping flags — either by hand from the template below, or generated for you by the interactive wizard's `--save-config`.

```json
{
  "paths": ["./src"],
  "extensions": [".py", ".md"],
  "exclude_patterns": [],
  "output": "codebase.md",
  "recursive": true,
  "include_readmes": true,
  "use_default_excludes": true,
  "max_file_size_mb": 10.0,
  "truncate_large_files": true,
  "truncation_limit_lines": 500,
  "show_progress": true,
  "compress": false,
  "compress_level": "signatures"
}
```

Only `paths` and `extensions` are required — every other key falls back to the default shown above if omitted.

| Key | Default | Notes |
|---|---|---|
| `paths` | *(required)* | At least one path |
| `extensions` | *(required)* | At least one; exact filenames like `Dockerfile`/`Makefile` are auto-detected (capitalized, no leading dot) |
| `exclude_patterns` | `[]` | Added to the defaults, not a replacement — see `use_default_excludes` |
| `output` | `"codebase.md"` | ⚠️ the JSON key is `output`, not `output_file` (the internal config field's name) |
| `recursive` | `true` | |
| `include_readmes` | `true` | |
| `use_default_excludes` | `true` | `false` disables the built-in `__pycache__`, `.venv`, etc. patterns (run `--show-excludes` to see the full list) |
| `max_file_size_mb` | `10.0` | |
| `truncate_large_files` | `true` | |
| `truncation_limit_lines` | `500` | |
| `show_progress` | `true` | |
| `compress` | `false` | |
| `compress_level` | `"signatures"` | Only other value currently accepted is `"docstrings_only"`, reserved for a future stricter mode |

Run it with:
```bash
code-assembler --config assembler_config.json
```

**CLI flags override the JSON file, not the other way around** — any flag passed alongside `--config` wins over the matching JSON key:
```bash
code-assembler --config base_config.json --compress --since last_snapshot.md
```
Handy for keeping one stable base config and only varying what changes per run. Note that `--since` is never a JSON key itself — delta mode always comes from this flag, config file or not.

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch.
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Code Assembler Pro** — *Give your AI the context it deserves, then take the code back.* 🚀