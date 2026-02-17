"""
Tests for clipboard functionality.
"""
import unittest
import sys
import platform
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.utils import copy_to_clipboard
from code_assembler.cli import main


class TestClipboard(unittest.TestCase):

    @patch('subprocess.run')
    def test_copy_to_clipboard_windows(self, mock_run):
        """Test clipboard call on Windows."""
        with patch('platform.system', return_value='Windows'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            # Check if 'clip' was called
            mock_run.assert_called_once_with("clip", input="test content", text=True, check=True)

    @patch('subprocess.run')
    def test_copy_to_clipboard_mac(self, mock_run):
        """Test clipboard call on macOS."""
        with patch('platform.system', return_value='Darwin'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            # Check if 'pbcopy' was called
            mock_run.assert_called_once_with("pbcopy", input="test content", text=True, check=True)

    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xclip(self, mock_run):
        """Test clipboard call on Linux using xclip."""
        with patch('platform.system', return_value='Linux'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            # Check if 'xclip' was tried
            mock_run.assert_called_with(["xclip", "-selection", "clipboard"], input="test content", text=True,
                                        check=True)

    @patch('subprocess.run', side_effect=FileNotFoundError)
    def test_copy_to_clipboard_fail(self, mock_run):
        """Test failure when clipboard tool is missing."""
        result = copy_to_clipboard("test content")
        self.assertFalse(result)

    @patch('code_assembler.cli.parse_args')
    @patch('code_assembler.cli.assemble_codebase')
    @patch('code_assembler.utils.copy_to_clipboard')
    def test_cli_calls_clipboard(self, mock_copy, mock_assemble, mock_parse):
        """Test that CLI triggers clipboard copy when --clip is set."""
        # Setup mock arguments
        mock_args = MagicMock()
        mock_args.clip = True
        mock_args.paths = ["src"]
        mock_args.extensions = [".py"]
        mock_args.interactive = False
        mock_args.config = None
        mock_args.show_excludes = False
        mock_args.save_config = None
        mock_parse.return_value = mock_args

        # Setup mock assembly result
        mock_assemble.return_value = "# Generated Content"
        mock_copy.return_value = True

        # Run CLI main (with stdout suppressed)
        with patch('sys.stdout', new=MagicMock()):
            main()

        # Verify clipboard function was called with the assembly result
        mock_copy.assert_called_once_with("# Generated Content")


if __name__ == '__main__':
    unittest.main()