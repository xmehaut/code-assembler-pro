import unittest
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from code_assembler.file_io import read_file_head


class TestFileIO(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_path = Path(self.test_dir) / "test_file.txt"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_file_head(self):
        """Test reading only the first N lines of a file."""
        content = "\n".join([f"Line {i}" for i in range(1, 11)])
        self.file_path.write_text(content, encoding='utf-8')

        head = read_file_head(str(self.file_path), max_lines=3)

        lines = head.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], "Line 1")
        self.assertEqual(lines[2], "Line 3")

    def test_read_file_head_small_file(self):
        """Test reading head of a file smaller than the limit."""
        self.file_path.write_text("Single line", encoding='utf-8')

        head = read_file_head(str(self.file_path), max_lines=50)
        self.assertEqual(head, "Single line")


if __name__ == '__main__':
    unittest.main()