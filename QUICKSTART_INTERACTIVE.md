# 🚀 Interactive Mode — 5-Minute Quickstart (v4.4.0)

Get started with Code Assembler Pro's interactive wizard and the new **Round-Trip workflow** in under 5 minutes!

---

## Step 1: Launch the Wizard

```bash
code-assembler -i
```

---

## Step 2: Follow the Prompts

### 📂 Choose What to Analyze
**Choice [1]**: Current directory (`.`) is usually the best start.

### 📝 Pick Your File Types
**Choice [2]**: Python + Config + Docs (includes `.py`, `.md`, `.toml`, `.yaml`, and now `.j2`).
**Choice [8]**: Custom — to include specific files like `Dockerfile`, `Makefile`, or `.tf`.

### 🚫 Exclusions
**Use defaults? [Y]**: Always say **Yes** to filter out noise like `node_modules` or `.venv`.

### 💾 Name Your Output
**Default**: `codebase.md`. In v4.4, this file now automatically includes a **Hidden Metadata Manifest** for reliable project restoration.

---

## Step 3: Confirm & Run

```
[>>] Start assembly? [Y/n]: y
```

---

## 🎯 The v4.4 "Round-Trip" Workflow

Once your `codebase.md` is generated, here is how to use the new pro features:

### 1. Copy to AI (Instant)
Instead of manual copy-pasting, use the built-in clipboard flag:
```bash
code-assembler . --ext py --clip
```
*Then simply paste (`Ctrl+V`) into Claude or ChatGPT.*

### 2. Update with Delta (Token Saver)
When you modify your code, don't resend the whole project. Send only the changes:
```bash
code-assembler . --ext py --since codebase.md --clip
```

### 3. Apply AI Changes (Rebuild)
If the AI provides a refactored version of your project in Markdown, save it as `refactor.md` and restore it instantly:
```bash
code-assembler --rebuild refactor.md --output-dir ./restored_project
```

---

## 💡 What You Get

```
codebase.md (LLM-Ready Context)
├── 📋 Header (timestamp, stats, TOC)
├── 🏛 Architecture Analysis & Patterns
├── 📊 Statistics Table
├── 📄 Full Source Code (with enhanced syntax highlighting)
└── 🔒 Hidden Metadata Manifest (for Rebuild & Delta)
```

---

## 🔥 Pro Tips

1. **Clipboard Shortcut**: Use `-k` as a shortcut for `--clip`.
2. **Jinja2 Support**: Templates (`.j2`, `.jinja`) are now natively recognized for better AI understanding.
3. **Check Token Count**: Look at the **Estimated Tokens** in the stats to ensure you stay within your LLM's context window (e.g., 200k for Claude 3.5).
4. **Smart Truncation**: If your project is huge, enable truncation in "Advanced Options" to keep only the first 500 lines of large files.

---

## ❓ Common Questions

**Q: How do I get my code back from the Markdown file?**
A: Use the `--rebuild` command. It uses the hidden JSON metadata to recreate your exact folder structure.

**Q: Does the clipboard feature work on Linux?**
A: Yes, but ensure you have `xclip` or `xsel` installed. It works natively on Windows and macOS.

**Q: Can I skip the wizard next time?**
A: Yes! Save your config at the end of the wizard and use: `code-assembler --config your_config.json`

---

**Happy assembling!** 🚀