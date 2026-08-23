"""
Reproduction of a self-referential ("dogfooding") bug: `_extract_metadata`
used to take the FIRST regex match in the document instead of the last.
`core.py` always appends the real metadata block after all file content,
so it is structurally guaranteed to be the *last* match — but any file
whose own prose describes this exact feature (a CHANGELOG entry, a README
section) and writes out `<!-- CODE_ASSEMBLER_METADATA ... -->` as a
literal example creates an earlier, non-JSON decoy match. Taking the
first match instead of the last then captures garbage between the decoy
and the next unrelated `-->` in the document, fails to parse as JSON, and
reports "no metadata found" even though a valid block exists at the real
end of the file.

Discovered by running code-assembler on its own source tree, where
CHANGELOG.md documents this exact mechanism in prose.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.rebuilder import CodebaseRebuilder


class TestMetadataBlockIsTheLastMatch(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.output_dir = self.root / "restored"
        self.md_file = self.root / "snapshot.md"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_prose_example_of_the_metadata_comment_is_not_mistaken_for_the_real_block(self):
        """
        A documentation file describing the hidden-metadata feature in
        prose — e.g. "Injects a hidden JSON block
        (`<!-- CODE_ASSEMBLER_METADATA ... -->`) at the end of generated
        files." — must not be mistaken for the real block. Only the
        genuine one, at the true end of the document, should be used.
        """
        real_metadata = {
            "version": "4.6.0",
            "generated_at": "2026-01-01 10:00:00",
            "files": {"docs/CHANGELOG.md": "2026-01-01 10:00"},
        }
        raw = (
            "# Consolidated Codebase\n\n"
            "### `docs/CHANGELOG.md`\n\n"
            "```markdown\n"
            "## Features\n\n"
            "- Injects a hidden JSON block "
            "(`<!-- CODE_ASSEMBLER_METADATA ... -->`) at the end of "
            "generated files, for reliable rebuild and delta operations.\n"
            "```\n"
        )
        full = raw + f"\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(real_metadata)}\n-->\n"
        self.md_file.write_text(full, encoding='utf-8')

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        found = rebuilder._extract_metadata()

        self.assertTrue(found, "The real metadata block must still be found")
        self.assertEqual(rebuilder.metadata["version"], "4.6.0")
        self.assertEqual(
            rebuilder.metadata["files"], {"docs/CHANGELOG.md": "2026-01-01 10:00"}
        )

    def test_full_rebuild_succeeds_despite_prose_decoy(self):
        """End-to-end: rebuild() must not report 'no valid metadata found'."""
        content = (
            "### `docs/CHANGELOG.md`\n\n"
            "```markdown\n"
            "Stores a hidden manifest "
            "(`<!-- CODE_ASSEMBLER_METADATA ... -->`) for rebuild.\n"
            "```\n\n"
            "### `pkg/main.py`\n\n"
            "```python\n"
            "print('real file')\n"
            "```\n"
        )
        metadata = {
            "version": "4.6.0",
            "generated_at": "2026-01-01 10:00:00",
            "files": {
                "docs/CHANGELOG.md": "2026-01-01 10:00",
                "pkg/main.py": "2026-01-01 10:00",
            },
        }
        full = content + f"\n<!-- CODE_ASSEMBLER_METADATA\n{json.dumps(metadata)}\n-->\n"
        self.md_file.write_text(full, encoding='utf-8')

        rebuilder = CodebaseRebuilder(str(self.md_file), str(self.output_dir))
        count, errors = rebuilder.rebuild()

        self.assertEqual(errors, [])
        self.assertEqual(count, 2)
        self.assertEqual(
            (self.output_dir / "pkg/main.py").read_text().strip(),
            "print('real file')"
        )


if __name__ == "__main__":
    unittest.main()
