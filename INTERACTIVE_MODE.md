# 🧙‍♂️ Interactive Mode Guide

**Code Assembler Pro** includes a powerful interactive wizard that guides you through the configuration process with smart defaults and helpful prompts.

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

```
You can analyze:
  1. Current directory (.)
  2. Specific directory/directories
  3. Specific files

Your choice [1-3]:
```

**Examples:**
- **Option 1:** Analyze everything in the current directory
- **Option 2:** Enter paths like `./src`, `./tests`, `./docs`
- **Option 3:** Specific files like `main.py`, `config.json`

---

### Step 2: 📝 Select Extensions

Choose file types via presets or custom selection:

```
Common presets:
  1. Python projects (.py)
  2. Python + Config + Docs (.py, .md, .toml, .yaml)
  3. JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
  4. Rust projects (.rs, .toml)
  5. Go projects (.go, .mod)
  6. Java projects (.java)
  7. C/C++ projects (.c, .cpp, .h, .hpp)
  8. Custom selection

Your choice [1-8]:
```

**Custom selection example:**
```
Extensions: .py .js .md .yaml Dockerfile
```

> **Tip (v4.3):** You can include exact filenames like `Dockerfile`, `Makefile`, `.env` alongside extensions. They will be matched by exact name.

---

### Step 3: 🚫 Configure Exclusions

Manage what to exclude:

```
Default exclusions:
  __pycache__, .pyc, .git, .venv, node_modules, ...

Use default exclusions? [Y/n]: y
Add custom exclusion patterns? [y/N]: y

Enter patterns (one per line, empty line to finish):
Examples: tests/, *.log, secret.py, temp_*
  Pattern: tests/
  [OK] Added: tests/
  Pattern: *.log
  [OK] Added: *.log
  Pattern:
```

> **Tip:** Use `code-assembler --show-excludes` to see the full list of default exclusions.

---

### Step 4: 💾 Output Configuration

Choose output filename:

```
Output filename [default: codebase.md]: my_project.md
```

**Smart features:**
- Auto-adds `.md` extension if missing
- Detects existing files and asks to overwrite
- Suggests alternative names if you decline overwrite

---

### Step 5: ⚙️ Advanced Options

Fine-tune the assembly:

```
Configure advanced options? [y/N]: y

  Recursively traverse subdirectories? [Y/n]: y
  Automatically include README files? [Y/n]: y

  File size handling:
    Maximum file size (MB) [default: 10.0]: 5.0
    Truncate large files instead of skipping? [Y/n]: y
      Keep first N lines when truncating [default: 500]: 300
```

---

## 🎯 Configuration Summary

Before executing, the wizard shows a complete summary:

```
[*] Configuration Summary
----------------------------------------------------------------------

[DIR] Paths: ./src, ./docs
[FILE] Extensions: .py, .md, .toml
[S] Output: my_project.md
[R] Recursive: True
[B] Include READMEs: True
[?] Max file size: 5.0 MB
[!] Truncate large files: True
   Keep first 300 lines

[X] Exclusions: 15 patterns
   - __pycache__
   - .git
   - .venv
   - tests/
   - *.log
   ... and 10 more

[>>] Start assembly? [Y/n]:
```

---

## 💾 Save Configuration

After review, you can save the configuration for future use:

```
[S] Save this configuration for future use? [y/N]: y
Configuration filename [default: assembler_config.json]: my_config.json
[OK] Configuration saved to: my_config.json
   Reuse it with: code-assembler --config my_config.json
```

This creates a reusable JSON file:

```json
{
  "paths": ["./src", "./docs"],
  "extensions": [".py", ".md", ".toml"],
  "exclude_patterns": ["__pycache__", ".git", "tests/"],
  "output": "my_project.md",
  "recursive": true,
  "include_readmes": true,
  "max_file_size_mb": 5.0,
  "truncate_large_files": true,
  "truncation_limit_lines": 300
}
```

> **New in v4.3:** You can also save CLI arguments directly with `--save-config`:
> ```bash
> code-assembler . --ext py md --exclude tests --save-config my_config.json
> ```

---

## ⌨️ Keyboard Shortcuts

- **Enter**: Accept default value
- **Ctrl+C**: Cancel wizard at any time
- **Ctrl+D**: End list input (paths, patterns)

---

## 🎓 Tips & Best Practices

### 1. Start with Presets
Use extension presets (Step 2) for common project types. They include sensible defaults.

### 2. Use Default Exclusions
Always keep default exclusions enabled unless you have a specific reason not to. They filter out build artifacts, dependencies, version control, and IDE files. Use `code-assembler --show-excludes` to see the full list.

### 3. Include Infrastructure Files
For DevOps projects, use custom selection and add exact filenames:
```
Extensions: .py .yml .sh Dockerfile Makefile .env.j2
```

### 4. Test with Small Projects First
Run the wizard on a small project to understand the output before tackling large codebases.

### 5. Save Configurations
For projects you analyze regularly, save the configuration to skip the wizard in the future:
```bash
code-assembler --config my_saved_config.json
```

### 6. Truncation for Large Codebases
For projects with many large files:
- Enable truncation (default: Yes)
- Set a reasonable line limit (300-500 lines)
- This keeps imports and key code while staying under token limits

---

## 🔧 Advanced: Programmatic Customization

You can extend the wizard with custom logic:

```python
from code_assembler.interactive import InteractiveWizard

class CustomWizard(InteractiveWizard):
    def _select_extensions(self):
        """Override to add project-specific presets."""
        # Add your custom logic here
        return super()._select_extensions()

wizard = CustomWizard()
wizard.run()
```

---

## 🐛 Troubleshooting

### Wizard doesn't start
```bash
# Make sure you're using the right flag
code-assembler --interactive
# NOT: code-assembler interactive
```

### Configuration not saving
Check write permissions in the current directory:
```bash
ls -la
# Ensure you can write to the current folder
```

### Cancelled by accident
No problem! Just run `code-assembler -i` again. The wizard has no side effects until you confirm the final step.

### Emoji not displaying (Windows)
On legacy PowerShell or cmd.exe, emoji are replaced with ASCII markers like `[OK]`, `[>>]`, `[DIR]`. This is normal. For full emoji support, use [Windows Terminal](https://aka.ms/terminal).

---

## 📚 Next Steps

- Try the [basic usage example](examples/interactive_demo.py)
- Read the [main README](README.md) for CLI and API usage
- Check out [advanced examples](examples/advanced_config.py)

---

**Interactive Mode** — *Configuration made simple.* ✨
