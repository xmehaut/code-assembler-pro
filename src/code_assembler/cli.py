"""
Command Line Interface (CLI) for Code Assembler Pro.

This module handles the command-line argument parsing and orchestrates the
different execution modes:
1. Interactive Mode: A guided wizard for configuration.
2. Configuration Mode: Loading settings from a JSON file.
3. Direct Mode: Using CLI arguments to define paths, extensions, and filters.

New features in v4.4.0 include Delta Mode (--since) for incremental updates
and Clipboard support (--clip) for direct ingestion into LLMs.
"""

import argparse
import json
import sys
import platform 
from typing import List, Optional

from .core import assemble_codebase, assemble_from_config
from .constants import (
    __version__,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_EXCLUDE_PATTERNS,
    EMOJI
)


def parse_args() -> argparse.Namespace:
    """
    Parse and return command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Consolidate a codebase into a single Markdown file for LLM analysis."
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    # --- Execution Modes ---
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Launch the interactive configuration wizard"
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to a JSON configuration file"
    )

    # --- Utility Flags ---
    parser.add_argument(
        "--show-excludes",
        action="store_true",
        help="Display default exclusion patterns and exit"
    )

    parser.add_argument(
        "--save-config",
        type=str,
        metavar="FILE",
        help="Save current CLI arguments as a reusable JSON configuration file"
    )

    parser.add_argument(
        "--clip", "-k",
        action="store_true",
        help="Copy the generated Markdown content directly to the system clipboard"
    )

    # --- Main Assembly Arguments ---
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to analyze"
    )

    parser.add_argument(
        "--ext", "-e",
        dest="extensions",
        nargs="+",
        help="Extensions and filenames to include (e.g., py js json Dockerfile)"
    )

    parser.add_argument(
        "--output", "-o",
        default="codebase.md",
        help="Output Markdown filename (default: codebase.md)"
    )

    parser.add_argument(
        "--exclude", "-x",
        dest="exclude_patterns",
        nargs="+",
        help="Additional patterns to exclude (added to defaults)"
    )

    # --- Filtering & Behavior Flags ---
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Disable recursive directory traversal"
    )

    parser.add_argument(
        "--no-readmes",
        action="store_false",
        dest="include_readmes",
        help="Do not automatically include README files for context"
    )

    parser.add_argument(
        "--no-default-excludes",
        action="store_false",
        dest="use_default_excludes",
        help="Disable the built-in default exclusion list"
    )

    parser.add_argument(
        "--max-size",
        type=float,
        default=DEFAULT_MAX_FILE_SIZE_MB,
        help=f"Maximum file size in MB before truncation (default: {DEFAULT_MAX_FILE_SIZE_MB})"
    )

    parser.add_argument(
        "--since", "-s",
        type=str,
        metavar="SNAPSHOT",
        help="Delta Mode: Only include files changed since the provided .md snapshot"
    )

    # Set defaults for boolean flags
    parser.set_defaults(
        recursive=True,
        include_readmes=True,
        use_default_excludes=True
    )

    return parser.parse_args()


def _show_excludes():
    """Display the list of default exclusion patterns to the console."""
    print(f"\n{EMOJI['target']} Default exclusion patterns ({len(DEFAULT_EXCLUDE_PATTERNS)}):\n")
    for pattern in sorted(DEFAULT_EXCLUDE_PATTERNS):
        print(f"  - {pattern}")
    print(f"\nUse --no-default-excludes to disable these.")
    print(f"Use --exclude / -x to add custom patterns on top.\n")


def _save_config(args: argparse.Namespace, extensions: List[str]):
    """
    Persist the current CLI arguments into a JSON configuration file.

    Args:
        args: The parsed CLI arguments.
        extensions: The list of extensions to save.
    """
    config = {
        "paths": args.paths,
        "extensions": extensions,
        "output": args.output,
        "recursive": args.recursive,
        "include_readmes": args.include_readmes,
        "max_file_size_mb": args.max_size,
        "use_default_excludes": args.use_default_excludes,
    }
    if args.exclude_patterns:
        config["exclude_patterns"] = args.exclude_patterns

    try:
        with open(args.save_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"{EMOJI['success']} Configuration saved to: {args.save_config}")
        print(f"   Reuse with: code-assembler --config {args.save_config}\n")
    except OSError as e:
        print(f"{EMOJI['error']} Failed to save configuration: {e}")


def main():
    """
    Main entry point for the Code Assembler Pro CLI.
    """
    args = parse_args()
    content: Optional[str] = None

    try:
        # 1. Utility: Show Excludes
        if args.show_excludes:
            _show_excludes()
            return

        # 2. Mode: Interactive Wizard
        if args.interactive:
            from .interactive import run_interactive_mode
            run_interactive_mode()
            return

        # 3. Mode: JSON Configuration
        if args.config:
            if args.show_progress:
                print(f"Loading configuration from: {args.config}")
            content = assemble_from_config(args.config, since=args.since)

        # 4. Mode: Direct CLI Arguments
        else:
            if not args.paths:
                print(f"{EMOJI['error']} Error: No path specified.")
                print("Usage: code-assembler path/to/code --ext py js")
                print("\nUseful options:")
                print("  --interactive / -i     Launch the interactive wizard")
                print("  --clip / -k            Copy result to clipboard")
                print("  --save-config FILE     Save current CLI args as JSON config")
                sys.exit(1)

            if not args.extensions:
                print(f"{EMOJI['error']} Error: No extensions specified.")
                print("Use --ext or -e (e.g., --ext py md Dockerfile)")
                sys.exit(1)

            # Save config if requested before running assembly
            if args.save_config:
                _save_config(args, args.extensions)

            content = assemble_codebase(
                paths=args.paths,
                extensions=args.extensions,
                exclude_patterns=args.exclude_patterns,
                output=args.output,
                recursive=args.recursive,
                include_readmes=args.include_readmes,
                max_file_size_mb=args.max_size,
                use_default_excludes=args.use_default_excludes,
                since=args.since,
            )

        # 5. Post-Processing: Clipboard Support
        if args.clip and content:
            from .utils import copy_to_clipboard
            if copy_to_clipboard(content):
                print(f"{EMOJI['clipboard']} Content successfully copied to clipboard!")
            else:
                msg = "Failed to copy to clipboard."
                if platform.system() == "Linux":
                    msg += " Ensure 'xclip' or 'xsel' is installed."
                print(f"{EMOJI['warning']} {msg}")

    except KeyboardInterrupt:
        print(f"\n{EMOJI['error']} Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{EMOJI['error']} An unexpected error occurred: {str(e)}")
        # Uncomment for debugging:
        # import traceback
        # traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()