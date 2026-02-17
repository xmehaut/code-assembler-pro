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

**Verifications:**
```bash
code-assembler --version          # Should display 4.4.0
code-assembler --show-excludes    # Test a quick command
```

---

## Step 2 — Run the Test Suite

```bash
pytest tests/ -v
```

**All tests must pass before publishing.** Version 4.4.0 includes critical new tests:
```
tests/test_config.py::... PASSED
tests/test_core.py::... PASSED
tests/test_file_io.py::... PASSED
tests/test_interactive.py::... PASSED
tests/test_utils.py::... PASSED
tests/test_delta_scenario.py::... PASSED  # New in v4.4
tests/test_formats.py::... PASSED          # New in v4.4
tests/test_rebuild.py::... PASSED          # New in v4.4
tests/test_clipboard.py::... PASSED        # New in v4.4
===== 35+ passed =====
```

> **Rule:** Never publish if a single test fails.

---

## Step 3 — Update Version Number

In `pyproject.toml`:
```toml
[project]
version = "4.4.0"
```

Verify that `code-assembler --version` returns the correct version (requires `pip install -e .` if changed).

---

## Step 4 — Build the Package

```bash
python -m build
```

This generates two files in `dist/`:
```
dist/
├── code_assembler_pro-4.4.0-py3-none-any.whl    # Wheel format (fast install)
└── code_assembler_pro-4.4.0.tar.gz               # Source distribution
```

**Verify that Jinja2 templates are included:**
```bash
# Linux/macOS
unzip -l dist/*.whl | grep j2

# Windows PowerShell
tar -tf dist\code_assembler_pro-4.4.0.tar.gz | Select-String "j2"

# Liste les fichiers .j2 contenus dans le fichier .whl
Get-ChildItem dist/*.whl | ForEach-Object { tar -tf $_.FullName } | Select-String "j2"
```

The `*.j2` files **must** appear in the list (otherwise the package will crash at runtime).

---

## Step 5 — Publish to TestPyPI

```bash
twine upload --repository testpypi dist/code_assembler_pro-4.4.0*
```

**Test the installation from TestPyPI:**
```bash# Créez un dossier temporaire de test
mkdir test_install
cd test_install

# Créez un environnement virtuel propre
python -m venv venv
.\venv\Scripts\activate

# Installez depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ code-assembler-pro==4.4.0

# Testez une commande
code-assembler --version

code-assember --help
```

---

## Step 6 — Publish to PyPI (Production)

Once TestPyPI validation is successful:

```bash
twine upload dist/code_assembler_pro-4.4.0*
```

The package will be available at:
`https://pypi.org/project/code-assembler-pro/4.4.0/`

---

## Step 7 — Git Tag & Push

```bash
git add -A
git commit -m "feat: v4.4.0 - Rebuild Mode, Delta Mode, Clipboard support, and Enhanced Syntax"
git tag v4.4.0
git push origin main --tags
```

---

## Quick Checklist

```
[ ] 1. pip install -e .
[ ] 2. pytest tests/ -v              → All tests pass (including new v4.4 tests)
[ ] 3. Update version in pyproject.toml to 4.4.0
[ ] 4. python -m build               → .whl + .tar.gz in dist/
[ ] 5. Verify j2 templates inside the .whl
[ ] 6. twine upload --repository testpypi dist/*4.4.0*
[ ] 7. pip install from TestPyPI and verify --rebuild and --clip
[ ] 8. twine upload dist/*4.4.0*     → Production PyPI
[ ] 9. git commit + tag + push
```

---

## Troubleshooting

| Issue | Solution |
|----------|----------|
| `403 Forbidden` on twine | Check the token in `.pypirc` (TestPyPI token != PyPI token) |
| `code-assembler` not found | Run `pip install -e .` to register the entry point |
| Missing templates in .whl | Check `package-data` configuration in `pyproject.toml` |
| Rebuild fails on paths | Ensure you are testing with a file containing the Metadata Block |
| Clipboard fails on Linux | Install `xclip` or `xsel` (`sudo apt install xclip`) |

---

*Last updated: v4.4.0 — February 2026*