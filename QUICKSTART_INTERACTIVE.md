# 🚀 Interactive Mode — 5-Minute Quickstart

Get started with Code Assembler Pro's interactive wizard in under 5 minutes!

---

## Step 1: Launch the Wizard

```bash
code-assembler -i
```

---

## Step 2: Follow the Prompts

### 📂 Choose What to Analyze

```
Your choice [1-3]: 1
```
**Tip:** Start with option 1 (current directory) for simplicity.

---

### 📝 Pick Your File Types

```
Your choice [1-8]: 2
```
**Recommended presets:**
- **Option 1**: Pure Python projects
- **Option 2**: Python with docs/config (most common)
- **Option 3**: JavaScript/TypeScript projects
- **Option 8**: Custom — include `Dockerfile`, `.env`, etc.

---

### 🚫 Exclusions

```
Use default exclusions? [Y/n]: y
Add custom exclusion patterns? [y/N]: n
```
**Tip:** Always accept defaults unless you need something specific. Use `code-assembler --show-excludes` to see what's excluded by default.

---

### 💾 Name Your Output

```
Output filename [default: codebase.md]:
```
**Tip:** Press Enter to use the default name.

---

### ⚙️ Advanced Options

```
Configure advanced options? [y/N]: n
```
**Tip:** Skip advanced options on first run. Defaults are sensible.

---

## Step 3: Confirm & Run

```
[>>] Start assembly? [Y/n]: y
```

That's it! Your `codebase.md` is ready to share with an LLM.

---

## 💡 What You Get

```
codebase.md (Ready for Claude/GPT!)
├── 📋 Header (timestamp, stats, TOC)
├── 🏛 Architecture Analysis
├── 📊 Statistics Table
├── 💬 Recommended Prompts
└── 📄 Full Source Code (organized by folder)
```

---

## 🎯 Next Steps

### Copy to Claude/GPT
```bash
# On macOS
cat codebase.md | pbcopy

# On Linux
cat codebase.md | xclip -selection clipboard

# On Windows
type codebase.md | clip
```

Then paste into your LLM chat!

### Save Your Configuration
When prompted:
```
[S] Save this configuration for future use? [y/N]: y
```

Or save directly from the CLI:
```bash
code-assembler . --ext py md --save-config my_config.json
```

Reuse it later:
```bash
code-assembler --config my_config.json
```

---

## 🔥 Pro Tips

### 1. Start Small
Test on a small project first to understand the output format.

### 2. Use Presets
The extension presets (Step 2) are tailored for common project types.

### 3. Include Infrastructure Files
For DevOps/MLOps projects, use custom selection (option 8) and add:
```
Extensions: .py .yml .sh Dockerfile Makefile .env.j2
```

### 4. Check Token Count
Look at the **Estimated Tokens** in the stats. Most LLMs have limits:
- GPT-4o: 128,000 tokens
- Claude 3.5 / 4: 200,000 tokens
- Gemini 1.5 Pro: 1,000,000 tokens

### 5. Truncate Large Files
If your project has huge files (>1000 lines), enable truncation:
```
Truncate large files instead of skipping? [Y/n]: y
Keep first N lines when truncating [default: 500]: 300
```

This keeps imports and key definitions while reducing token usage.

### 6. See What's Excluded
```bash
code-assembler --show-excludes
```

---

## ❓ Common Questions

**Q: Can I run it on the same project multiple times?**
A: Yes! It will ask to overwrite or suggest a new filename.

**Q: What if I make a mistake during the wizard?**
A: Press `Ctrl+C` to cancel and start over. No harm done!

**Q: Can I skip the wizard next time?**
A: Yes! Save your config and use: `code-assembler --config your_config.json`

**Q: Does it work on Windows?**
A: Absolutely! The wizard is cross-platform. On legacy PowerShell, emoji are replaced with ASCII markers.

**Q: How do I include `Dockerfile` or `Makefile`?**
A: Just add them as-is: `--ext py md Dockerfile Makefile`. They're matched by exact filename.

---

## 🎓 Learn More

- **Full Guide:** [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md)
- **CLI Reference:** [README.md](README.md)
- **Examples:** [examples/](examples/)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

**Happy assembling!** 🚀
