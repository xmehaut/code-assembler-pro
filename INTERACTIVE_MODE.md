# 🧙‍♂️ Interactive Mode Guide (v4.4.0)

**Code Assembler Pro** includes a powerful interactive wizard that guides you through the configuration process with smart defaults and helpful prompts. In version 4.4.0, the wizard is optimized to prepare your codebase for the full **Round-Trip workflow** (Assemble → AI → Rebuild).

---

## 🚀 Quick Start

### Launch Interactive Mode

```bash
# From command line
code-assembler --interactive

# Or short form
code-assembler -i
```

### Programmatic Usage

```python
from code_assembler import run_interactive_mode

run_interactive_mode()
```

---

## 📋 Wizard Steps

The interactive wizard guides you through 5 main steps:

### Step 1: 📂 Select Paths
Choose what to analyze:
- **Option 1:** Current directory (`.`) — *Most common*
- **Option 2:** Specific directories (e.g., `./src`, `./lib`)
- **Option 3:** Specific files

---

### Step 2: 📝 Select Extensions
Choose file types via presets or custom selection.

**New in v4.4:** Presets now include enhanced support for **Jinja2** (`.j2`), **Terraform** (`.tf`), and automatic syntax highlighting for extensionless files like `Dockerfile` and `Makefile`.

```
Common presets:
  1. Python projects (.py)
  2. Python + Config + Docs (.py, .md, .toml, .yaml, .j2)
  3. JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
  ...
  8. Custom selection
```

---

### Step 3: 🚫 Configure Exclusions
Manage what to exclude. The wizard uses a smart exclusion engine that prevents build artifacts and sensitive data from leaking into your AI prompts.

> **Tip:** Use `code-assembler --show-excludes` to see the full list of default exclusions.

---

### Step 4: 💾 Output Configuration
Choose your output filename (default: `codebase.md`).

**v4.4 Feature:** The wizard now automatically enables the **Hidden Metadata Manifest**. This invisible JSON block is injected at the end of your file, enabling:
1.  **Reliable Rebuilds:** Reconstruct your project from the generated file.
2.  **Accurate Deltas:** Track changes precisely between versions.

---

### Step 5: ⚙️ Advanced Options
Fine-tune the assembly:
- **Recursion:** Traverse subdirectories.
- **README Inclusion:** Automatically inject local READMEs for folder-level context.
- **Smart Truncation:** Set size limits and line counts to stay within LLM token windows.

---

## 🎯 Configuration Summary

Before executing, the wizard shows a complete summary using the new v4.4 icon set:

```
[*] Configuration Summary
----------------------------------------------------------------------

[DIR] Paths: ./src, ./docs
[FILE] Extensions: .py, .md, .j2, Dockerfile
[S] Output: codebase.md
[RECYCLE] Rebuild Metadata: Enabled (Hidden JSON)
[R] Recursive: True
[B] Include READMEs: True
[?] Max file size: 10.0 MB
[!] Truncate large files: True (500 lines)

[X] Exclusions: 15 patterns
   - __pycache__
   - .git
   - .venv
   ...

[>>] Start assembly? [Y/n]:
```

---

## 💾 Save & Reuse

After the assembly, you can save your configuration to a JSON file.

**New in v4.4:** You can also save CLI arguments directly without the wizard:
```bash
code-assembler . --ext py md --save-config my_project.json
```

---

## 🎓 The v4.4 Round-Trip Workflow

Interactive mode is the starting point for the most efficient AI coding workflow:

1.  **Assemble:** Run `code-assembler -i`, select your files, and enable the metadata block.
2.  **Consult AI:** Paste the content into your LLM (use `--clip` for speed).
3.  **Iterate:** Use the generated file with `--since` to send only your latest changes.
4.  **Rebuild:** If the AI provides a refactored version of your project, save it and use:
    `code-assembler --rebuild ai_response.md --output-dir ./restored`

---

## ⌨️ Keyboard Shortcuts

- **Enter**: Accept default value.
- **Ctrl+C**: Cancel wizard at any time.
- **Ctrl+D**: End list input (paths, patterns).

---

**Interactive Mode** — *Configuration made simple, AI context made perfect.* ✨