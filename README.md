# 🏛️ Code Assembler Pro

> **Turn your codebase into structured, LLM-ready context with one command.**

![Version](https://img.shields.io/badge/version-4.3.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![PyPI version](https://badge.fury.io/py/code-assembler-pro.svg)](https://badge.fury.io/py/code-assembler-pro)


**Code Assembler Pro** is a high-grade engineering utility designed to bridge the gap between your source code and Large Language Models (Claude, GPT-4o, Gemini, DeepSeek).

It doesn't just concatenate files; it generates a **contextual technical document** optimized for LLM ingestion, preserving project structure, identifying architectural patterns, and managing token limits through intelligent truncation.

---

## 🎯 Why Code Assembler Pro?

Copy-pasting raw files into a chat window leads to context loss (who calls what? where is this file located?).

**Code Assembler Pro solves this by:**
1.  **🗺️ Project Mapping:** Automatically generates a clickable Table of Contents and architectural overview.
2.  **✂️ Smart Token Management:** Estimates token costs and **intelligently truncates** large files (keeping imports and class definitions) instead of ignoring them.
3.  **🛡️ Noise Filtering:** Automatically excludes binaries, build artifacts (`node_modules`, `venv`), and sensitive secrets.
4.  **🎨 Jinja2 Templating:** Uses a clean separation between data and presentation for perfectly formatted Markdown.

---

## ✨ Key Features

- **🧠 Architecture Analysis:** Detects design patterns (MVC, API, Testing structures) and provides file distribution stats.
- **📊 Token Metrics:** Real-time estimation of token count to stay within model limits.
- **📌 Dual Interface:** Use it as a powerful CLI tool or integrate it as a Python library.
- **📝 Multi-Language Support:** Syntax highlighting for 50+ extensions (.py, .rs, .ts, .go, .toml, etc.).
- **📄 Exact Filename Matching:** **(v4.3)** Include files like `Dockerfile`, `Makefile`, `.env` by exact name.
- **ℹ️ README Integration:** Automatically injects local READMEs into the flow to provide folder-level context to the AI.
- **🖥️ Cross-Platform:** Works on Windows (PowerShell, cmd), macOS, and Linux with automatic emoji/ASCII adaptation.

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

*Dependencies: `chardet`, `jinja2`.*

---

## 💻 Quick Start (CLI)

Once installed, the `code-assembler` command is available globally in your environment.

### 1. Basic Usage
Consolidate all Python and Markdown files in the current directory:

```bash
code-assembler . --ext py md
```

### 2. Include special files
Include `Dockerfile`, `.env`, and Jinja2 templates alongside Python:

```bash
code-assembler . --ext py md yml Dockerfile .env .env.j2 .j2
```

### 3. Targeted Usage
Exclude tests, target a specific source folder, and define a custom output:

```bash
code-assembler ./src \
  --ext py js ts \
  --exclude tests legacy \
  --output project_context.md
```

### 4. Save your CLI as a reusable config
```bash
code-assembler . --ext py md Dockerfile --exclude tests --save-config my_project.json
```
Reuse it later:
```bash
code-assembler --config my_project.json
```

### 5. Show default exclusions
```bash
code-assembler --show-excludes
```

---

## 🧙‍♂️ Interactive Mode

**Don't want to remember CLI arguments?** Use the interactive wizard!

```bash
code-assembler --interactive
# or
code-assembler -i
```

The wizard will guide you through:
1. 📂 **Path selection** — Choose directories or specific files
2. 📝 **Extension presets** — Python, JS/TS, Rust, Go, Java, C/C++, or custom
3. 🚫 **Smart exclusions** — Use defaults or add custom patterns
4. 💾 **Output config** — Name your file, auto-detect conflicts
5. ⚙️ **Advanced options** — Truncation, recursion, README inclusion

👉 **[Full Interactive Mode Guide](INTERACTIVE_MODE.md)** | **[5-Minute Quickstart](QUICKSTART_INTERACTIVE.md)**

---

## ⚙️ Advanced Configuration (JSON)

For complex projects, use a JSON configuration file for full control:

```json
{
  "paths": ["./src", "./infra"],
  "extensions": [".py", ".ts", ".tsx", ".sql", "Dockerfile", ".env.j2"],
  "exclude_patterns": [
    "migrations",
    "__pycache__",
    "*.test.ts"
  ],
  "output": "full_stack_context.md",
  "recursive": true,
  "include_readmes": true,
  "max_file_size_mb": 2.0,
  "truncate_large_files": true,
  "truncation_limit_lines": 500
}
```

Run it using:
```bash
code-assembler --config assembler_config.json
```

### 📖 CLI Options Reference

| Option | Description |
|--------|-------------|
| `paths` | Files or directories to analyze |
| `--ext` / `-e` | Extensions and filenames to include (e.g., `py md Dockerfile`) |
| `--output` / `-o` | Output file name (default: `codebase.md`) |
| `--exclude` / `-x` | Patterns to exclude (added to defaults) |
| `--config` / `-c` | Load a JSON configuration file |
| `--interactive` / `-i` | Launch the interactive wizard |
| `--save-config FILE` | **(v4.3)** Save CLI args as reusable JSON config |
| `--show-excludes` | **(v4.3)** Display default exclusion patterns |
| `--no-recursive` | Do not traverse subdirectories |
| `--no-readmes` | Do not auto-include README files |
| `--no-default-excludes` | Disable default exclusion patterns |
| `--max-size` | Maximum file size in MB (default: 10.0) |
| `--version` | Show version and exit |

### 📖 JSON Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| **`paths`** | `List` | Root directories or files to analyze. | **Required** |
| **`extensions`** | `List` | File extensions and exact filenames (e.g., `[".py", "Dockerfile"]`). | **Required** |
| **`output`** | `str` | Name of the generated Markdown file. | `"codebase.md"` |
| **`exclude_patterns`** | `List` | Patterns to ignore (e.g., `"tests"`, `"*.log"`, `"build/"`). | `[]` |
| **`recursive`** | `bool` | Whether to traverse subdirectories. | `true` |
| **`include_readmes`** | `bool` | Automatically include `README.md` for folder context. | `true` |
| **`max_file_size_mb`** | `float` | Size limit before a file is truncated or skipped. | `10.0` |
| **`truncate_large_files`** | `bool` | If true, cuts large files instead of skipping them. | `true` |
| **`truncation_limit_lines`** | `int` | Number of lines to keep when truncating. | `500` |

---

## 📦 Python Library Usage

Integrate the assembler directly into your automation scripts or CI/CD pipelines:

```python
from code_assembler import assemble_codebase

# Configure and execute
markdown_content = assemble_codebase(
    paths=["./src"],
    extensions=[".py", "Dockerfile"],
    output="ai_docs.md",
    truncate_large_files=True,
    truncation_limit_lines=200,
    show_progress=True
)

print(f"Generated context: {len(markdown_content)} characters.")
```

---

## 💡 Recommended Use Cases

### 1. Onboarding & Audit
> *"Analyze this codebase and summarize the architecture, then list potential technical debt."*

### 2. Massive Refactoring
> *"I want to migrate this module from `requests` to `httpx`. Here is the relevant code. Propose a migration plan."*

### 3. Complex Debugging
> *"I have a circular import error between these three files. Find the root cause and fix it."*

### 4. Infrastructure as Code
> *"Review my Docker + Kubernetes setup and suggest improvements."*
Include `Dockerfile`, `.yml`, `.env.j2` in your extensions.

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

### Development Setup
```bash
git clone https://github.com/xmehaut/code-assembler-pro.git
cd code-assembler-pro
pip install -e ".[dev]"
pytest tests/ -v
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Code Assembler Pro** — *Give your AI the context it deserves.*
