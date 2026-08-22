"""
Standalone reproduction of the known limitation documented in CHANGELOG.md
[4.5.2]:

    "A handful of edge cases (~7 files across one large monorepo snapshot)
    still over-capture when a file's content block is immediately followed
    by a directory-level 'README context' section rather than another file
    header — not yet root-caused, left for a follow-up pass."

Root cause: `_find_real_file_headers()` only recognizes a boundary when a
`#+ \\`path\\`` heading is *immediately* followed by an opening fence. The
`readme_context.md.j2` template emits `### README context` (no backticks,
no immediate fence — a blank line and prose follow instead), so this
heading is never counted as a boundary. If that untracked section itself
contains a nested ``` example, its closing fence becomes the new "last
bare fence" within the *preceding* file's search window, and
`_extract_file_content` swallows everything from the preceding file's real
end, through the README-context section, up to that nested example's
close.

This mirrors the exact structure that triggered it on a real snapshot:
a Python file, immediately followed by an (untracked) directory README
context section whose own prose includes a fenced shell example, followed
eventually by the next real file.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.rebuilder import CodebaseRebuilder


class TestReadmeContextIsABoundary(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.output_dir = self.root / "restored"
        self.md_file = self.root / "snapshot.md"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _write(self, raw_markdown: str, files: dict):
        metadata = {
            "version": "4.5.2",
            "generated_at": "2026-01-01 10:00:00",
            "files": files,
        }
        full = raw_markdown + f"\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(metadata)}\n-->\n"
        self.md_file.write_text(full, encoding='utf-8')

    def test_readme_context_section_with_nested_fence_is_not_absorbed(self):
        """
        A file immediately followed by an (untracked) directory-level
        'README context' section — itself containing a nested fenced
        example — must stop at its own real closing fence. The README
        section must not be merged into the preceding file, and the
        next real file must still resolve to its own content.
        """
        raw = (
            "# Consolidated Codebase\n\n"
            "## Table of Contents\n\n"
            "- `pkg/module.py` | 2026-01-01 10:00\n"
            "- `pkg/sub/next.py` | 2026-01-01 10:00\n\n"
            "---\n\n"
            "### `pkg/module.py`\n\n"
            "```python\n"
            "def real_function():\n"
            "    return 42\n"
            "```\n\n"
            "## `pkg/sub/`\n\n"
            "### README context\n\n"
            "# Sub-package\n\n"
            "Alias short-hand, install via:\n\n"
            "```bash\n"
            "pip install pkg-sub\n"
            "```\n\n"
            "---\n\n"
            "### `pkg/sub/next.py`\n\n"
            "```python\n"
            "print(\"real next file\")\n"
            "```\n"
        )
        self._write(raw, {
            "pkg/module.py": "2026-01-01 10:00",
            "pkg/sub/next.py": "2026-01-01 10:00",
        })

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

        module_content = (self.output_dir / "pkg/module.py").read_text()
        # The bug: module.py absorbs the README section and the nested
        # "pip install pkg-sub" example, becoming invalid Python.
        self.assertNotIn("README", module_content)
        self.assertNotIn("pip install", module_content)
        self.assertEqual(
            module_content.strip(),
            "def real_function():\n    return 42"
        )

        next_content = (self.output_dir / "pkg/sub/next.py").read_text()
        self.assertEqual(next_content.strip(), 'print("real next file")')


if __name__ == "__main__":
    unittest.main()
