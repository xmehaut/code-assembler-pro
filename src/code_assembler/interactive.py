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
    """Interactive configuration wizard for Code Assembler Pro."""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.available_extensions = self._get_available_extensions()

    def _get_available_extensions(self) -> List[str]:
        return sorted(list(set(LANGUAGE_MAP.keys())))

    def _print_banner(self):
        print("\n" + "=" * 70)
        print(f"{EMOJI['rocket']}  Code Assembler Pro - Interactive Mode")
        print("=" * 70)
        print("\nWelcome! This wizard will help you configure your codebase assembly.")
        print("Press Ctrl+C at any time to cancel.\n")

    def _print_section(self, title: str):
        print(f"\n{EMOJI['target']} {title}")
        print("-" * 70)

    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
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
        if default:
            response = input(f"{question} [default: {default}]: ").strip()
            return response if response else default
        else:
            return input(f"{question}: ").strip()

    def _select_paths(self) -> List[str]:
        self._print_section("Step 1: Select Paths to Analyze")
        print("\nYou can analyze:")
        print("  1. Current directory (.)")
        print("  2. Specific directory/directories")
        print("  3. Specific files")

        paths: List[str] = []
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
            ext = ext.strip().rstrip(',')
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.append(ext)

        if not extensions:
            print(f"{EMOJI['warning']}  No extensions selected, using .py as default")
            extensions = [".py"]
        return extensions

    def _configure_exclusions(self) -> List[str]:
        """
        Configure exclusion patterns.

        FIX: previously the wizard merged DEFAULT_EXCLUDE_PATTERNS here, but
        AssemblerConfig also added them again (use_default_excludes defaults to
        True), causing double-inclusion. The wizard now owns the full list and
        signals AssemblerConfig to skip its own merge (use_default_excludes=False
        is set in run()).
        """
        self._print_section("Step 3: Configure Exclusions")
        print("\nDefault exclusions:")
        print(f"  {', '.join(DEFAULT_EXCLUDE_PATTERNS[:10])}")
        if len(DEFAULT_EXCLUDE_PATTERNS) > 10:
            print(f"  ... and {len(DEFAULT_EXCLUDE_PATTERNS) - 10} more")

        use_defaults = self._ask_yes_no("\nUse default exclusions?", default=True)

        custom_patterns: List[str] = []
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
        return custom_patterns

    def _configure_output(self) -> str:
        self._print_section("Step 4: Output Configuration")
        output = self._ask_text("\nOutput filename", default="codebase.md")
        if not output.endswith('.md'):
            output += '.md'

        if os.path.exists(output):
            if not self._ask_yes_no(
                f"{EMOJI['warning']}  '{output}' already exists. Overwrite?", default=False
            ):
                counter = 1
                while os.path.exists(f"codebase_{counter}.md"):
                    counter += 1
                output = f"codebase_{counter}.md"
                print(f"{EMOJI['success']} Using: {output}")
        return output

    def _configure_advanced(self) -> Dict[str, Any]:
        self._print_section("Step 5: Advanced Options")
        advanced: Dict[str, Any] = {}

        if self._ask_yes_no("\nConfigure advanced options?", default=False):
            advanced['recursive'] = self._ask_yes_no(
                "  Recursively traverse subdirectories?", default=True
            )
            advanced['include_readmes'] = self._ask_yes_no(
                "  Automatically include README files?", default=True
            )
            print("\n  File size handling:")
            advanced['max_file_size_mb'] = self._ask_number(
                "    Maximum file size (MB)", default=10.0, min_val=0.1
            )
            advanced['truncate_large_files'] = self._ask_yes_no(
                "    Truncate large files instead of skipping?", default=True
            )
            if advanced['truncate_large_files']:
                advanced['truncation_limit_lines'] = int(self._ask_number(
                    "      Keep first N lines when truncating", default=500, min_val=10
                ))
        else:
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
            patterns = self.config['exclude_patterns']
            print(f"\n{EMOJI['error']} Exclusions: {len(patterns)} patterns")
            for pattern in patterns[:5]:
                print(f"   - {pattern}")
            if len(patterns) > 5:
                print(f"   ... and {len(patterns) - 5} more")

    def _save_config(self):
        if self._ask_yes_no(
            f"\n{EMOJI['floppy']} Save this configuration for future use?", default=False
        ):
            import json
            config_name = self._ask_text("Configuration filename", default="assembler_config.json")
            if not config_name.endswith('.json'):
                config_name += '.json'

            save_config = {k: v for k, v in self.config.items() if k != 'show_progress'}
            with open(config_name, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=2, ensure_ascii=False)

            print(f"{EMOJI['success']} Configuration saved to: {config_name}")
            print(f"   Reuse it with: code-assembler --config {config_name}")

    def run(self) -> Optional[str]:
        """Run the interactive wizard."""
        try:
            self._print_banner()

            self.config['paths'] = self._select_paths()
            self.config['extensions'] = self._select_extensions()

            exclude_patterns = self._configure_exclusions()
            self.config['exclude_patterns'] = exclude_patterns
            # FIX: wizard manages the full exclusion list itself (with or without
            # defaults). Tell AssemblerConfig not to add DEFAULT_EXCLUDE_PATTERNS
            # a second time, which would cause silent duplication.
            self.config['use_default_excludes'] = False

            self.config['output'] = self._configure_output()

            advanced = self._configure_advanced()
            self.config.update(advanced)

            self._show_summary()

            if not self._ask_yes_no(f"\n{EMOJI['rocket']} Start assembly?", default=True):
                print(f"\n{EMOJI['error']} Assembly cancelled.")
                return None

            self._save_config()

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
    """Entry point for interactive mode."""
    wizard = InteractiveWizard()
    wizard.run()


if __name__ == "__main__":
    run_interactive_mode()