"""
Tests for file format detection and syntax highlighting.
"""
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.formatters import MarkdownFormatter


class TestFileFormats(unittest.TestCase):
    def setUp(self):
        self.formatter = MarkdownFormatter()

    def test_standard_extensions(self):
        """Test detection of common extensions."""
        self.assertEqual(self.formatter._detect_language("main.py"), "python")
        self.assertEqual(self.formatter._detect_language("script.js"), "javascript")
        self.assertEqual(self.formatter._detect_language("styles.css"), "css")

    def test_new_formats(self):
        """Test detection of newly added formats like Jinja2."""
        self.assertEqual(self.formatter._detect_language("template.j2"), "jinja2")
        self.assertEqual(self.formatter._detect_language("config.jinja2"), "jinja2")
        self.assertEqual(self.formatter._detect_language("infra.tf"), "hcl")

    def test_special_filenames(self):
        """Test detection of files without extensions or special names."""
        self.assertEqual(self.formatter._detect_language("Dockerfile"), "dockerfile")
        self.assertEqual(self.formatter._detect_language("Makefile"), "makefile")
        self.assertEqual(self.formatter._detect_language(".env"), "bash")
        self.assertEqual(self.formatter._detect_language(".env.local"), "bash")

    def test_case_insensitivity(self):
        """Test that detection is case-insensitive."""
        self.assertEqual(self.formatter._detect_language("MAIN.PY"), "python")
        self.assertEqual(self.formatter._detect_language("DOCKERFILE"), "dockerfile")

    def test_unknown_format(self):
        """Test fallback to 'text' for unknown formats."""
        self.assertEqual(self.formatter._detect_language("data.unknown_ext"), "text")
        self.assertEqual(self.formatter._detect_language("README"), "text")


if __name__ == "__main__":
    unittest.main()
