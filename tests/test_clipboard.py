"""
Tests for clipboard functionality.
"""
import unittest
import sys
import argparse
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.utils import copy_to_clipboard
from code_assembler.cli import main

class TestClipboard(unittest.TestCase):

    @patch('subprocess.run')
    def test_copy_to_clipboard_windows(self, mock_run):
        """Test clipboard call on Windows using PowerShell with UTF8 forced input."""
        with patch('platform.system', return_value='Windows'):
            test_text = "test content with emoji 🚀"
            result = copy_to_clipboard(test_text)

            self.assertTrue(result)
            # Vérifie la commande complexe et l'encodage utf-8
            mock_run.assert_called_once_with(
                [
                    "powershell", "-NoProfile", "-Command",
                    "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
                    "$input | Out-String | Set-Clipboard"
                ],
                input=test_text,
                encoding='utf-8',
                check=True
            )

    @patch('subprocess.run')
    def test_copy_to_clipboard_mac(self, mock_run):
        """Test clipboard call on macOS using pbcopy."""
        with patch('platform.system', return_value='Darwin'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            mock_run.assert_called_once_with(
                "pbcopy", input="test content", text=True, check=True
            )

    @patch('subprocess.run')
    def test_copy_to_clipboard_linux_xclip(self, mock_run):
        """Test clipboard call on Linux using xclip."""
        with patch('platform.system', return_value='Linux'):
            result = copy_to_clipboard("test content")
            self.assertTrue(result)
            mock_run.assert_called_with(
                ["xclip", "-selection", "clipboard"],
                input="test content", text=True, check=True
            )

    @patch('code_assembler.cli.parse_args')
    @patch('code_assembler.cli.assemble_codebase')
    @patch('code_assembler.utils.copy_to_clipboard')
    def test_cli_calls_clipboard(self, mock_copy, mock_assemble, mock_parse):
        """Test that CLI triggers clipboard copy when --clip is set."""

        # Configuration d'un Namespace complet
        args = argparse.Namespace(
            clip=True,
            paths=["src"],
            extensions=[".py"],
            interactive=False,
            config=None,
            rebuild=None,
            show_excludes=False,
            save_config=None,
            output="codebase.md",
            exclude_patterns=[],
            recursive=True,
            include_readmes=True,
            use_default_excludes=True,
            max_size=10.0,
            since=None
        )
        mock_parse.return_value = args

        mock_assemble.return_value = "# Generated Content"
        mock_copy.return_value = True

        # Exécution en capturant stdout
        with patch('sys.stdout', new=StringIO()):
            main()

        # Vérification que la fonction de haut niveau a été appelée
        mock_copy.assert_called_once_with("# Generated Content")

if __name__ == '__main__':
    unittest.main()