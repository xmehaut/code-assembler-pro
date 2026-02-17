"""
Tests for the Rebuild functionality of Code Assembler Pro.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.rebuilder import CodebaseRebuilder


class TestRebuild(unittest.TestCase):
    def setUp(self):
        """Create a temporary environment for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.output_dir = self.root / "restored"
        self.md_file = self.root / "snapshot.md"

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def _create_mock_md(self, files_data: dict, metadata_files: dict):
        """
        Helper to create a valid Markdown snapshot with metadata.
        files_data: { "rel/path": "content" }
        metadata_files: { "rel/path": "timestamp" }
        """
        lines = ["# Consolidated Codebase\n", "## Table of Contents\n"]

        # Add TOC
        for path in metadata_files:
            lines.append(f"- `{path}` | 2026-02-17 10:00")

        lines.append("\n---\n")

        # Add File Blocks
        for path, content in files_data.items():
            lines.append(f"# `{path}`\n")
            lines.append("```python")
            lines.append(content)
            lines.append("```\n")

        # Add Metadata Block
        metadata = {
            "version": "4.4.0",
            "generated_at": "2026-02-17 10:00:00",
            "files": metadata_files
        }
        lines.append(f"\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(metadata)}\n-->")

        self.md_file.write_text("\n".join(lines), encoding='utf-8')

    def test_successful_rebuild(self):
        """Test a standard successful reconstruction of multiple files."""
        files = {
            "src/main.py": "print('hello')",
            "config/settings.json": '{"key": "value"}'
        }
        meta = {
            "src/main.py": "2026-02-17 10:00",
            "config/settings.json": "2026-02-17 10:00"
        }
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 2)
        self.assertEqual(len(errors), 0)

        # Verify files exist and content is correct
        self.assertTrue((self.output_dir / "src/main.py").exists())
        self.assertEqual((self.output_dir / "src/main.py").read_text(), "print('hello')")
        self.assertTrue((self.output_dir / "config/settings.json").exists())

    def test_security_path_traversal(self):
        """Test that the rebuilder blocks attempts to write outside the output directory."""
        files = {"../../evil.py": "malicious code"}
        meta = {"../../evil.py": "2026-02-17 10:00"}
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 0)
        self.assertTrue(any("Security skip" in err for err in errors))
        self.assertFalse((self.root / "evil.py").exists())

    def test_dry_run(self):
        """Test that dry_run mode does not write any files."""
        files = {"test.py": "content"}
        meta = {"test.py": "2026-02-17 10:00"}
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir), dry_run=True)
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 1)
        self.assertFalse(self.output_dir.exists())

    def test_truncation_warning(self):
        """Test that the rebuilder detects and warns about truncated files."""
        files = {"large.py": "part 1\n[TRUNCATED]\npart 2"}
        meta = {"large.py": "2026-02-17 10:00"}
        self._create_mock_md(files, meta)

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 1)
        self.assertTrue(any("truncated" in err.lower() for err in errors))

    def test_missing_metadata(self):
        """Test behavior when the Markdown file has no metadata block."""
        self.md_file.write_text("# Just some markdown", encoding='utf-8')

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(count, 0)
        self.assertIn("No valid metadata found", errors[0])


if __name__ == "__main__":
    unittest.main()
