"""
Tests for the compression module (CodeCompressor).

Python compression via stdlib ast is always tested (no external deps).
Tree-sitter paths are tested via mocks to avoid requiring installed parsers.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.compressor import CodeCompressor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_compressor(extensions=None) -> CodeCompressor:
    """Create a CodeCompressor without loading any tree-sitter parsers."""
    extensions = extensions or [".py"]
    # Patch _load_parsers to avoid real imports during unit tests
    with patch.object(CodeCompressor, "_load_parsers"):
        c = CodeCompressor(extensions)
    return c


# ---------------------------------------------------------------------------
# Python AST compression — no external dependency needed
# ---------------------------------------------------------------------------

class TestPythonASTCompression(unittest.TestCase):

    def setUp(self):
        self.c = make_compressor([".py"])

    def _compress(self, source: str) -> str:
        return self.c._compress_python_ast(source)

    # --- Basic function ---

    def test_function_body_replaced(self):
        source = (
            "def add(a, b):\n"
            "    result = a + b\n"
            "    return result\n"
        )
        result = self._compress(source)
        self.assertIn("def add(a, b):", result)
        self.assertIn("...", result)
        self.assertNotIn("result = a + b", result)
        self.assertNotIn("return result", result)

    def test_function_signature_preserved(self):
        source = (
            "def greet(name: str, greeting: str = 'Hello') -> str:\n"
            "    return f'{greeting}, {name}!'\n"
        )
        result = self._compress(source)
        self.assertIn("def greet(name: str, greeting: str = 'Hello') -> str:", result)

    def test_docstring_preserved(self):
        source = (
            "def compute(x):\n"
            "    \"\"\"Compute the result.\"\"\"\n"
            "    return x * 2\n"
        )
        result = self._compress(source)
        self.assertIn("Compute the result.", result)
        self.assertIn("...", result)
        self.assertNotIn("x * 2", result)

    def test_function_only_docstring(self):
        """A function whose body IS only a docstring should not add '...'."""
        source = (
            "def documented():\n"
            "    \"\"\"This function is abstract.\"\"\"\n"
        )
        result = self._compress(source)
        self.assertIn("This function is abstract.", result)
        # No extra ... needed — body is only the docstring
        lines = [l.strip() for l in result.splitlines() if l.strip()]
        self.assertNotIn("...", lines)

    def test_async_function(self):
        source = (
            "async def fetch(url: str):\n"
            "    response = await client.get(url)\n"
            "    return response.json()\n"
        )
        result = self._compress(source)
        self.assertIn("async def fetch(url: str):", result)
        self.assertIn("...", result)
        self.assertNotIn("response = await", result)

    # --- Class handling ---

    def test_class_methods_compressed(self):
        source = (
            "class Calculator:\n"
            "    def add(self, a, b):\n"
            "        return a + b\n"
            "    def sub(self, a, b):\n"
            "        return a - b\n"
        )
        result = self._compress(source)
        self.assertIn("class Calculator:", result)
        self.assertIn("def add(self, a, b):", result)
        self.assertIn("def sub(self, a, b):", result)
        self.assertNotIn("return a + b", result)
        self.assertNotIn("return a - b", result)

    def test_class_docstring_preserved(self):
        source = (
            "class MyClass:\n"
            "    \"\"\"Class-level docstring.\"\"\"\n"
            "    def method(self):\n"
            "        pass\n"
        )
        result = self._compress(source)
        self.assertIn("Class-level docstring.", result)

    def test_class_method_docstring_preserved(self):
        source = (
            "class Foo:\n"
            "    def bar(self):\n"
            "        \"\"\"Method doc.\"\"\"\n"
            "        x = 1\n"
            "        return x\n"
        )
        result = self._compress(source)
        self.assertIn("Method doc.", result)
        self.assertNotIn("x = 1", result)

    # --- Top-level code ---

    def test_imports_preserved(self):
        source = (
            "import os\n"
            "from pathlib import Path\n"
            "\n"
            "def foo():\n"
            "    return 42\n"
        )
        result = self._compress(source)
        self.assertIn("import os", result)
        self.assertIn("from pathlib import Path", result)

    def test_module_constants_preserved(self):
        source = (
            "VERSION = '1.0.0'\n"
            "DEBUG = False\n"
            "\n"
            "def main():\n"
            "    print(VERSION)\n"
        )
        result = self._compress(source)
        self.assertIn("VERSION = '1.0.0'", result)
        self.assertIn("DEBUG = False", result)
        self.assertNotIn("print(VERSION)", result)

    # --- Edge cases ---

    def test_syntax_error_returns_original(self):
        """Invalid Python should be returned as-is without raising."""
        source = "def broken(\n    missing closing\n"
        result = self._compress(source)
        self.assertEqual(result, source)

    def test_empty_source(self):
        result = self._compress("")
        self.assertEqual(result, "")

    def test_indentation_correct(self):
        """The '...' placeholder must be at the right indentation level."""
        source = (
            "class Outer:\n"
            "    def method(self):\n"
            "        x = 1\n"
            "        return x\n"
        )
        result = self._compress(source)
        # '...' should be indented 8 spaces (class 0 + method 4 + body 4)
        self.assertIn("        ...", result)


# ---------------------------------------------------------------------------
# compress() dispatcher
# ---------------------------------------------------------------------------

class TestCompressDispatcher(unittest.TestCase):

    def setUp(self):
        self.c = make_compressor([".py", ".js"])

    def test_python_file_dispatched_to_ast(self):
        source = "def foo():\n    return 1\n"
        result = self.c.compress(source, "script.py")
        self.assertIn("def foo():", result)
        self.assertIn("...", result)

    def test_unknown_extension_returns_original(self):
        source = "some content"
        result = self.c.compress(source, "file.xyz")
        self.assertEqual(result, source)

    def test_no_parser_for_lang_returns_original(self):
        """JS file without a loaded parser should pass through unchanged."""
        source = "function foo() { return 1; }"
        # No parsers loaded (mocked _load_parsers), so JS falls through
        result = self.c.compress(source, "app.js")
        self.assertEqual(result, source)

    def test_treesitter_exception_returns_original(self):
        """If tree-sitter raises, compress() must return the original content."""
        source = "function broken() {}"
        # Inject a fake parser that raises
        bad_parser = MagicMock()
        bad_parser.parse.side_effect = RuntimeError("parser exploded")
        self.c.parsers["javascript"] = bad_parser

        result = self.c.compress(source, "app.js")
        self.assertEqual(result, source)


# ---------------------------------------------------------------------------
# Parser loading — mocked to avoid requiring installed packages
# ---------------------------------------------------------------------------

class TestParserLoading(unittest.TestCase):

    def test_missing_package_reported(self):
        """Missing tree-sitter language package should be recorded, not raise."""
        try:
            from tree_sitter import Language, Parser  # noqa
            ts_available = True
        except ImportError:
            ts_available = False

        if not ts_available:
            self.skipTest("tree-sitter core not installed — skipping")

        # Patch only the compressor module's import_module, not the global one
        with patch(
            "code_assembler.compressor.importlib.import_module",
            side_effect=ImportError("no module"),
        ):
            with patch("builtins.print"):  # suppress console output
                c = CodeCompressor([".js"])

        self.assertNotIn("javascript", c.parsers)
        self.assertTrue(len(c._missing_packages) > 0)

    def test_python_never_needs_treesitter(self):
        """Python extension should not trigger any tree-sitter load attempt."""
        with patch("importlib.import_module") as mock_import:
            c = CodeCompressor([".py"])
            # tree-sitter modules should NOT have been imported for Python
            ts_calls = [
                call for call in mock_import.call_args_list
                if "tree_sitter" in str(call)
            ]
            self.assertEqual(len(ts_calls), 0)


if __name__ == "__main__":
    unittest.main()