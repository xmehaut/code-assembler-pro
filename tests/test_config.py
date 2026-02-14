"""
Tests for configuration module.
"""
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.config import AssemblerConfig


class TestExtensionClassification(unittest.TestCase):
    """Test that extensions and exact filenames are correctly separated."""

    def _make_config(self, extensions):
        """Helper to create config with given extensions."""
        return AssemblerConfig(
            paths=["."],
            extensions=extensions,
            use_default_excludes=False
        )

    def test_bare_extensions(self):
        """Test that bare extensions (py, md, js) get a dot prefix."""
        config = self._make_config(["py", "md", "js"])
        self.assertEqual(sorted(config.extensions), [".js", ".md", ".py"])
        self.assertEqual(config.exact_filenames, [])

    def test_dotted_extensions(self):
        """Test that dotted extensions (.py, .md) stay as-is."""
        config = self._make_config([".py", ".md", ".toml"])
        self.assertEqual(sorted(config.extensions), [".md", ".py", ".toml"])
        self.assertEqual(config.exact_filenames, [])

    def test_exact_filenames(self):
        """Test that uppercase names become exact filenames."""
        config = self._make_config(["Dockerfile", "Makefile"])
        self.assertEqual(config.extensions, [])
        self.assertEqual(sorted(config.exact_filenames), ["Dockerfile", "Makefile"])

    def test_mixed(self):
        """Test mixed extensions and exact filenames."""
        config = self._make_config(["py", ".md", "Dockerfile", "toml", "Makefile"])
        self.assertEqual(sorted(config.extensions), [".md", ".py", ".toml"])
        self.assertEqual(sorted(config.exact_filenames), ["Dockerfile", "Makefile"])

    def test_dotfiles(self):
        """Test dotfiles like .env are treated as extensions."""
        config = self._make_config([".env", ".gitignore"])
        self.assertEqual(sorted(config.extensions), [".env", ".gitignore"])
        self.assertEqual(config.exact_filenames, [])

    def test_compound_extensions(self):
        """Test compound extensions like .env.j2."""
        config = self._make_config([".env.j2", "env.j2"])
        self.assertEqual(sorted(config.extensions), [".env.j2", ".env.j2"])
        self.assertEqual(config.exact_filenames, [])

    def test_realistic_python_project(self):
        """Test a realistic Python project configuration."""
        config = self._make_config(["py", "md", "toml", "yaml", "j2"])
        self.assertIn(".py", config.extensions)
        self.assertIn(".md", config.extensions)
        self.assertIn(".toml", config.extensions)
        self.assertIn(".yaml", config.extensions)
        self.assertIn(".j2", config.extensions)
        self.assertEqual(config.exact_filenames, [])

    def test_realistic_devops_project(self):
        """Test a realistic DevOps project configuration."""
        config = self._make_config([".py", ".yml", "Dockerfile", "Makefile", ".env"])
        self.assertIn(".py", config.extensions)
        self.assertIn(".yml", config.extensions)
        self.assertIn(".env", config.extensions)
        self.assertIn("Dockerfile", config.exact_filenames)
        self.assertIn("Makefile", config.exact_filenames)


if __name__ == "__main__":
    unittest.main()