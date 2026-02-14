"""
Command Line Interface for Code Assembler Pro.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .core import assemble_codebase, assemble_from_config
from .constants import __version__, DEFAULT_MAX_FILE_SIZE_MB


def parse_args():
    parser = argparse.ArgumentParser(
        description="Consolidate a codebase into a single Markdown file for LLM analysis."
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    # Interactive mode
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Launch interactive wizard mode"
    )

    # Config file mode
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to a JSON configuration file"
    )

    # Main arguments (used if --config is not present)
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to analyze"
    )

    parser.add_argument(
        "--ext", "-e",
        dest="extensions",
        nargs="+",
        help="Extensions to include (e.g., py md json)"
    )

    parser.add_argument(
        "--output", "-o",
        default="codebase.md",
        help="Output file name (default: codebase.md)"
    )

    parser.add_argument(
        "--exclude", "-x",
        dest="exclude_patterns",
        nargs="+",
        help="Patterns to exclude (added to defaults)"
    )

    # Boolean flags
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Do not traverse subdirectories recursively"
    )

    parser.add_argument(
        "--no-readmes",
        action="store_false",
        dest="include_readmes",
        help="Do not automatically include README files"
    )

    parser.add_argument(
        "--no-default-excludes",
        action="store_false",
        dest="use_default_excludes",
        help="Do not use the default exclusion list"
    )

    parser.add_argument(
        "--max-size",
        type=float,
        default=DEFAULT_MAX_FILE_SIZE_MB,
        help=f"Maximum file size in MB (default: {DEFAULT_MAX_FILE_SIZE_MB})"
    )

    # Set defaults for flags
    parser.set_defaults(
        recursive=True,
        include_readmes=True,
        use_default_excludes=True
    )

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        if args.interactive:
            # Interactive Wizard Mode
            from .interactive import run_interactive_mode
            run_interactive_mode()
            return
        elif args.config:
            # JSON Configuration Mode
            print(f"Loading configuration from: {args.config}")
            assemble_from_config(args.config)
        else:
            # CLI Arguments Mode
            if not args.paths:
                print("Error: No path specified.")
                print("Usage: code-assembler path/to/code --ext py js")
                sys.exit(1)

            if not args.extensions:
                print("Error: No extensions specified.")
                print("Use --ext or -e (e.g., --ext py md)")
                sys.exit(1)

            # Normalize extensions (add leading dot if missing)
            extensions = [
                e if e.startswith('.') else f'.{e}'
                for e in args.extensions
            ]

            assemble_codebase(
                paths=args.paths,
                extensions=extensions,
                exclude_patterns=args.exclude_patterns,
                output=args.output,
                recursive=args.recursive,
                include_readmes=args.include_readmes,
                max_file_size_mb=args.max_size,
                use_default_excludes=args.use_default_excludes
            )

    except Exception as e:
        print(f"\nâŒ An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()