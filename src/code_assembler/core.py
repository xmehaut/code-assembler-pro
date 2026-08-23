"""
Core assembly engine for Code Assembler Pro.

This module orchestrates the traversal of directories, file processing,
and the final assembly of the Markdown document, including delta analysis
and metadata injection.
"""

import os
from pathlib import Path
from typing import List, Optional, Set, Dict

from .analyzers import ArchitectureAnalyzer
from .config import AssemblerConfig, FileEntry, CodebaseStats
from .constants import README_FILENAMES, EMOJI
from .file_io import read_file_content, read_file_head
from .formatters import MarkdownFormatter
from .utils import should_exclude, get_file_extension, count_lines, estimate_tokens


class CodebaseAssembler:
    """Main assembler class that orchestrates codebase consolidation."""

    def __init__(self, config: AssemblerConfig, since: Optional[str] = None):
        """
        Initialize the assembler.

        Args:
            config: Configuration for the assembly process.
            since: Path to a previous .md snapshot for delta analysis.
        """
        self.config = config
        self.since = since
        self.since_filter: Optional[Set[str]] = None
        self.deleted_files: Set[str] = set()
        self.stats = CodebaseStats()
        self.toc_entries: List[FileEntry] = []
        self.content_buffer: List[str] = []
        self.formatter = MarkdownFormatter()

        # Compression (v4.5) — initialised once so parsers load a single time
        self.compressor = None
        if config.compress:
            from .compressor import CodeCompressor
            self.compressor = CodeCompressor(config.extensions)

    def _collect_all_files(self) -> Set[str]:
        """Collect all candidate files without processing them."""
        result: Set[str] = set()
        for path in self.config.paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                if self._matches_file(Path(path)):
                    result.add(os.path.abspath(path))
            elif os.path.isdir(path):
                self._collect_dir(path, result)
        return result

    def _collect_dir(self, dir_path: str, result: Set[str]) -> None:
        """Recursively traverse a directory to collect file paths."""
        current = Path(dir_path)
        if should_exclude(str(current), self.config.exclude_patterns):
            return
        try:
            for item in sorted(current.iterdir(), key=lambda p: p.name.lower()):
                if should_exclude(str(item), self.config.exclude_patterns):
                    continue
                if item.is_file() and self._matches_file(item):
                    result.add(os.path.abspath(str(item)))
                elif item.is_dir() and self.config.recursive:
                    self._collect_dir(str(item), result)
        except PermissionError:
            pass

    def _matches_file(self, filepath: Path) -> bool:
        """Check if a file matches configured extensions or exact filenames."""
        name = filepath.name
        if any(name.endswith(ext) for ext in self.config.extensions):
            return True
        if name in self.config.exact_filenames:
            return True
        return False

    def process_file(self, file_path: str, depth: int = 0) -> bool:
        """
        Process a single file and add its content to the buffer.
        Handles large files by truncating them if configured.
        When compression is active, reduces content to signatures + docstrings.
        """
        if self.since_filter is not None and os.path.abspath(file_path) not in self.since_filter:
            return False

        try:
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            content = ""
            is_truncated = False

            if size_mb > self.config.max_file_size_mb:
                if self.config.truncate_large_files:
                    limit = self.config.truncation_limit_lines
                    content = read_file_head(file_path, limit)
                    content += (
                        f"\n\n# ... [TRUNCATED] ...\n"
                        f"# Content truncated because > {self.config.max_file_size_mb}MB.\n"
                        f"# Only the first {limit} lines are shown for context."
                    )
                    is_truncated = True
                    if self.config.show_progress:
                        print(f"  {EMOJI['warning']}  Truncated (too large): {Path(file_path).name}")
                else:
                    self.stats.skip_file(file_path, f"too large: {size_mb:.1f}MB")
                    return False
            else:
                content = read_file_content(file_path)

        except OSError as e:
            self.stats.skip_file(file_path, f"system error: {e}")
            return False

        if content.startswith("[ERROR]"):
            self.stats.skip_file(file_path, "read error")
            return False

        # Compression injection — skipped for truncated files to avoid double-mangling
        if self.compressor is not None and not is_truncated:
            content = self.compressor.compress(content, file_path)

        line_count = count_lines(content)
        md_block = self.formatter.format_file_block(
            file_path=file_path, content=content, depth=depth,
            size_bytes=size_bytes, line_count=line_count
        )

        self.content_buffer.append(md_block)
        self.stats.add_file(get_file_extension(file_path), line_count, size_bytes)
        self.stats.update_largest_file(file_path, size_bytes)
        self.toc_entries.append(FileEntry(
            path=file_path, type='file', depth=depth,
            size_bytes=size_bytes, line_count=line_count
        ))

        if self.config.show_progress and not is_truncated:
            compress_tag = " [compressed]" if self.compressor else ""
            print(f"  {EMOJI['success']} {Path(file_path).name} ({line_count:,} lines{compress_tag})")

        return True

    def process_readme(self, dir_path: str, depth: int = 0) -> bool:
        """Process README file if it exists in the directory for context."""
        for readme_name in README_FILENAMES:
            readme_path = os.path.join(dir_path, readme_name)
            if os.path.exists(readme_path) and not should_exclude(readme_path, self.config.exclude_patterns):
                content = read_file_content(readme_path)
                if not content.startswith("[ERROR]"):
                    self.content_buffer.append(self.formatter.format_readme_context(content, depth))
                    if self.config.show_progress:
                        print(f"  {EMOJI['readme']}  README found: {readme_name}")
                    return True
        return False

    def process_directory(self, dir_path: str, depth: int = 0) -> None:
        """Process a directory recursively."""
        current_path = Path(dir_path)
        if should_exclude(str(current_path), self.config.exclude_patterns):
            return

        if self.config.show_progress:
            print(f"{'  ' * depth}{EMOJI['folder']} {current_path.name}")

        try:
            if self.config.include_readmes:
                self.process_readme(str(current_path), depth)

            items = sorted(current_path.iterdir(), key=lambda p: p.name.lower())
            for item in items:
                if should_exclude(str(item), self.config.exclude_patterns):
                    continue
                if item.is_file() and self._matches_file(item):
                    self.process_file(str(item), depth)
                elif item.is_dir() and self.config.recursive:
                    self.content_buffer.append(self.formatter.format_directory_header(str(item), depth))
                    self.toc_entries.append(FileEntry(path=str(item), type='dir', depth=depth))
                    self.process_directory(str(item), depth + 1)
        except PermissionError:
            self.stats.skip_file(str(current_path), "permission denied")

    def assemble(self) -> str:
        """Assemble the complete codebase into a single Markdown string."""
        delta_summary = ""
        if self.since and os.path.exists(self.since):
            from .delta import filter_changed_files, get_delta, format_delta_summary
            all_files = self._collect_all_files()
            files_to_assemble, self.deleted_files = filter_changed_files(self.since, all_files)
            self.since_filter = files_to_assemble

            modified, added, deleted = get_delta(self.since, all_files)
            delta_summary = format_delta_summary(modified, added, deleted)

            if self.config.show_progress:
                print(f"\n{EMOJI['mag']} Delta mode: {len(files_to_assemble)} file(s) changed")

        if self.config.show_progress:
            compress_info = f" (compress={self.config.compress_level})" if self.config.compress else ""
            print(f"\n{EMOJI['rocket']} Starting assembly{compress_info}...\n")

        for path in self.config.paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                if self._matches_file(Path(path)):
                    self.process_file(path)
            elif os.path.isdir(path):
                self.process_directory(path)

        full_content = "".join(self.content_buffer)
        self.stats.total_chars = len(full_content)
        self.stats.estimated_tokens = estimate_tokens(full_content)

        toc = self.formatter.generate_toc(self.toc_entries)
        analyzer = ArchitectureAnalyzer(self.toc_entries, self.stats)
        archi_data = analyzer.analyze_data()
        architecture_md = self.formatter.render("components/architecture.md.j2", archi_data)

        header = self.formatter.generate_header(self.stats, self.config, toc, architecture_md)
        if delta_summary:
            header = header.replace("---", f"{delta_summary}\n\n---", 1)

        # Generated separately from generate_header() and prepended only
        # here, i.e. after the delta_summary substitution above: this
        # block starts and ends with its own "---" delimiters, and doing
        # the substitution first (on `header` alone) guarantees it can
        # never mistake the frontmatter's own "---" for the header's.
        frontmatter = self.formatter.generate_frontmatter(self.stats, description=self.config.description)

        metadata_block = self.formatter.generate_metadata_block(self.toc_entries)

        if self.config.show_progress:
            self._print_summary()

        return frontmatter + header + "\n\n" + full_content + metadata_block

    def _print_summary(self) -> None:
        """Print assembly summary to console."""
        from .utils import format_file_size, format_number
        print(f"\n{EMOJI['success']} Assembly completed!")
        print(f"\n{EMOJI['chart']} Summary:")
        print(f"   {EMOJI['file']} Files: {format_number(self.stats.total_files)}")
        print(f"   {EMOJI['mag']} Lines: {format_number(self.stats.total_lines)}")
        print(f"   {EMOJI['floppy']} Size: {format_file_size(self.stats.total_chars)}")
        print(f"   {EMOJI['target']} Tokens: ~{format_number(self.stats.estimated_tokens)}")
        if self.config.compress:
            print(f"   {EMOJI['recycle']} Compression: {self.config.compress_level}")


