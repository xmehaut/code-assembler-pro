"""
Tests for interactive wizard mode.
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.interactive import InteractiveWizard


class TestInteractiveWizard(unittest.TestCase):
    """Test cases for the interactive wizard."""

    def setUp(self):
        """Set up test wizard instance."""
        self.wizard = InteractiveWizard()

    def test_yes_no_default_yes(self):
        """Test yes/no question with default Yes."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_yes_no("Test?", default=True)
            self.assertTrue(result)

    def test_yes_no_default_no(self):
        """Test yes/no question with default No."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_yes_no("Test?", default=False)
            self.assertFalse(result)

    def test_yes_no_explicit_yes(self):
        """Test explicit yes answer."""
        with patch('builtins.input', return_value='y'):
            result = self.wizard._ask_yes_no("Test?")
            self.assertTrue(result)

    def test_yes_no_explicit_no(self):
        """Test explicit no answer."""
        with patch('builtins.input', return_value='n'):
            result = self.wizard._ask_yes_no("Test?")
            self.assertFalse(result)

    def test_ask_number_default(self):
        """Test number input with default."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_number("Size?", default=10.0)
            self.assertEqual(result, 10.0)

    def test_ask_number_custom(self):
        """Test number input with custom value."""
        with patch('builtins.input', return_value='5.5'):
            result = self.wizard._ask_number("Size?", default=10.0)
            self.assertEqual(result, 5.5)

    def test_ask_number_validation(self):
        """Test number input validation."""
        # First invalid, then valid
        with patch('builtins.input', side_effect=['invalid', '5.0']):
            result = self.wizard._ask_number("Size?", default=10.0)
            self.assertEqual(result, 5.0)

    def test_ask_text_default(self):
        """Test text input with default."""
        with patch('builtins.input', return_value=''):
            result = self.wizard._ask_text("Name?", default="test.md")
            self.assertEqual(result, "test.md")

    def test_ask_text_custom(self):
        """Test text input with custom value."""
        with patch('builtins.input', return_value='custom.md'):
            result = self.wizard._ask_text("Name?", default="test.md")
            self.assertEqual(result, "custom.md")

    def test_select_paths_current_dir(self):
        """Test selecting current directory."""
        with patch('builtins.input', return_value='1'):
            paths = self.wizard._select_paths()
            self.assertEqual(paths, ['.'])

    def test_select_extensions_preset(self):
        """Test selecting extension preset."""
        with patch('builtins.input', return_value='1'):
            extensions = self.wizard._select_extensions()
            self.assertIn('.py', extensions)

    def test_configure_exclusions_defaults_only(self):
        """Test using default exclusions."""
        with patch('builtins.input', side_effect=['y', 'n']):  # Use defaults, no custom
            patterns = self.wizard._configure_exclusions()
            self.assertIn('__pycache__', patterns)
            self.assertIn('.git', patterns)

    def test_configure_output_default(self):
        """Test output configuration with default."""
        with patch('builtins.input', return_value=''):
            with patch('code_assembler.interactive.os.path.exists', return_value=False):
                output = self.wizard._configure_output()
                self.assertEqual(output, 'codebase.md')

    def test_configure_output_custom(self):
        """Test output configuration with custom name."""
        with patch('builtins.input', return_value='my_project'):
            output = self.wizard._configure_output()
            self.assertEqual(output, 'my_project.md')  # Should auto-add .md

    def test_configure_advanced_all_defaults(self):
        """Test advanced config with all defaults."""
        with patch('builtins.input', return_value='n'):  # Don't configure advanced
            advanced = self.wizard._configure_advanced()
            self.assertTrue(advanced['recursive'])
            self.assertTrue(advanced['include_readmes'])
            self.assertEqual(advanced['max_file_size_mb'], 10.0)

    @patch('builtins.input')
    @patch('code_assembler.interactive.os.path.exists')
    def test_full_wizard_flow(self, mock_exists, mock_input):
        """Test complete wizard flow."""
        # Mock user inputs for entire flow
        mock_input.side_effect = [
            '1',      # Current directory
            '1',      # Python preset
            'y', 'n', # Use defaults, no custom exclusions
            '',       # Default output name
            'n',      # No advanced config
            'y',      # Confirm assembly
            'n',      # Don't save config
        ]

        # Mock file existence check
        mock_exists.return_value = False

        # Mock assemble_codebase to avoid actual execution
        with patch('code_assembler.interactive.assemble_codebase') as mock_assemble:
            mock_assemble.return_value = "# Mock content"

            # Capture print output
            with patch('sys.stdout', new=StringIO()):
                result = self.wizard.run()

            # Verify assemble was called
            mock_assemble.assert_called_once()

            # Verify result
            self.assertEqual(result, "# Mock content")

    def test_wizard_keyboard_interrupt(self):
        """Test wizard handles Ctrl+C gracefully."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new=StringIO()):
                result = self.wizard.run()
            self.assertIsNone(result)

    def test_available_extensions(self):
        """Test that available extensions are loaded."""
        self.assertGreater(len(self.wizard.available_extensions), 0)
        self.assertIn('.py', self.wizard.available_extensions)
        self.assertIn('.js', self.wizard.available_extensions)

    def test_select_extensions_custom_with_commas(self):
        """Regression test: extensions typed with commas must be cleaned."""
        # Simule l'utilisateur qui tape ".py, .yaml, .tsx,"
        with patch('builtins.input', side_effect=['8', '.py, .yaml, .tsx,']):
            extensions = self.wizard._select_extensions()

        self.assertIn('.py', extensions)
        self.assertIn('.yaml', extensions)
        self.assertIn('.tsx', extensions)
        # S'assurer qu'aucune extension ne contient de virgule
        for ext in extensions:
            self.assertNotIn(',', ext, f"Extension '{ext}' contains a comma!")

    def test_select_extensions_custom_space_separated(self):
        """Normal case: space-separated extensions work correctly."""
        with patch('builtins.input', side_effect=['8', '.py .yaml .tsx']):
            extensions = self.wizard._select_extensions()

        self.assertIn('.py', extensions)
        self.assertIn('.yaml', extensions)
        self.assertIn('.tsx', extensions)

if __name__ == '__main__':
    unittest.main()