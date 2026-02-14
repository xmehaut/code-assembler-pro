import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from code_assembler.utils import (
    should_exclude,
    normalize_path,
    format_file_size,
    slugify_path
)


class TestUtils(unittest.TestCase):

    def test_normalize_path(self):
        """Test path normalization for cross-platform consistency."""
        # Windows style to POSIX
        self.assertEqual(normalize_path("C:\\Users\\Test"), "c:/users/test")

        # Trailing slash removal
        res = normalize_path("/var/www/html/")
        self.assertTrue(res.endswith("/var/www/html"))

        self.assertEqual(normalize_path(""), "")

    def test_should_exclude(self):
        """Test the exclusion logic with various patterns."""
        patterns = ["__pycache__", ".git", "venv", "secret.py"]

        # Case 1: Parent directory exclusion
        self.assertTrue(should_exclude("/abs/path/to/__pycache__/file.pyc", patterns))

        # Case 2: Root folder exclusion
        self.assertTrue(should_exclude(".git/config", patterns))

        # Case 3: Exact filename exclusion
        self.assertTrue(should_exclude("src/secret.py", patterns))

        # Case 4: Should NOT exclude
        self.assertFalse(should_exclude("src/main.py", patterns))

        # Case 5: Glob pattern (prefix match with wildcard)
        self.assertTrue(should_exclude("tests/test_user.py", ["test_*"]))

        # Case 6: No false positives — "dist" must NOT match "redistribute"
        self.assertFalse(should_exclude("src/redistribute.py", ["dist"]))

        # Case 7: No false positives — "env" must NOT match "environment.py"
        self.assertFalse(should_exclude("src/environment.py", ["env"]))

        # Case 8: Extension pattern
        self.assertTrue(should_exclude("cache/module.pyc", [".pyc"]))

    def test_format_file_size(self):
        """Test human-readable file size formatting."""
        self.assertEqual(format_file_size(0), "0B")
        self.assertEqual(format_file_size(512), "512B")
        self.assertEqual(format_file_size(1024), "1.0KB")
        self.assertEqual(format_file_size(1572864), "1.5MB")

    def test_slugify(self):
        """Test conversion of paths to valid HTML anchors."""
        self.assertEqual(slugify_path("path/to/File.py"), "path_to_file_py")
        self.assertEqual(slugify_path("C:\\My Docs\\script.js"), "c__my_docs_script_js")


if __name__ == '__main__':
    unittest.main()