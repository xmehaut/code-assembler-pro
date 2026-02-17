"""
Command Line Interface (CLI) for Code Assembler Pro.

This module serves as the main entry point for the application. It handles
argument parsing and dispatches execution to the appropriate engine:
1. Assembly Engine: Consolidates code into Markdown (Direct or Config mode).
2. Rebuild Engine: Reconstructs a project from a Markdown snapshot.
3. Interactive Engine: Guided wizard for configuration.

New in v4.4.0:
    - --rebuild: Restore project structure from a .md file.
    - --clip: Direct copy to system clipboard.
    - --since: Incremental updates based on previous snapshots.
"""

import argparse
import json
import sys
from typing import List, Optional

from .constants import (
    __version__,
    DEFAULT_MAX_FILE_SIZE_MB,
    EMOJI
)
from .core import assemble_codebase, assemble_from_config


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Consolidate a codebase into a single Markdown file for LLM analysis or rebuild it."
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # --- Execution Modes ---
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive wizard")
    parser.add_argument("--config", "-c", type=str, help="Path to a JSON configuration file")

    # --- Rebuild Mode ---
    rebuild_group = parser.add_argument_group("Rebuild Mode")
    rebuild_group.add_argument("--rebuild", type=str, metavar="MD_FILE", help="Reconstruct project")
    rebuild_group.add_argument("--output-dir", type=str, default="./rebuilt_project", help="Target directory")
    rebuild_group.add_argument("--dry-run", action="store_true", help="Preview rebuild")

    # --- Utility Flags ---
    parser.add_argument("--show-excludes", action="store_true", help="Show default exclusions")
    parser.add_argument("--save-config", type=str, metavar="FILE", help="Save CLI args to JSON")
    parser.add_argument("--clip", "-k", action="store_true", help="Copy to clipboard")

    # --- Main Arguments ---
    parser.add_argument("paths", nargs="*", help="Files or directories to analyze")
    parser.add_argument("--ext", "-e", dest="extensions", nargs="+", help="Extensions to include")
    parser.add_argument("--output", "-o", default="codebase.md", help="Output filename")
    parser.add_argument("--exclude", "-x", dest="exclude_patterns", nargs="+", help="Extra exclusions")

    # --- Flags ---
    parser.add_argument("--no-recursive", action="store_false", dest="recursive", help="Disable recursion")
    parser.add_argument("--no-readmes", action="store_false", dest="include_readmes", help="Disable READMEs")
    parser.add_argument("--no-default-excludes", action="store_false", dest="use_default_excludes",
                        help="Disable defaults")
    parser.add_argument("--max-size", type=float, default=DEFAULT_MAX_FILE_SIZE_MB, help="Max size in MB")
    parser.add_argument("--since", "-s", type=str, metavar="SNAPSHOT", help="Delta mode")

    parser.set_defaults(recursive=True, include_readmes=True, use_default_excludes=True)
    return parser.parse_args()


def _save_config(args: argparse.Namespace, extensions: List[str]):
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


def main():
    """Main entry point."""
    args = parse_args()
    content: Optional[str] = None

    try:
        if args.show_excludes:
            from .cli import _show_excludes
            _show_excludes()
            return

        if args.interactive:
            from .interactive import run_interactive_mode
            run_interactive_mode()
            return

        if args.rebuild:
            from .rebuilder import CodebaseRebuilder
            rebuilder = CodebaseRebuilder(args.rebuild, args.output_dir, args.dry_run)
            count, errors = rebuilder.rebuild()
            return

        if args.config:
            # FIX: Removed args.show_progress check
            content = assemble_from_config(args.config, since=args.since)
        else:
            if not args.paths or not args.extensions:
                print(f"{EMOJI['error']} Error: Paths and extensions are required.")
                sys.exit(1)

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

        if args.clip and content:
            from .utils import copy_to_clipboard
            if copy_to_clipboard(content):
                print(f"{EMOJI['clipboard']} Content copied to clipboard!")

    except Exception as e:
        print(f"\n{EMOJI['error']} An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
