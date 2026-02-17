"""
Interactive wizard mode for Code Assembler Pro.

This module provides a user-friendly interactive interface for configuring
and running the assembler without memorizing CLI arguments.
"""

import os
from typing import List, Optional, Dict, Any

from .constants import LANGUAGE_MAP, DEFAULT_EXCLUDE_PATTERNS, EMOJI
from .core import assemble_codebase


class InteractiveWizard:
    """
    Interactive configuration wizard for Code Assembler Pro.

    Guides users through the configuration process with smart defaults
    and contextual help.
    """

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.available_extensions = self._get_available_extensions()

    def _get_available_extensions(self) -> List[str]:
        """Get list of supported extensions from LANGUAGE_MAP."""
        return sorted(list(set(LANGUAGE_MAP.keys())))

    def _print_banner(self):
        """Print welcome banner."""
        print("\n" + "=" * 70)
        print(f"{EMOJI['rocket']}  Code Assembler Pro - Interactive Mode")
        print("=" * 70)
        print("\nWelcome! This wizard will help you configure your codebase assembly.")
        print("Press Ctrl+C at any time to cancel.\n")

    def _print_section(self, title: str):
        """Print section header."""
        print(f"\n{EMOJI['target']} {title}")
        print("-" * 70)

    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """
        Ask a yes/no question.

        Args:
            question: Question to ask
            default: Default answer if user just presses Enter

        Returns:
            True for yes, False for no
        """
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{question} [{default_str}]: ").strip().lower()

            if not response:
                return default

            if response in ['y', 'yes', 'oui']:
                return True
            elif response in ['n', 'no', 'non']:
                return False
            else:
                print(f"{EMOJI['warning']}  Please answer 'y' or 'n'")

    def _ask_number(self, question: str, default: float, min_val: float = 0.0) -> float:
        """
        Ask for a number with validation.

        Args:
            question: Question to ask
            default: Default value
            min_val: Minimum allowed value

        Returns:
            User's number or default
        """
        while True:
            response = input(f"{question} [default: {default}]: ").strip()

            if not response:
                return default

            try:
                value = float(response)
                if value < min_val:
                    print(f"{EMOJI['warning']}  Value must be >= {min_val}")
                    continue
                return value
            except ValueError:
                print(f"{EMOJI['warning']}  Please enter a valid number")

    def _ask_text(self, question: str, default: str = "") -> str:
        """
        Ask for text input.

        Args:
            question: Question to ask
            default: Default value

        Returns:
            User's input or default
        """
        if default:
            response = input(f"{question} [default: {default}]: ").strip()
            return response if response else default
        else:
            response = input(f"{question}: ").strip()
            return response

    def _select_paths(self) -> List[str]:
        """Interactive path selection."""
        self._print_section("Step 1: Select Paths to Analyze")

        print("\nYou can analyze:")
        print("  1. Current directory (.)")
        print("  2. Specific directory/directories")
        print("  3. Specific files")

        paths = []

        choice = input("\nYour choice [1-3]: ").strip()

        if choice == "1":
            paths = ["."]
            print(f"{EMOJI['success']} Selected: current directory")

        elif choice == "2":
            print("\nEnter directory paths (one per line, empty line to finish):")
            while True:
                path = input("  Path: ").strip()
                if not path:
                    break

                if os.path.exists(path):
                    if os.path.isdir(path):
                        paths.append(path)
                        print(f"  {EMOJI['success']} Added: {path}")
                    else:
                        print(f"  {EMOJI['warning']}  '{path}' is not a directory")
                else:
                    print(f"  {EMOJI['warning']}  '{path}' does not exist")

        elif choice == "3":
            print("\nEnter file paths (one per line, empty line to finish):")
            while True:
                path = input("  File: ").strip()
                if not path:
                    break

                if os.path.exists(path) and os.path.isfile(path):
                    paths.append(path)
                    print(f"  {EMOJI['success']} Added: {path}")
                else:
                    print(f"  {EMOJI['warning']}  '{path}' is not a valid file")

        if not paths:
            print(f"{EMOJI['warning']}  No paths selected, using current directory")
            paths = ["."]

        return paths

    def _select_extensions(self) -> List[str]:
        """Interactive extension selection."""
        self._print_section("Step 2: Select File Extensions")

        print("\nCommon presets:")
        presets = {
            "1": ([".py"], "Python projects"),
            "2": ([".py", ".md", ".toml", ".yaml"], "Python + Config + Docs"),
            "3": ([".js", ".ts", ".jsx", ".tsx"], "JavaScript/TypeScript"),
            "4": ([".rs", ".toml"], "Rust projects"),
            "5": ([".go", ".mod"], "Go projects"),
            "6": ([".java"], "Java projects"),
            "7": ([".c", ".cpp", ".h", ".hpp"], "C/C++ projects"),
        }

        for key, (exts, desc) in presets.items():
            print(f"  {key}. {desc} ({', '.join(exts)})")
        print("  8. Custom selection")

        choice = input("\nYour choice [1-8]: ").strip()

        if choice in presets:
            extensions, desc = presets[choice]
            print(f"{EMOJI['success']} Selected: {desc}")
            return extensions

        # Custom selection
        print("\nAvailable extensions:")
        for i, ext in enumerate(self.available_extensions, 1):
            lang = LANGUAGE_MAP.get(ext, "unknown")
            print(f"  {ext:12} ({lang})", end="")
            if i % 4 == 0:
                print()
        print()

        print("\nEnter extensions separated by spaces (e.g., .py .js .md):")
        extensions_input = input("Extensions: ").strip()

        extensions = []
        for ext in extensions_input.replace(',', ' ').split():
            ext = ext.strip().rstrip(',')  # double sécurité
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.append(ext)

        if not extensions:
            print(f"{EMOJI['warning']}  No extensions selected, using .py as default")
            extensions = [".py"]

        return extensions

    def _configure_exclusions(self) -> List[str]:
        """Configure exclusion patterns."""
        self._print_section("Step 3: Configure Exclusions")

        print("\nDefault exclusions:")
        print(f"  {', '.join(DEFAULT_EXCLUDE_PATTERNS[:10])}")
        if len(DEFAULT_EXCLUDE_PATTERNS) > 10:
            print(f"  ... and {len(DEFAULT_EXCLUDE_PATTERNS) - 10} more")

        use_defaults = self._ask_yes_no("\nUse default exclusions?", default=True)

        custom_patterns = []

        if self._ask_yes_no("Add custom exclusion patterns?", default=False):
            print("\nEnter patterns (one per line, empty line to finish):")
            print("Examples: tests/, *.log, secret.py, temp_*")
            while True:
                pattern = input("  Pattern: ").strip()
                if not pattern:
                    break
                custom_patterns.append(pattern)
                print(f"  {EMOJI['success']} Added: {pattern}")

        if use_defaults:
            return list(set(DEFAULT_EXCLUDE_PATTERNS + custom_patterns))
        else:
            return custom_patterns

    def _configure_output(self) -> str:
        """Configure output filename."""
        self._print_section("Step 4: Output Configuration")

        default_name = "codebase.md"
        output = self._ask_text(f"\nOutput filename", default=default_name)

        if not output.endswith('.md'):
            output += '.md'

        # Check if file exists
        if os.path.exists(output):
            if not self._ask_yes_no(f"{EMOJI['warning']}  '{output}' already exists. Overwrite?", default=False):
                counter = 1
                while os.path.exists(f"codebase_{counter}.md"):
                    counter += 1
                output = f"codebase_{counter}.md"
                print(f"{EMOJI['success']} Using: {output}")

        return output

    def _configure_advanced(self) -> Dict[str, Any]:
        """Configure advanced options."""
        self._print_section("Step 5: Advanced Options")

        advanced = {}

        if self._ask_yes_no("\nConfigure advanced options?", default=False):

            advanced['recursive'] = self._ask_yes_no(
                "  Recursively traverse subdirectories?",
                default=True
            )

            advanced['include_readmes'] = self._ask_yes_no(
                "  Automatically include README files?",
                default=True
            )

            print("\n  File size handling:")
            advanced['max_file_size_mb'] = self._ask_number(
                "    Maximum file size (MB)",
                default=10.0,
                min_val=0.1
            )

            advanced['truncate_large_files'] = self._ask_yes_no(
                "    Truncate large files instead of skipping?",
                default=True
            )

            if advanced['truncate_large_files']:
                advanced['truncation_limit_lines'] = int(self._ask_number(
                    "      Keep first N lines when truncating",
                    default=500,
                    min_val=10
                ))
        else:
            # Use sensible defaults
            advanced = {
                'recursive': True,
                'include_readmes': True,
                'max_file_size_mb': 10.0,
                'truncate_large_files': True,
                'truncation_limit_lines': 500,
            }

        advanced['show_progress'] = True

        return advanced

    def _show_summary(self):
        """Display configuration summary."""
        self._print_section("Configuration Summary")

        print(f"\n{EMOJI['folder']} Paths: {', '.join(self.config['paths'])}")
        print(f"{EMOJI['memo']} Extensions: {', '.join(self.config['extensions'])}")
        print(f"{EMOJI['floppy']} Output: {self.config['output']}")
        print(f"{EMOJI['recycle']} Recursive: {self.config.get('recursive', True)}")
        print(f"{EMOJI['book']} Include READMEs: {self.config.get('include_readmes', True)}")
        print(f"{EMOJI['mag']} Max file size: {self.config.get('max_file_size_mb', 10.0)} MB")
        print(f"{EMOJI['warning']}  Truncate large files: {self.config.get('truncate_large_files', True)}")

        if self.config.get('truncate_large_files'):
            print(f"   Keep first {self.config.get('truncation_limit_lines', 500)} lines")

        if self.config.get('exclude_patterns'):
            print(f"\n{EMOJI['error']} Exclusions: {len(self.config['exclude_patterns'])} patterns")
            if len(self.config['exclude_patterns']) <= 5:
                for pattern in self.config['exclude_patterns']:
                    print(f"   - {pattern}")
            else:
                for pattern in self.config['exclude_patterns'][:5]:
                    print(f"   - {pattern}")
                print(f"   ... and {len(self.config['exclude_patterns']) - 5} more")

    def _save_config(self):
        """Optionally save configuration to JSON."""
        if self._ask_yes_no(f"\n{EMOJI['floppy']} Save this configuration for future use?", default=False):
            import json

            config_name = self._ask_text("Configuration filename", default="assembler_config.json")
            if not config_name.endswith('.json'):
                config_name += '.json'

            # Prepare config for JSON (remove runtime flags)
            save_config = {k: v for k, v in self.config.items() if k != 'show_progress'}

            with open(config_name, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=2, ensure_ascii=False)

            print(f"{EMOJI['success']} Configuration saved to: {config_name}")
            print(f"   Reuse it with: code-assembler --config {config_name}")

    def run(self) -> Optional[str]:
        """
        Run the interactive wizard.

        Returns:
            Generated markdown content, or None if cancelled
        """
        try:
            self._print_banner()

            # Step 1: Paths
            self.config['paths'] = self._select_paths()

            # Step 2: Extensions
            self.config['extensions'] = self._select_extensions()

            # Step 3: Exclusions
            exclude_patterns = self._configure_exclusions()
            if exclude_patterns:
                self.config['exclude_patterns'] = exclude_patterns

            # Step 4: Output
            self.config['output'] = self._configure_output()

            # Step 5: Advanced options
            advanced = self._configure_advanced()
            self.config.update(advanced)

            # Summary
            self._show_summary()

            # Confirm
            if not self._ask_yes_no(f"\n{EMOJI['rocket']} Start assembly?", default=True):
                print(f"\n{EMOJI['error']} Assembly cancelled.")
                return None

            # Save config option
            self._save_config()

            # Run assembly
            print(f"\n{EMOJI['rocket']} Starting assembly...\n")

            content = assemble_codebase(**self.config)

            print(f"\n{EMOJI['success']} Assembly completed successfully!")
            print(f"{EMOJI['file']} Output file: {self.config['output']}")

            return content

        except KeyboardInterrupt:
            print(f"\n\n{EMOJI['error']} Wizard cancelled by user.")
            return None
        except Exception as e:
            print(f"\n{EMOJI['error']} An error occurred: {e}")
            import traceback
            traceback.print_exc()
            return None


def run_interactive_mode():
    """
    Entry point for interactive mode.

    Usage:
        code-assembler --interactive
        or
        python -m code_assembler.interactive
    """
    wizard = InteractiveWizard()
    wizard.run()


if __name__ == "__main__":
    run_interactive_mode()
