# 🚀 Build & Release Guide — Code Assembler Pro

Step-by-step guide to developing, testing, and publishing a new version of the package.

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
code-assembler --version          # Should display 4.5.0
code-assembler --show-excludes    # Test a quick command
code-assembler src/ --ext py --compress --output test_compress.md   # Test compression
```

---

## Step 2 — Run the Test Suite

```bash
pytest tests/ -v
```

**All tests must pass before publishing.** Version 4.5.0 adds compression tests:
```
tests/test_config.py::... PASSED
tests/test_core.py::... PASSED
tests/test_file_io.py::... PASSED
tests/test_interactive.py::... PASSED
tests/test_utils.py::... PASSED
tests/test_delta_scenario.py::... PASSED
tests/test_formats.py::... PASSED
tests/test_rebuild.py::... PASSED
tests/test_clipboard.py::... PASSED
tests/test_compressor.py::... PASSED   # New in v4.5
===== 54+ passed =====
```

> **Note on compression tests:** `test_missing_package_reported` is skipped if
> `tree-sitter` is not installed in the test environment. This is expected and correct.
> The test runs automatically in environments where tree-sitter is available.

> **Rule:** Never publish if a single test fails (skips are acceptable).

---

## Step 3 — Update Version Number

In `pyproject.toml`:
```toml
[project]
version = "4.5.0"
```

Verify that `code-assembler --version` returns the correct version.

---

## Step 4 — Build the Package

```bash
python -m build
```

This generates two files in `dist/`:
```
dist/
├── code_assembler_pro-4.5.0-py3-none-any.whl
└── code_assembler_pro-4.5.0.tar.gz
```

**Verify that Jinja2 templates are included:**
```bash
# Linux/macOS
unzip -l dist/*.whl | grep j2

# Windows PowerShell
Get-ChildItem dist/*.whl | ForEach-Object { tar -tf $_.FullName } | Select-String "j2"
```

The `*.j2` files **must** appear in the list (otherwise the package will crash at runtime).

---

## Step 5 — Publish to TestPyPI

```bash
twine upload --repository testpypi dist/code_assembler_pro-4.5.0*
```

**Test the standard installation:**
```bash
mkdir test_install && cd test_install
python -m venv venv && .\venv\Scripts\activate

pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            code-assembler-pro==4.5.0

code-assembler --version
code-assembler --help
```

**Test compression extras:**
```bash
# Install with web compression support
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            "code-assembler-pro[compress-web]==4.5.0"

# Verify Python compression (no extra needed)
code-assembler src/ --ext py --compress --output skeleton.md
cat skeleton.md   # Check that bodies are replaced with '...'

# Verify JS compression (requires compress-web extra)
code-assembler src/ --ext js --compress --output skeleton_js.md
```

---

## Step 6 — Publish to PyPI (Production)

Once TestPyPI validation is successful:

```bash
twine upload dist/code_assembler_pro-4.5.0*
```

The package will be available at:
`https://pypi.org/project/code-assembler-pro/4.5.0/`

---

## Step 7 — Git Tag & Push

```bash
git add -A
git commit -m "feat: v4.5.0 - Code Compression Mode (--compress) with tree-sitter per-language support"
git tag v4.5.0
git push origin main --tags
```

---

## Quick Checklist

```
[ ] 1. pip install -e .
[ ] 2. pytest tests/ -v              → All tests pass (54+ including new v4.5 compression tests)
[ ] 3. Update version in pyproject.toml to 4.5.0
[ ] 4. python -m build               → .whl + .tar.gz in dist/
[ ] 5. Verify j2 templates inside the .whl
[ ] 6. twine upload --repository testpypi dist/*4.5.0*
[ ] 7. Test standard install + test --compress on Python files (no extra needed)
[ ] 8. Test install with [compress-web] extra + test --compress on .js files
[ ] 9. twine upload dist/*4.5.0*     → Production PyPI
[ ] 10. git commit + tag + push
```

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

---

*Last updated: v4.5.0 — May 2026*