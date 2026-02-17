import json
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


if __name__ == '__main__':
    unittest.main()
