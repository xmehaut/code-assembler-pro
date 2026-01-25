# 🏛️ Code Assembler Pro

> **Turn your codebase into structured, LLM-ready context with one command.**

![Version](https://img.shields.io/badge/version-4.1.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Code Assembler Pro** is a high-grade engineering utility designed to bridge the gap between your source code and Large Language Models (Claude 3.5, GPT-4o, Gemini 1.5). 

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
- **🔌 Dual Interface:** Use it as a powerful CLI tool or integrate it as a Python library.
- **📝 Multi-Language Support:** Syntax highlighting for 50+ extensions (.py, .rs, .ts, .go, .toml, etc.).
- **ℹ️ README Integration:** Automatically injects local READMEs into the flow to provide folder-level context to the AI.

---

## 🚀 Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/yourusername/code-assembler-pro.git
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

### 2. Targeted Usage
Exclude tests, target a specific source folder, and define a custom output:

```bash
code-assembler ./src \
  --ext py js ts \
  --exclude tests legacy \
  --output project_context.md
```

---

## ⚙️ Advanced Configuration (JSON)

For complex projects, use a JSON configuration file (`assembler_config.json`) for full control:

```json
{
  "paths": ["./src", "./docs"],
  "extensions": [".py", ".ts", ".tsx", ".sql"],
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

### 📖 Configuration Options Reference

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| **`paths`** | `List` | Root directories or files to analyze. | **Required** |
| **`extensions`** | `List` | File extensions to include (e.g., `[".py", ".js"]`). | **Required** |
| **`output`** | `str` | Name of the generated Markdown file. | `"codebase.md"` |
| **`exclude_patterns`** | `List` | Patterns to ignore (e.g., `"tests"`, `"build/"`). | `[]` |
| **`recursive`** | `bool` | Whether to traverse subdirectories. | `true` |
| **`include_readmes`** | `bool` | Automatically include `README.md` for folder context. | `true` |
| **`max_file_size_mb`** | `float` | Size limit before a file is truncated or skipped. | `10.0` |
| **`truncate_large_files`** | `bool` | **(v4.1)** If true, cuts large files instead of skipping them. | `true` |
| **`truncation_limit_lines`** | `int` | **(v4.1)** Number of lines to keep when truncating. | `500` |

---

## 📦 Python Library Usage

Integrate the assembler directly into your automation scripts or CI/CD pipelines:

```python
from code_assembler import assemble_codebase

# Configure and execute
markdown_content = assemble_codebase(
    paths=["./src"],
    extensions=[".py"],
    output="ai_docs.md",
    truncate_large_files=True,
    truncation_limit_lines=200,
    show_progress=True
)

print(f"Generated context: {len(markdown_content)} characters.")
```

---

## 🧙‍♂️ Interactive Mode (New!)

**Don't want to remember CLI arguments?** Use the interactive wizard!

```bash
code-assembler --interactive
# or
code-assembler -i
```

The wizard will guide you through:
1. 📂 **Path selection** - Choose directories or specific files
2. 📝 **Extension presets** - Python, JS/TS, Rust, Go, Java, C/C++, or custom
3. 🚫 **Smart exclusions** - Use defaults or add custom patterns
4. 💾 **Output config** - Name your file, auto-detect conflicts
5. ⚙️ **Advanced options** - Truncation, recursion, README inclusion

**Example session:**
```
🚀 Code Assembler Pro - Interactive Mode
═════════════════════════════════════════════════════

🎯 Step 1: Select Paths to Analyze
──────────────────────────────────────────────────────
You can analyze:
  1. Current directory (.)
  2. Specific directory/directories
  3. Specific files

Your choice [1-3]: 1
✅ Selected: current directory

🎯 Step 2: Select File Extensions
──────────────────────────────────────────────────────
Common presets:
  1. Python projects (.py)
  2. Python + Config + Docs (.py, .md, .toml, .yaml)
  3. JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
  ...

Your choice [1-8]: 2
✅ Selected: Python + Config + Docs

... [wizard continues]

🎯 Configuration Summary
──────────────────────────────────────────────────────
📂 Paths: .
📝 Extensions: .py, .md, .toml, .yaml
💾 Output: codebase.md
🔧 Recursive: True
✂️  Truncate large files: True (keep first 500 lines)

🚀 Start assembly? [Y/n]: y

💾 Save this configuration for future use? [y/N]: y
✅ Configuration saved to: assembler_config.json
   Reuse it with: code-assembler --config assembler_config.json
```

👉 **[Full Interactive Mode Guide](INTERACTIVE_MODE.md)**

---

## 💡 Recommended Use Cases

### 1. Onboarding & Audit
> *"Analyze this codebase and summarize the architecture, then list potential technical debt."*
👉 Provide the generated `codebase.md` to Claude/GPT-4.

### 2. Massive Refactoring
> *"I want to migrate this module from `requests` to `httpx`. Here is the relevant code. Propose a migration plan."*
👉 Target specific folders to reduce noise and stay within token limits.

### 3. Complex Debugging
> *"I have a circular import error between these three files. Find the root cause and fix it."*
👉 The tool preserves import structures, making it easy for the AI to trace dependencies.

---

## 🤝 Contributing

Contributions are welcome! 
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Code Assembler Pro** — *Give your AI the context it deserves.*