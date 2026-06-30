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

    def _find_real_file_headers(self) -> List[Tuple[str, int, int]]:
        """
        Scan the whole document once for genuine file-header blocks:
        a '#+ `path`' line immediately followed (at most one blank line
        between) by an opening code fence.

        That tight anchoring — no free-form text allowed between the
        header and the fence — is what filters out prose headings that
        merely *wrap* an identifier in backticks (e.g. "#### `@Contract.
        validate` and `self` in tests"), since those are followed by
        ordinary paragraph text, not directly by a fence. It deliberately
        does NOT require `path` to be a key in the embedded metadata: some
        real header blocks are directory-level README context sections
        (e.g. "#### `behavioral/`" → "##### README context") rather than
        individual files, and excluding them would make this scan skip
        over a real document boundary, silently swallowing the README
        section into whatever file happens to precede it.

        Returns a list of (path, header_start, content_start) ordered by
        position in the document. Used both to locate a specific file's
        content and to bound where each block ends (the next entry's start
        is the bound for the previous one).
        """
        header_re = re.compile(
            r'#+ `([^`]+)`[ \t]*\r?\n(?:[ \t]*\r?\n)?```[a-z0-9]*\r?\n',
            re.IGNORECASE
        )
        return [
            (m.group(1).strip().replace('\\', '/'), m.start(), m.end())
            for m in header_re.finditer(self.md_content)
        ]

    def _extract_file_content(self, rel_path: str) -> Optional[str]:
        """
        Find and extract the content of a specific file from the Markdown.
        Robust against path separators, blank lines, duplicate filenames at
        different paths, and nested ``` fences inside the file's own content
        (a markdown file documenting code blocks, a README showing
        examples, etc. — see `_find_real_file_headers` for why a single
        validated scan is used instead of a per-call regex search).
        """
        target_normalized = rel_path.replace('\\', '/').strip()
        headers = self._find_real_file_headers()

        match_index = next(
            (i for i, (path, _, _) in enumerate(headers) if path == target_normalized),
            None
        )
        if match_index is None:
            return None

        _, _, content_start = headers[match_index]
        content_end_bound = (
            headers[match_index + 1][1] if match_index + 1 < len(headers) else len(self.md_content)
        )
        search_zone = self.md_content[content_start:content_end_bound]

        # True closing fence = the LAST bare ``` line in the window, since
        # earlier ones may be nested fences belonging to the file's own
        # content rather than the block's real terminator.
        closing_candidates = list(re.finditer(r'\r?\n```[ \t]*(?:\r?\n|$)', search_zone))
        if not closing_candidates:
            return None

        last_closing = closing_candidates[-1]
        return search_zone[:last_closing.start()]

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