# 🏛️ Code Assembler Pro

> **Turn your codebase into structured, LLM-ready context—and rebuild it from AI suggestions.**

![Version](https://img.shields.io/badge/version-4.4.2-blue)
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
4.  **✂️ Smart Truncation:** Intelligently truncates large files (keeping imports/classes) instead of ignoring them.
5.  **🛡️ Metadata Manifest:** Injects a hidden JSON manifest for 100% reliable project reconstruction and change tracking.

---

## ✨ Key Features

- **♻️ Rebuild Mode (`--rebuild`):** Reconstruct an entire project from a Markdown snapshot. Perfect for applying AI-generated refactors instantly.
- **⏱️ Delta Mode (`--since`):** Generate updates containing only files modified, added, or deleted since a previous assembly.
- **📋 Clipboard Integration (`--clip`):** Direct copy to system clipboard for instant ingestion into LLMs.
- **🧠 Architecture Analysis:** Detects design patterns (MVC, API, Testing) and provides file distribution stats.
- **📊 Token Metrics:** Real-time estimation of token count to stay within model context windows.
- **📝 Enhanced Syntax Highlighting:** Support for 50+ extensions including **Jinja2**, **Terraform**, and smart detection for `Dockerfile`, `Makefile`, and `.env`.
- **🖥️ Cross-Platform:** Native support for Windows, macOS, and Linux with automatic emoji/ASCII adaptation.

---

## 🚀 Installation

### From PyPI
```bash
pip install code-assembler-pro
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

---

## 📖 CLI Options Reference

| Option | Description |
|--------|-------------|
| `paths` | Files or directories to analyze |
| `--ext` / `-e` | Extensions and filenames to include (e.g., `py md Dockerfile`) |
| `--output` / `-o` | Output file name (default: `codebase.md`) |
| `--since` / `-s` | **(v4.4)** Delta Mode: Only include changes since this snapshot |
| `--rebuild` | **(v4.4)** Reconstruct project from a Markdown file |
| `--output-dir` | **(v4.4)** Target directory for reconstruction |
| `--clip` / `-k` | **(v4.4)** Copy result directly to clipboard |
| `--dry-run` | **(v4.4)** Preview rebuild without writing files |
| `--interactive` / `-i` | Launch the interactive wizard |
| `--config` / `-c` | Load a JSON configuration file |
| `--exclude` / `-x` | Patterns to exclude (added to defaults) |
| `--max-size` | Maximum file size in MB (default: 10.0) |
| `--version` | Show version and exit |

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

### Incremental Update (Delta Mode)
```python
# Only include files changed since 'previous_snapshot.md'
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

For complex projects, use a JSON configuration file:

```json
{
  "paths": ["./src", "./infra"],
  "extensions": [".py", ".ts", ".j2", "Dockerfile", ".env"],
  "exclude_patterns": ["migrations", "__pycache__", "*.test.ts"],
  "output": "project_context.md",
  "recursive": true,
  "include_readmes": true,
  "max_file_size_mb": 2.0,
  "truncate_large_files": true,
  "truncation_limit_lines": 500
}
```
Run it using: `code-assembler --config assembler_config.json`

---

## 📦 Python Library Usage

Integrate the assembler directly into your automation scripts:

```python
from code_assembler import assemble_codebase

# Configure and execute
markdown_content = assemble_codebase(
    paths=["./src"],
    extensions=[".py", "Dockerfile"],
    output="ai_docs.md",
    show_progress=True
)

print(f"Generated context: {len(markdown_content)} characters.")
```

---

## 💡 Recommended Use Cases

### 1. Massive Refactoring Loop
1. Assemble your project: `code-assembler . -e py --clip`
2. Paste into Claude: *"Refactor this project to use Pydantic v2."*
3. Save Claude's response as `refactor.md`.
4. Apply changes: `code-assembler --rebuild refactor.md --output-dir .`

### 2. Incremental Debugging
After fixing a bug, send only the delta to the AI to verify the fix without re-sending the whole codebase:
`code-assembler . -e py --since previous_snapshot.md --clip`

### 3. Infrastructure Audit
Include `Dockerfile`, `Makefile`, and `.tf` files to give the AI a full view of your deployment stack.

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