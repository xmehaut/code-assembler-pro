# 🎬 Interactive Mode - Visual Demo

This document shows a complete interactive wizard session from start to finish.

---

## 📺 Complete Session Recording

```
$ code-assembler --interactive

══════════════════════════════════════════════════════════════════════
🚀  Code Assembler Pro - Interactive Mode
══════════════════════════════════════════════════════════════════════

Welcome! This wizard will help you configure your codebase assembly.
Press Ctrl+C at any time to cancel.


🎯 Step 1: Select Paths to Analyze
──────────────────────────────────────────────────────────────────────

You can analyze:
  1. Current directory (.)
  2. Specific directory/directories
  3. Specific files

Your choice [1-3]: 2

Enter directory paths (one per line, empty line to finish):
  Path: ./src
  ✅ Added: ./src
  Path: ./docs
  ✅ Added: ./docs
  Path: 


🎯 Step 2: Select File Extensions
──────────────────────────────────────────────────────────────────────

Common presets:
  1. Python projects (.py)
  2. Python + Config + Docs (.py, .md, .toml, .yaml)
  3. JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
  4. Rust projects (.rs, .toml)
  5. Go projects (.go, .mod)
  6. Java projects (.java)
  7. C/C++ projects (.c, .cpp, .h, .hpp)
  8. Custom selection

Your choice [1-8]: 2
✅ Selected: Python + Config + Docs


🎯 Step 3: Configure Exclusions
──────────────────────────────────────────────────────────────────────

Default exclusions:
  __pycache__, .pyc, .pyo, .pyd, .so, .dll, .dylib, .egg-info, .eggs, dist

Use default exclusions? [Y/n]: y

Add custom exclusion patterns? [y/N]: y

Enter patterns (one per line, empty line to finish):
Examples: tests/, *.log, secret.py, temp_*
  Pattern: experiments/
  ✅ Added: experiments/
  Pattern: *.backup
  ✅ Added: *.backup
  Pattern: 


🎯 Step 4: Output Configuration
──────────────────────────────────────────────────────────────────────

Output filename [default: codebase.md]: project_context.md


🎯 Step 5: Advanced Options
──────────────────────────────────────────────────────────────────────

Configure advanced options? [y/N]: y

  Recursively traverse subdirectories? [Y/n]: y
  Automatically include README files? [Y/n]: y

  File size handling:
    Maximum file size (MB) [default: 10.0]: 5.0
    Truncate large files instead of skipping? [Y/n]: y
      Keep first N lines when truncating [default: 500]: 300


🎯 Configuration Summary
──────────────────────────────────────────────────────────────────────

📂 Paths: ./src, ./docs
📝 Extensions: .py, .md, .toml, .yaml
💾 Output: project_context.md
🔧 Recursive: True
📖 Include READMEs: True
📏 Max file size: 5.0 MB
✂️  Truncate large files: True
   Keep first 300 lines

🚫 Exclusions: 13 patterns
   - __pycache__
   - .pyc
   - .git
   - .venv
   - node_modules
   ... and 8 more

🚀 Start assembly? [Y/n]: y

💾 Save this configuration for future use? [y/N]: y
Configuration filename [default: assembler_config.json]: my_project_config.json
✅ Configuration saved to: my_project_config.json
   Reuse it with: code-assembler --config my_project_config.json

🚀 Starting assembly...

📂 Processing: ./src

  📁 code_assembler
  ℹ️  README found: README.md
  ✅ __init__.py (14 lines)
  ✅ config.py (136 lines)
  ✅ constants.py (201 lines)
  ✅ core.py (278 lines)
  ✅ file_io.py (83 lines)
  ✅ formatters.py (136 lines)
  ✅ utils.py (110 lines)
  ✅ analyzers.py (152 lines)
  ✅ cli.py (141 lines)
  ✅ interactive.py (425 lines)

📂 Processing: ./docs

  ✅ ARCHITECTURE.md (89 lines)
  ✅ API.md (124 lines)

✅ Assembly completed!

📊 Summary:
   📄 Files: 12
   📏 Lines: 1,889
   💾 Size: 67.3KB
   🎯 Tokens: ~16,825

💾 Saved: project_context.md

```

---

## 🎨 Key Features Demonstrated

### 1. **Smart Path Selection**
- Multiple directories (`./src`, `./docs`)
- Validation of existing paths
- Clear feedback on each addition

### 2. **Extension Presets**
- One-click selection for common project types
- Preset #2 chosen: Python + Config + Docs
- Includes: `.py`, `.md`, `.toml`, `.yaml`

### 3. **Flexible Exclusions**
- Default patterns automatically applied
- Custom additions: `experiments/`, `*.backup`
- Clear count in summary (13 patterns total)

### 4. **Advanced Configuration**
- Custom file size limit (5 MB instead of 10 MB)
- Truncation enabled with 300-line limit
- All options clearly explained

### 5. **Configuration Saving**
- Saved as `my_project_config.json`
- Clear instructions for reuse
- Reusable for future assemblies

### 6. **Real-time Progress**
- Folder-by-folder breakdown
- README detection notifications
- Per-file success indicators
- Final statistics summary

---

## 📋 Generated Configuration File

The wizard created this `my_project_config.json`:

```json
{
  "paths": [
    "./src",
    "./docs"
  ],
  "extensions": [
    ".py",
    ".md",
    ".toml",
    ".yaml"
  ],
  "exclude_patterns": [
    "__pycache__",
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".dylib",
    ".egg-info",
    ".eggs",
    "dist",
    "build",
    ".git",
    ".venv",
    "node_modules",
    "experiments/",
    "*.backup"
  ],
  "output": "project_context.md",
  "recursive": true,
  "include_readmes": true,
  "max_file_size_mb": 5.0,
  "truncate_large_files": true,
  "truncation_limit_lines": 300
}
```

**Reuse it:**
```bash
code-assembler --config my_project_config.json
```

---

## 🔁 Variations

### Quick Start (All Defaults)

```
Your choice [1-3]: 1
Your choice [1-8]: 1
Use default exclusions? [Y/n]: 
Add custom exclusion patterns? [y/N]: 
Output filename [default: codebase.md]: 
Configure advanced options? [y/N]: 
🚀 Start assembly? [Y/n]: 
💾 Save this configuration for future use? [y/N]: 
```

Just 7 Enter presses! ⚡

### Minimal Input (Current Dir + Python)

```
$ code-assembler -i
[Step 1] Your choice: 1         # Current directory
[Step 2] Your choice: 1         # Python only
[Step 3] Use defaults: <Enter>  # Yes to defaults
[Step 3] Custom patterns: <Enter> # No custom
[Step 4] Filename: <Enter>      # Use default
[Step 5] Advanced: <Enter>      # Use defaults
[Confirm] Start: <Enter>        # Yes, start
[Save] Config: <Enter>          # Don't save

Done! → codebase.md created
```

---

## 💡 Tips from the Demo

1. **Start with Presets** - Preset #2 (Python + Config) covers 80% of Python projects
2. **Always Use Default Exclusions** - They filter out build artifacts and dependencies
3. **Add Custom Exclusions Sparingly** - Only add project-specific patterns
4. **Save Configurations** - Reuse them for regular project updates
5. **Enable Truncation** - Keeps token count manageable for large codebases

---

## 🎓 Next Steps

Try it yourself:
```bash
code-assembler --interactive
```

Or run the demo script:
```bash
python examples/interactive_demo.py
```

---

**Interactive Mode** — *Configuration in under 60 seconds.* ⚡