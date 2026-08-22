import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# --- PATH SETUP ---
# Add the 'src' directory to the search path so 'code_assembler' can be found
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

from code_assembler.core import assemble_codebase, assemble_from_config


class TestCore(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory before each test."""
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        shutil.rmtree(self.test_dir)

    def test_smart_truncation(self):
        """Test if large files are correctly truncated based on configuration."""
        src_dir = self.root / "src"
        src_dir.mkdir()

        large_file = src_dir / "big_data.py"
        # Write 100 lines of dummy content
        content = "\n".join([f"line {i}" for i in range(100)])
        large_file.write_text(content, encoding='utf-8')

        output_file = self.root / "output.md"

        # Run assembly with a tiny size limit to force truncation
        assemble_codebase(
            paths=[str(src_dir)],
            extensions=[".py"],
            output=str(output_file),
            max_file_size_mb=0.0001,  # Very low threshold
            truncate_large_files=True,
            truncation_limit_lines=5,
            show_progress=False
        )

        result = output_file.read_text(encoding='utf-8')

        self.assertIn("line 0", result)
        self.assertIn("line 4", result)
        self.assertNotIn("line 50", result, "File was not truncated!")
        self.assertIn("[TRUNCATED]", result, "Truncation marker is missing")

    def test_exclusion_logic(self):
        """Test if the exclusion logic correctly skips specified patterns."""
        src_dir = self.root / "project"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('main')", encoding='utf-8')

        # Directory to exclude
        tests_dir = src_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("print('test')", encoding='utf-8')

        output_file = self.root / "output.md"

        assemble_codebase(
            paths=[str(src_dir)],
            extensions=[".py"],
            exclude_patterns=["tests"],
            output=str(output_file),
            show_progress=False
        )

        result = output_file.read_text(encoding='utf-8')
        self.assertIn("main.py", result)
        self.assertNotIn("test_main.py", result, "The 'tests' directory should have been excluded")

    def test_json_config_loading(self):
        """Test loading configuration from a JSON file and the output_file mapping."""
        src_dir = self.root / "src"
        src_dir.mkdir()
        (src_dir / "script.py").write_text("print('ok')", encoding='utf-8')

        config_file = self.root / "config.json"
        output_md = self.root / "result_from_json.md"

        # JSON config using 'output' key
        config_data = {
            "paths": [str(src_dir)],
            "extensions": [".py"],
            "output": str(output_md),
            "show_progress": False
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        assemble_from_config(str(config_file))

        self.assertTrue(output_md.exists(), "Output file defined in JSON was not created")


class TestFrontmatter(unittest.TestCase):
    """
    Tests for the YAML frontmatter block prepended to every generated
    snapshot (loosely inspired by Google's Open Knowledge Format), added
    so an agent reading only the start of a large file — or one with no
    network access to resolve `agents_doc` — still finds the rebuild
    instructions without having to reach the hidden
    CODE_ASSEMBLER_METADATA block at the end of the file.
    """

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_frontmatter_is_first_and_well_formed(self):
        """
        The document must start with '---' (not '# Consolidated
        Codebase'), the frontmatter must parse as valid YAML, its numeric
        fields must be raw ints (not comma-formatted display strings),
        and the header/TOC/stats sections must still follow immediately
        after, unchanged.
        """
        import yaml

        src_dir = self.root / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('hello')", encoding='utf-8')

        output_file = self.root / "output.md"
        assemble_codebase(
            paths=[str(src_dir)],
            extensions=[".py"],
            output=str(output_file),
            show_progress=False
        )

        content = output_file.read_text(encoding='utf-8')

        self.assertTrue(content.startswith("---\n"), "Document must start with the frontmatter delimiter")

        match = re.match(r'\A---\n(.*?)\n---\n', content, re.DOTALL)
        self.assertIsNotNone(match, "Frontmatter block not found or not closed")

        frontmatter = yaml.safe_load(match.group(1))
        self.assertEqual(frontmatter["type"], "source-bundle")
        self.assertEqual(frontmatter["generator"], "code-assembler-pro")
        self.assertIn("source_repo", frontmatter)
        self.assertTrue(frontmatter["agents_doc"].startswith(frontmatter["source_repo"]))
        self.assertIn("rebuild", frontmatter)
        self.assertIn("--rebuild", frontmatter["rebuild"])

        # Machine-readable fields: raw ints, not "1,234"-style display strings
        self.assertIsInstance(frontmatter["files"], int)
        self.assertIsInstance(frontmatter["tokens_estimate"], int)
        self.assertEqual(frontmatter["files"], 1)

        # The normal document must still follow right after (one blank
        # line is intentionally kept between the closing "---" and the
        # header, for readability)
        after_frontmatter = content[match.end():].lstrip("\n")
        self.assertTrue(after_frontmatter.startswith("# Consolidated Codebase"))

    def test_frontmatter_does_not_shift_delta_summary_injection(self):
        """
        Regression guard: generate_frontmatter() must never be rendered
        as part of main_header.md.j2 itself, and must only be prepended
        to `header` after `assemble()`'s `header.replace("---", ..., 1)`
        delta_summary injection has already run. Otherwise the
        frontmatter's own opening "---" becomes the first one in the
        document and silently steals the delta_summary insertion point
        from the real one in main_header.md.j2.
        """
        src_dir = self.root / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('v1')", encoding='utf-8')

        ref_md = self.root / "ref.md"
        assemble_codebase(
            paths=[str(src_dir)], extensions=[".py"],
            output=str(ref_md), show_progress=False
        )

        delta_md = self.root / "delta.md"
        assemble_codebase(
            paths=[str(src_dir)], extensions=[".py"],
            output=str(delta_md), since=str(ref_md), show_progress=False
        )

        content = delta_md.read_text(encoding='utf-8')

        # The delta note must appear in the actual header, i.e. after the
        # frontmatter's closing "---", not trapped inside the YAML block.
        match = re.match(r'\A---\n.*?\n---\n', content, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter_text = content[:match.end()]
        after_frontmatter = content[match.end():]

        self.assertNotIn("No changes detected", frontmatter_text)
        self.assertIn("No changes detected", after_frontmatter)


if __name__ == '__main__':
    unittest.main()

