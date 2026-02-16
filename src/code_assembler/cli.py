"""
Command Line Interface for Code Assembler Pro.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .core import assemble_codebase, assemble_from_config
from .constants import __version__, DEFAULT_MAX_FILE_SIZE_MB, DEFAULT_EXCLUDE_PATTERNS, EMOJI


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

    # Utility flags
    parser.add_argument(
        "--show-excludes",
        action="store_true",
        help="Show default exclusion patterns and exit"
    )

    parser.add_argument(
        "--save-config",
        type=str,
        metavar="FILE",
        help="Save the CLI arguments as a reusable JSON config file"
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
        help="Extensions and filenames to include (e.g., py md json Dockerfile)"
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

    parser.add_argument(
        "--since", "-s",
        type=str,
        metavar="SNAPSHOT",
        help="Only include files modified since the given .md snapshot (e.g. viewer.md)"
    )

    # Set defaults for flags
    parser.set_defaults(
        recursive=True,
        include_readmes=True,
        use_default_excludes=True
    )

    return parser.parse_args()


def _show_excludes():
    """Display default exclusion patterns."""
    print(f"\n{EMOJI['target']} Default exclusion patterns ({len(DEFAULT_EXCLUDE_PATTERNS)}):\n")
    for pattern in sorted(DEFAULT_EXCLUDE_PATTERNS):
        print(f"  - {pattern}")
    print(f"\nUse --no-default-excludes to disable these.")
    print(f"Use --exclude / -x to add custom patterns on top.\n")


def _save_config(args, extensions):
    """Save CLI arguments as a JSON config file."""
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

    with open(args.save_config, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"{EMOJI['success']} Configuration saved to: {args.save_config}")
    print(f"   Reuse with: code-assembler --config {args.save_config}\n")


def main():
    args = parse_args()

    try:
        # Show excludes and exit
        if args.show_excludes:
            _show_excludes()
            return

        # Interactive mode
        if args.interactive:
            from .interactive import run_interactive_mode
            run_interactive_mode()
            return

        # JSON Configuration Mode
        if args.config:
            print(f"Loading configuration from: {args.config}")
            assemble_from_config(args.config, since=args.since)  # ← nouveau
            return

        # CLI Arguments Mode
        if not args.paths:
            print("Error: No path specified.")
            print("Usage: code-assembler path/to/code --ext py js")
            print("\nUseful options:")
            print("  --interactive / -i     Launch the interactive wizard")
            print("  --show-excludes        Show default exclusion patterns")
            print("  --save-config FILE     Save current CLI args as JSON config")
            sys.exit(1)

        if not args.extensions:
            print("Error: No extensions specified.")
            print("Use --ext or -e (e.g., --ext py md Dockerfile)")
            sys.exit(1)

        # Keep raw extensions (don't force dot prefix — config.py handles separation)
        extensions = args.extensions

        # Save config if requested
        if args.save_config:
            _save_config(args, extensions)

        assemble_codebase(
            paths=args.paths,
            extensions=extensions,
            exclude_patterns=args.exclude_patterns,
            output=args.output,
            recursive=args.recursive,
            include_readmes=args.include_readmes,
            max_file_size_mb=args.max_size,
            use_default_excludes=args.use_default_excludes,
            since=args.since,  # ← nouveau
        )

    except Exception as e:
        print(f"\n{EMOJI['error']} An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
