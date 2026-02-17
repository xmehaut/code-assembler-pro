"""
Tests for clipboard functionality.
"""
import argparse
import sys
import unittest
from io import StringIO  # Importation déplacée ici
from pathlib import Path
from unittest.mock import patch

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
            # Vérifie que 'clip' a été appelé
            mock_run.assert_called_once()

    @patch('code_assembler.cli.parse_args')
    @patch('code_assembler.cli.assemble_codebase')
    @patch('code_assembler.utils.copy_to_clipboard')
    def test_cli_calls_clipboard(self, mock_copy, mock_assemble, mock_parse):
        """Test that CLI triggers clipboard copy when --clip is set."""

        # Configuration d'un Namespace complet pour éviter les erreurs dans main()
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

        # Simulation du résultat de l'assemblage
        mock_assemble.return_value = "# Generated Content"
        mock_copy.return_value = True

        # Exécution en capturant la sortie standard
        with patch('sys.stdout', new=StringIO()):
            main()

        # Vérification que la fonction de copie a bien été appelée avec le contenu
        mock_copy.assert_called_once_with("# Generated Content")


if __name__ == '__main__':
    unittest.main()