def assemble_codebase(
        paths: List[str],
        extensions: List[str],
        exclude_patterns: Optional[List[str]] = None,
        output: str = "codebase.md",
        since: Optional[str] = None,
        **kwargs
) -> str:
    """Main entry point function to assemble a codebase."""
    from .file_io import write_file_content

    if 'output_file' in kwargs:
        output = kwargs.pop('output_file')

    config = AssemblerConfig(
        paths=paths, extensions=extensions,
        exclude_patterns=exclude_patterns or [],
        output_file=output, **kwargs
    )

    assembler = CodebaseAssembler(config, since=since)
    content = assembler.assemble()

    if not write_file_content(output, content):
        raise OSError(f"Failed to write output file: {output}")

    if config.show_progress:
        print(f"\n{EMOJI['floppy']} Saved: {output}\n")

    return content


def assemble_modules(config_data: dict) -> Dict[str, Dict[str, str]]:
    """
    Batch-assemble every module declared under a "modules" key
    (MODULES_SPEC.md §2-4, §9-10).

    Single pass: `resolve_module_configs()` validates and resolves every
    module's effective config up front — nothing is written until every
    static error (bad root/module shape, missing extensions, a `/` in a
    module name) has already been ruled out. Assembly itself then runs
    per module; one module's runtime failure (bad path, permission error)
    is recorded and does NOT abort the batch — the remaining modules
    still get assembled, and the failure is reported back to the caller
    (§10 partial-failure policy).

    Returns a summary, not file content — there is no single string to
    hand back for N output files:
        {"succeeded": {module_name: output_path, ...},
         "failed":    {module_name: error_message, ...}}
    """
    from .config import resolve_module_configs

    resolved = resolve_module_configs(config_data)  # raises on any static error

    succeeded: Dict[str, str] = {}
    failed: Dict[str, str] = {}

    for name, module_config in resolved.items():
        module_config = dict(module_config)  # don't mutate the resolved dict
        try:
            paths = module_config.pop("paths")
            # assemble_codebase() itself does not raise on a missing path —
            # it silently walks nothing and produces a near-empty snapshot.
            # That's tolerable for a single, deliberate invocation, but
            # wrong for a batch: §10 explicitly names "bad path" as an
            # expected per-module failure, so it must actually surface as
            # one rather than silently succeed with 0 files.
            missing = [p for p in paths if not Path(p).exists()]
            if missing:
                raise FileNotFoundError(f"path(s) not found: {', '.join(missing)}")
            extensions = module_config.pop("extensions")
            exclude_patterns = module_config.pop("exclude_patterns", None)
            output = module_config.pop("output")
            assemble_codebase(
                paths=paths,
                extensions=extensions,
                exclude_patterns=exclude_patterns,
                output=output,
                **module_config,
            )
            succeeded[name] = output
        except Exception as e:
            failed[name] = str(e)

    return {"succeeded": succeeded, "failed": failed}


