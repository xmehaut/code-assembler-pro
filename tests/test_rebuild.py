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


class TestRebuildRegressions(unittest.TestCase):
    """
    Regression tests for three bugs found in _extract_file_content() while
    rebuilding real-world snapshots:

      1. A non-greedy '(.*?)\\n```' capture stopped at the FIRST closing
         fence, even when that fence was nested inside the file's own
         content (e.g. a .md file documenting a code example).
      2. An unanchored '.*?' between a file's header and its opening fence
         let the search latch onto a prose heading that merely wraps an
         identifier in backticks (e.g. "#### `@Contract.validate` and
         `self` in tests"), followed later by an unrelated code block.
      3. Matching by filename substring caused collisions between files
         sharing the same name at different paths (multiple
         `pyproject.toml` in one monorepo snapshot, for example).

    These tests build raw Markdown snapshots directly (rather than going
    through `_create_mock_md`, whose helper always wraps a single flat
    string in one fence per file) because reproducing the bugs requires
    nested fences and multi-block documents that helper cannot express.
    """

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.output_dir = self.root / "restored"
        self.md_file = self.root / "snapshot.md"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _write(self, raw_markdown: str, files: dict):
        """Write a raw snapshot body plus a matching metadata block."""
        metadata = {
            "version": "4.5.1",
            "generated_at": "2026-01-01 10:00:00",
            "files": files,
        }
        full = raw_markdown + f"\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(metadata)}\n-->\n"
        self.md_file.write_text(full, encoding='utf-8')

    def test_nested_fence_inside_file_content(self):
        """
        A markdown file whose own content contains a fenced code example
        must be extracted in full, not truncated at the first nested
        closing fence.
        """
        raw = (
            "# Consolidated Codebase\n\n"
            "## Table of Contents\n\n"
            "- `docs/guide.md` | 2026-01-01 10:00\n"
            "- `src/next_file.py` | 2026-01-01 10:00\n\n"
            "---\n\n"
            "### `docs/guide.md`\n\n"
            "```markdown\n"
            "# Guide\n\n"
            "Here is an example:\n\n"
            "```python\n"
            "print(\"nested fence\")\n"
            "```\n\n"
            "End of guide.\n"
            "```\n\n"
            "### `src/next_file.py`\n\n"
            "```python\n"
            "print(\"next file content\")\n"
            "```\n"
        )
        self._write(raw, {
            "docs/guide.md": "2026-01-01 10:00",
            "src/next_file.py": "2026-01-01 10:00",
        })

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

        guide = (self.output_dir / "docs/guide.md").read_text()
        self.assertIn("End of guide.", guide)
        self.assertIn('print("nested fence")', guide)

        next_file = (self.output_dir / "src/next_file.py").read_text()
        self.assertEqual(next_file, 'print("next file content")')

    def test_prose_heading_with_backticks_is_not_a_file_boundary(self):
        """
        A markdown sub-heading that wraps an identifier in backticks (and
        is itself followed, later in the same paragraph, by an unrelated
        code block) must not be mistaken for the next file's header — the
        first file's content must include everything up to its own real
        closing fence.
        """
        raw = (
            "# Consolidated Codebase\n\n"
            "## Table of Contents\n\n"
            "- `core/contracts.md` | 2026-01-01 10:00\n"
            "- `core/next.py` | 2026-01-01 10:00\n\n"
            "---\n\n"
            "### `core/contracts.md`\n\n"
            "```markdown\n"
            "# Contracts\n\n"
            "#### `@Contract.validate` and `self` in tests\n\n"
            "When used at module level this works as expected. Example:\n\n"
            "```python\n"
            "def my_rule(inputs, output):\n"
            "    pass\n"
            "```\n\n"
            "End of section.\n"
            "```\n\n"
            "### `core/next.py`\n\n"
            "```python\n"
            "print(\"real next file\")\n"
            "```\n"
        )
        self._write(raw, {
            "core/contracts.md": "2026-01-01 10:00",
            "core/next.py": "2026-01-01 10:00",
        })

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

        contracts = (self.output_dir / "core/contracts.md").read_text()
        self.assertIn("End of section.", contracts)
        self.assertNotIn("real next file", contracts)

        next_file = (self.output_dir / "core/next.py").read_text()
        self.assertEqual(next_file, 'print("real next file")')

    def test_duplicate_filename_at_different_paths(self):
        """
        Two files sharing the same name at different paths (a common
        monorepo pattern, e.g. several pyproject.toml) must each resolve
        to their own content — not whichever header the search happens to
        reach first.
        """
        raw = (
            "# Consolidated Codebase\n\n"
            "## Table of Contents\n\n"
            "- `pyproject.toml` | 2026-01-01 10:00\n"
            "- `sub/pyproject.toml` | 2026-01-01 10:00\n\n"
            "---\n\n"
            "### `sub/pyproject.toml`\n\n"
            "```toml\n"
            "[project]\n"
            "name = \"sub-package\"\n"
            "```\n\n"
            "### `pyproject.toml`\n\n"
            "```toml\n"
            "[project]\n"
            "name = \"root-package\"\n"
            "```\n"
        )
        self._write(raw, {
            "pyproject.toml": "2026-01-01 10:00",
            "sub/pyproject.toml": "2026-01-01 10:00",
        })

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

        root_toml = (self.output_dir / "pyproject.toml").read_text()
        sub_toml = (self.output_dir / "sub/pyproject.toml").read_text()

        self.assertIn("root-package", root_toml)
        self.assertNotIn("sub-package", root_toml)
        self.assertIn("sub-package", sub_toml)
        self.assertNotIn("root-package", sub_toml)


if __name__ == "__main__":
    unittest.main()