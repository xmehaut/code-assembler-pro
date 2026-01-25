"""
Core assembly engine for Code Assembler Pro.

This module contains the main logic for traversing directories,
processing files, and assembling the final markdown output.
"""

import os
from pathlib import Path
from typing import List, Tuple

from .config import AssemblerConfig, FileEntry, CodebaseStats
from .file_io import read_file_content, read_file_head
from .analyzers import ArchitectureAnalyzer
from .formatters import MarkdownFormatter
from .utils import should_exclude, get_file_extension, count_lines, estimate_tokens
from .constants import README_FILENAMES, EMOJI


class CodebaseAssembler:
    """
    Main assembler class that orchestrates codebase consolidation.
    """

    def __init__(self, config: AssemblerConfig):
        """
        Initialize the assembler.

        Args:
            config: Configuration for the assembly process
        """
        self.config = config
        self.stats = CodebaseStats()
        self.toc_entries: List[FileEntry] = []
        self.content_buffer: List[str] = []
        self.formatter = MarkdownFormatter()

    def process_file(self, file_path: str, depth: int = 0) -> bool:
        """
        Process a single file and add its content to the buffer.
        Handles large files by truncating them if configured.
        """
        try:
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)

            content = ""
            is_truncated = False

            # Handle file size limit
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
                        print(f"  ✂️  Truncated (too large): {Path(file_path).name}")
                else:
                    reason = f"too large: {size_mb:.1f}MB"
                    self.stats.skip_file(file_path, reason)
                    if self.config.show_progress:
                        print(f"⚠️  Skipped (too large): {file_path}")
                    return False
            else:
                content = read_file_content(file_path)

        except OSError as e:
            self.stats.skip_file(file_path, f"system error: {e}")
            return False

        if content.startswith("[❌"):
            self.stats.skip_file(file_path, "read error")
            if self.config.show_progress:
                print(f"❌ Read error: {file_path}")
            return False

        line_count = count_lines(content)

        md_block = self.formatter.format_file_block(
            file_path=file_path,
            content=content,
            depth=depth,
            size_bytes=size_bytes,
            line_count=line_count
        )

        self.content_buffer.append(md_block)

        ext = get_file_extension(file_path)
        self.stats.add_file(ext, line_count, size_bytes)
        self.stats.update_largest_file(file_path, size_bytes)

        self.toc_entries.append(FileEntry(
            path=file_path,
            type='file',
            depth=depth,
            size_bytes=size_bytes,
            line_count=line_count
        ))

        if self.config.show_progress and not is_truncated:
            print(f"  ✅ {Path(file_path).name} ({line_count:,} lines)")

        return True

    def process_readme(self, dir_path: str, depth: int = 0) -> bool:
        """Process README file if it exists in the directory."""
        for readme_name in README_FILENAMES:
            readme_path = os.path.join(dir_path, readme_name)

            if os.path.exists(readme_path) and not should_exclude(
                    readme_path, self.config.exclude_patterns
            ):
                content = read_file_content(readme_path)

                if not content.startswith("[❌"):
                    md_block = self.formatter.format_readme_context(content, depth)
                    self.content_buffer.append(md_block)

                    if self.config.show_progress:
                        print(f"  ℹ️  README found: {readme_name}")

                    return True
        return False

    def process_directory(self, dir_path: str, depth: int = 0) -> None:
        """Process a directory recursively using Pathlib."""
        current_path = Path(dir_path)

        if should_exclude(str(current_path), self.config.exclude_patterns):
            if self.config.show_progress:
                print(f"⏭️  Excluded: {current_path}")
            return

        if self.config.show_progress:
            indent = "  " * depth
            print(f"{indent}📁 {current_path.name}")

        try:
            if self.config.include_readmes:
                self.process_readme(str(current_path), depth)

            items = sorted(current_path.iterdir(), key=lambda p: p.name.lower())

            for item in items:
                if should_exclude(str(item), self.config.exclude_patterns):
                    continue

                if item.is_file():
                    if any(item.name.endswith(ext) for ext in self.config.extensions):
                        self.process_file(str(item), depth)

                elif item.is_dir():
                    if self.config.recursive:
                        dir_header = self.formatter.format_directory_header(str(item), depth)
                        self.content_buffer.append(dir_header)

                        self.toc_entries.append(FileEntry(
                            path=str(item),
                            type='dir',
                            depth=depth
                        ))
                        self.process_directory(str(item), depth + 1)

        except PermissionError:
            if self.config.show_progress:
                print(f"❌ Permission denied: {current_path}")
            self.stats.skip_file(str(current_path), "permission denied")
        except Exception as e:
            if self.config.show_progress:
                print(f"❌ Error processing {current_path}: {e}")
            self.stats.skip_file(str(current_path), str(e))

    def assemble(self) -> str:
        """Assemble the complete codebase into markdown."""
        if self.config.show_progress:
            print(f"\n{EMOJI['rocket']} Starting assembly...\n")

        for path in self.config.paths:
            if not os.path.exists(path):
                if self.config.show_progress:
                    print(f"⚠️  Path does not exist: {path}")
                continue

            if self.config.show_progress:
                print(f"\n📂 Processing: {path}")

            if os.path.isfile(path):
                if any(path.endswith(ext) for ext in self.config.extensions):
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

        header = self.formatter.generate_header(
            self.stats, self.config, toc, architecture_md
        )

        final_content = header + "\n\n" + full_content

        if self.config.show_progress:
            self._print_summary()

        return final_content

    def _print_summary(self) -> None:
        """Print assembly summary."""
        from .utils import format_file_size, format_number

        print(f"\n{EMOJI['success']} Assembly completed!")
        print(f"\n📊 Summary:")
        print(f"   📄 Files: {format_number(self.stats.total_files)}")
        print(f"   📏 Lines: {format_number(self.stats.total_lines)}")
        print(f"   💾 Size: {format_file_size(self.stats.total_chars)}")
        print(f"   🎯 Tokens: ~{format_number(self.stats.estimated_tokens)}")

        if self.stats.estimated_tokens > 100000:
            print(f"\n⚠️  WARNING: High token volume (>100k).")
            print(f"    Check your model's context limit (GPT-4o: 128k, Claude: 200k).")

        if self.stats.skipped_files:
            print(f"\n⚠️  Skipped files: {len(self.stats.skipped_files)}")
            for skipped in self.stats.skipped_files[:5]:
                print(f"   - {skipped}")


def assemble_codebase(
        paths: List[str],
        extensions: List[str],
        exclude_patterns: List[str] = None,
        output: str = "codebase.md",
        **kwargs
) -> str:
    """Main function to assemble a codebase into markdown."""
    from .file_io import write_file_content

    if 'output_file' in kwargs:
        output = kwargs.pop('output_file')

    config = AssemblerConfig(
        paths=paths,
        extensions=extensions,
        exclude_patterns=exclude_patterns or [],
        output_file=output,
        **kwargs
    )

    assembler = CodebaseAssembler(config)
    content = assembler.assemble()

    success = write_file_content(output, content)

    if success and config.show_progress:
        print(f"\n{EMOJI['floppy']} Saved: {output}\n")

    return content


def assemble_from_config(config_file: str) -> str:
    """Assemble codebase from JSON configuration file."""
    import json
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return assemble_codebase(**config_data)