# 🚀 Build & Release Guide — Code Assembler Pro

Step-by-step guide to developing, testing, and publishing a new version of the package.

`X.Y.Z` below stands for whatever version you're releasing — this guide is
kept version-agnostic on purpose. Earlier revisions hardcoded a specific
version number throughout (`4.5.2`, then later ones), and every one of them
went stale the moment the next release shipped. Don't reintroduce that: if
you're tempted to write a real version number in this file, write `X.Y.Z`
instead.

---

## Prerequisites

```bash
pip install build twine pytest
```

Required accounts:
- [PyPI](https://pypi.org/manage/account/) — Production publication
- [TestPyPI](https://test.pypi.org/manage/account/) — Test publication

Configuration file `~/.pypirc` (Windows: `C:\Users\<user>\.pypirc`):
```ini
[testpypi]
  username = __token__
  password = pypi-xxxxxxx   # TestPyPI Token

[pypi]
  username = __token__
  password = pypi-xxxxxxx   # Production PyPI Token
```

---

## Step 1 — Development Installation

```bash
pip install -e .
```

Installs the package in **editable** mode: changes made to the source code in `src/` are immediately active without reinstallation.

**To test compression with non-Python languages:**
```bash
# Install with extras during development
pip install -e ".[compress-web]"       # JS + TS
pip install -e ".[compress-systems]"   # Rust, Go, C, C++
pip install -e ".[compress-all]"       # Everything
```

**Verifications:**
```bash
code-assembler --version          # Should display X.Y.Z
code-assembler --show-excludes    # Test a quick command
code-assembler src/ --ext py --compress --output test_compress.md   # Test compression
```

---

## Step 2 — Run the Test Suite

```bash
pytest tests/ -v
```

**All tests must pass before publishing.** Don't rely on a specific test
count in this guide — it grows with every feature and any number written
here would be stale within a release or two. Read pytest's own summary
line instead:

```
===== N passed, 1 skipped =====
```

The one skip is **expected**: it corresponds to a tree-sitter test that
only runs when the optional tree-sitter packages are installed. Do not try
to "fix" it or make it mandatory — see `AGENTS.md` if you're unsure why.

> **Rule:** Never publish if a single test fails (the one expected skip is fine).

---

## Step 3 — Update Version Number

In `pyproject.toml`:
```toml
[project]
version = "X.Y.Z"
```

Also check `src/code_assembler/constants.py`'s `__version__` fallback
string (used only in dev mode, when the package isn't properly
pip-installed and `importlib.metadata` has nothing to read) — keep it in
sync so it doesn't silently drift from `pyproject.toml`.

Verify that `code-assembler --version` returns the correct version.

---

## Step 4 — Build the Package

```bash
python -m build
```

This generates two files in `dist/`:
```
dist/
├── code_assembler_pro-X.Y.Z-py3-none-any.whl
└── code_assembler_pro-X.Y.Z.tar.gz
```

**Verify that Jinja2 templates are included:**
```bash
# Linux/macOS
unzip -l dist/*.whl | grep j2

# Windows PowerShell
Get-ChildItem dist/*.whl | ForEach-Object { tar -tf $_.FullName } | Select-String "j2"
```

The `*.j2` files **must** appear in the list (otherwise the package will
crash at runtime). This check matters most exactly when you've just added a
*new* template file — `package-data` in `pyproject.toml` uses a glob
(`templates/*.j2`, `templates/components/*.j2`), so a new file in either of
those two directories is picked up automatically, but a template added
somewhere else wouldn't be — that's the failure mode this step catches.

---

## Step 5 — Publish to TestPyPI

```bash
twine upload --repository testpypi dist/code_assembler_pro-X.Y.Z*
```

**Test the standard installation:**
```bash
mkdir test_install && cd test_install
python -m venv venv && .\venv\Scripts\activate

pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            code-assembler-pro==X.Y.Z

code-assembler --version
code-assembler --help
```

**Test compression extras:**
```bash
# Install with web compression support
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            "code-assembler-pro[compress-web]==X.Y.Z"

# Verify Python compression (no extra needed)
code-assembler src/ --ext py --compress --output skeleton.md
cat skeleton.md   # Check that bodies are replaced with '...'

# Verify JS compression (requires compress-web extra)
code-assembler src/ --ext js --compress --output skeleton_js.md
```

**Test the multi-module ("modules") config path**, since it's easy to
forget it isn't exercised by any of the checks above:
```bash
cat > modules_smoke_test.json << 'EOF'
{
  "extensions": [".py"],
  "output": "smoke.md",
  "modules": {
    "a": { "paths": ["src"] }
  }
}
EOF
code-assembler --config modules_smoke_test.json
head -15 smoke_a.md   # frontmatter should show module: a, siblings: []
```

---

## Step 6 — Publish to PyPI (Production)

Once TestPyPI validation is successful:

```bash
twine upload dist/code_assembler_pro-X.Y.Z*
```

The package will be available at:
`https://pypi.org/project/code-assembler-pro/X.Y.Z/`

---

## Step 7 — Git Tag & Push

```bash
git add -A
git commit -m "feat: vX.Y.Z - <one-line summary of what shipped>"
git tag vX.Y.Z
git push origin main --tags
```

---

## Quick Checklist

```
[ ] 1. pip install -e .
[ ] 2. pytest tests/ -v                 → all pass, 1 expected skip
[ ] 3. Update version in pyproject.toml (and constants.py's fallback) to X.Y.Z
[ ] 4. python -m build                  → .whl + .tar.gz in dist/
[ ] 5. Verify j2 templates inside the .whl (especially if one was just added)
[ ] 6. twine upload --repository testpypi dist/*X.Y.Z*
[ ] 7. Test standard install + --compress on Python files (no extra needed)
[ ] 8. Test install with [compress-web] extra + --compress on .js files
[ ] 9. Test a "modules" config end to end
[ ] 10. twine upload dist/*X.Y.Z*       → Production PyPI
[ ] 11. git commit + tag + push
```

**Release gate, not optional**: run `code-assembler` on this repository's
own source tree and `--rebuild` the result before publishing. Two real,
non-synthetic bugs (a self-referential metadata match, and false
truncation-warning positives) were only ever found this way — every
synthetic test fixture in the suite missed both. See `ROADMAP.md`'s
*Release gate* section.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `403 Forbidden` on twine | Check the token in `.pypirc` (TestPyPI token ≠ PyPI token) |
| `code-assembler` not found | Run `pip install -e .` to register the entry point |
| Missing templates in .whl | Check `package-data` configuration in `pyproject.toml` |
| Rebuild fails on paths | Ensure you are testing with a file containing the Metadata Block |
| Clipboard fails on Linux | Install `xclip` or `xsel` (`sudo apt install xclip`) |
| `--compress` does nothing on .js | Install `pip install "code-assembler-pro[compress-js]"` |
| `ImportError: tree_sitter` | Run `pip install tree-sitter>=0.21` (core package required) |
| tree-sitter API error | Ensure `tree-sitter>=0.21` — v0.20 has incompatible API |
| `--since`/`--compress`/`--description` silently ignored with `--config` | Expected if the config has a `"modules"` key — CLI overrides are rejected outright in batch mode, not silently dropped; check for that error message |

---

*This guide is intentionally left without a "last updated" version stamp —
see the note at the top on why hardcoding one here goes stale by design.*