def assemble_from_config(
        config_file: str,
        since: Optional[str] = None,
        **cli_overrides
):
    """
    Assemble codebase using a JSON configuration file.

    CLI flags passed as keyword arguments take precedence over values
    in the JSON config file. This allows combining --config with flags
    like --compress without modifying the config file.

    Returns the assembled Markdown content (str) for a normal, single-
    output config. Returns a batch summary dict instead — see
    `assemble_modules()` — when the config contains a top-level "modules"
    key (MODULES_SPEC.md §2). Callers that need to tell the two apart
    (e.g. the CLI) should check `isinstance(result, dict)`.

    Example:
        assemble_from_config("config.json", since="prev.md", compress=True)
    """
    import json
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # Normalise output key
    if 'output_file' in config_data and 'output' not in config_data:
        config_data['output'] = config_data.pop('output_file')
    elif 'output_file' in config_data:
        config_data.pop('output_file')

    if "modules" in config_data:
        # §11: delta mode is not meaningful across a batch of N independent
        # snapshots — refuse explicitly rather than guessing which module
        # --since was meant for.
        if since is not None:
            raise ValueError(
                '--since is not supported with a "modules" config — run it '
                'against a single module\'s own output file instead'
            )
        # Same reasoning for CLI overrides (--compress, --description, …):
        # silently applying them to every module, or to none, would both be
        # guesses. A module that wants --compress declares "compress": true
        # itself (or inherits it from the config root, per §3).
        if cli_overrides:
            raise ValueError(
                f'CLI overrides ({", ".join(cli_overrides)}) are not supported '
                'with a "modules" config — set these keys in the JSON itself, '
                'at the root or per module'
            )
        return assemble_modules(config_data)

    # CLI overrides win over JSON values — only apply truthy/explicit values
    # so that a bare --compress=False doesn't accidentally disable JSON compress:true
    for key, value in cli_overrides.items():
        if value is not None:
            config_data[key] = value

    return assemble_codebase(since=since, **config_data)