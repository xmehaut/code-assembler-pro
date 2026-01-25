"""
Markdown formatters for Code Assembler Pro using Jinja2 templates.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader

from .config import FileEntry, CodebaseStats, AssemblerConfig
from .constants import LANGUAGE_MAP, EMOJI, __version__
from .utils import slugify_path, format_file_size, format_number


class MarkdownFormatter:
    """Handles formatting of content into Markdown using Jinja2."""

    def __init__(self):
        """Initialize Jinja2 environment."""
        template_dir = Path(__file__).parent / "templates"

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        self.env.globals.update({
            "format_number": format_number,
            "format_file_size": format_file_size,
            "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": __version__,
            "emoji": EMOJI
        })

    def render(self, template_name: str, data: Dict[str, Any]) -> str:
        """Helper to render a template with data."""
        template = self.env.get_template(template_name)
        return template.render(**data)

    def format_file_block(
            self,
            file_path: str,
            content: str,
            depth: int = 0,
            size_bytes: int = 0,
            line_count: int = 0
    ) -> str:
        """Format a file's content using the file_block template."""
        ext = Path(file_path).suffix
        data = {
            "header_level": "#" * (2 + depth),
            "filename": Path(file_path).name,
            "anchor": slugify_path(file_path),
            "path": file_path,
            "size": format_file_size(size_bytes),
            "lines": format_number(line_count),
            "lang": LANGUAGE_MAP.get(ext, "text"),
            "content": content
        }
        return self.render("components/file_block.md.j2", data)

    def format_directory_header(self, dir_path: str, depth: int = 0) -> str:
        """Format a directory header."""
        header_level = "#" * (1 + depth)
        anchor = slugify_path(dir_path)
        dirname = Path(dir_path).name
        return f'{header_level} {EMOJI["folder"]} {dirname}<a name="{anchor}"></a>\n\n'

    def format_readme_context(self, readme_content: str, depth: int = 0) -> str:
        """Format README content using the readme_context template."""
        data = {
            "header_level": "#" * (1 + depth),
            "content": readme_content
        }
        return self.render("components/readme_context.md.j2", data)

    def generate_toc(self, entries: List[FileEntry]) -> str:
        """Generate table of contents using the toc template."""
        toc_data = []
        for e in entries:
            toc_data.append({
                "depth": e.depth,
                "is_directory": e.is_directory,
                "is_file": e.is_file,
                "name": e.name,
                "anchor": slugify_path(e.path),
                "size": format_file_size(e.size_bytes) if e.is_file else "",
                "lines": format_number(e.line_count) if e.is_file else ""
            })

        return self.render("components/toc.md.j2", {"entries": toc_data})

    def generate_stats_table(self, stats: CodebaseStats, config: AssemblerConfig) -> str:
        """Generate statistics table using the stats_table template."""
        largest_file_name = "N/A"
        largest_file_size = "N/A"

        if stats.largest_file:
            largest_file_name = Path(stats.largest_file[0]).name
            largest_file_size = format_file_size(stats.largest_file[1])

        # Clean extensions for display
        clean_extensions = sorted(list(set(
            ext.replace('*', '').lstrip('.') for ext in config.extensions
        )))

        data = {
            "total_files": format_number(stats.total_files),
            "total_lines": format_number(stats.total_lines),
            "total_chars": format_number(stats.total_chars),
            "estimated_tokens": format_number(stats.estimated_tokens),
            "extensions": clean_extensions,
            "largest_file_name": largest_file_name,
            "largest_file_size": largest_file_size,
            "max_depth": stats.max_depth,
            "paths": config.paths,
            "exclude_patterns": config.exclude_patterns[:10],
            "skipped_count": len(stats.skipped_files)
        }
        return self.render("components/stats_table.md.j2", data)

    def generate_header(self, stats: CodebaseStats, config: AssemblerConfig, toc: str, arch_md: str) -> str:
        """Generate complete document header using the main_header template."""
        data = {
            "now_short": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "toc": toc,
            "architecture": arch_md,
            "total_files": format_number(stats.total_files),
            "estimated_tokens": format_number(stats.estimated_tokens),
            "skipped_count": len(stats.skipped_files),
            "stats_table": self.generate_stats_table(stats, config)
        }
        return self.render("main_header.md.j2", data)