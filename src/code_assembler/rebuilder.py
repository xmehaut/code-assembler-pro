"""
Rebuilder module for Code Assembler Pro.

This module reconstructs a project's directory structure and file contents
from a generated Markdown snapshot, using the embedded JSON metadata.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CodebaseRebuilder:
    """Handles the reconstruction of files from a Markdown codebase."""

    def __init__(self, md_path: str, output_dir: str, dry_run: bool = False):
        self.md_path = Path(md_path)
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.metadata: Dict = {}
        self.md_content: str = ""

    def _extract_metadata(self) -> bool:
        """Extract the hidden JSON metadata from the Markdown file."""
        if not self.md_path.exists():
            return False

        self.md_content = self.md_path.read_text(encoding='utf-8')
        pattern = re.compile(r'<!-- CODE_ASSEMBLER_METADATA\s+(.*?)\s+-->', re.DOTALL)
        match = pattern.search(self.md_content)

        if not match:
            return False

        try:
            self.metadata = json.loads(match.group(1))
            return True
        except json.JSONDecodeError:
            return False

    def _extract_file_content(self, rel_path: str) -> Optional[str]:
        """
        Find and extract the content of a specific file from the Markdown.
        It looks for the file header and captures the following code block.
        """
        # Escape path for regex
        escaped_path = re.escape(rel_path)

        # Pattern to find the file header and the code block that follows
        # It looks for: # `path` followed by any headers, then ```lang\n(content)\n```
        pattern = re.compile(
            rf'#+ `.*?{escaped_path}`.*?\n```[a-z0-9]*\n(.*?)\n```',
            re.DOTALL | re.IGNORECASE
        )

        match = pattern.search(self.md_content)
        return match.group(1) if match else None

    def rebuild(self) -> Tuple[int, List[str]]:
        """
        Execute the reconstruction process.

        Returns:
            Tuple[int, List[str]]: (number of files created, list of errors)
        """
        if not self._extract_metadata():
            return 0, ["No valid metadata found in the Markdown file. Rebuild impossible."]

        files_to_rebuild = self.metadata.get("files", {})
        created_count = 0
        errors = []

        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        for rel_path in files_to_rebuild:
            content = self._extract_file_content(rel_path)

            if content is None:
                errors.append(f"Content not found for: {rel_path}")
                continue

            # Security: Prevent path traversal
            if ".." in rel_path or rel_path.startswith("/") or rel_path.startswith("\\"):
                errors.append(f"Security skip (invalid path): {rel_path}")
                continue

            target_path = self.output_dir / rel_path

            if self.dry_run:
                print(f"[DRY-RUN] Would create: {target_path}")
                created_count += 1
                continue

            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content, encoding='utf-8')

                # Check for truncation warning
                if "[TRUNCATED]" in content:
                    errors.append(f"Warning: {rel_path} was truncated in the source MD.")

                created_count += 1
            except Exception as e:
                errors.append(f"Failed to write {rel_path}: {str(e)}")

        return created_count, errors
