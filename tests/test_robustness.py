"""
Robustness tests for Code Assembler Pro.

One test per bug fixed in the review — these are regression guards.
If any of these fail, a previously fixed bug has been reintroduced.

Bugs covered:
    [1] constants   — duplicate keys in LANGUAGE_MAP and EMOJI dicts
    [2] cli         — _show_excludes() missing → AttributeError
    [3] cli         — rebuild errors never displayed
    [4] config      — empty extension string → IndexError on ext[0]
    [5] analyzers   — os.path.commonpath crash on Windows multi-drive paths
    [6] delta       — bare except swallowing PermissionError and JSONDecodeError
    [7] utils       — Linux clipboard: xsel fallback only on FileNotFoundError
    [8] utils       — no timeout on subprocess → potential infinite hang
    [9] core        — write_file_content return value ignored → silent data loss
    [10] interactive — use_default_excludes double-application
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch, call

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# ---------------------------------------------------------------------------
# [1] constants — no duplicate keys
# ---------------------------------------------------------------------------

class TestConstantsNoDuplicates(unittest.TestCase):

    def test_language_map_no_duplicate_dot_properties(self):
        """'.properties' must appear exactly once in LANGUAGE_MAP."""
        from code_assembler.constants import LANGUAGE_MAP
        # Python dicts can't hold duplicate keys at runtime (last wins),
        # so we verify the value is what we expect and that the key exists.
        self.assertIn(".properties", LANGUAGE_MAP)
        self.assertEqual(LANGUAGE_MAP[".properties"], "properties")

    def test_language_map_no_duplicate_graphql(self):
        """'.graphql' and '.gql' must each map to 'graphql'."""
        from code_assembler.constants import LANGUAGE_MAP
        self.assertEqual(LANGUAGE_MAP[".graphql"], "graphql")
        self.assertEqual(LANGUAGE_MAP[".gql"], "graphql")

    def test_emoji_recycle_key_is_unique_and_correct(self):
        """
        'recycle' key must not be silently overwritten.
        The surviving value should be the recycling symbol ♻️ (u267b).
        """
        from code_assembler.constants import _EMOJI_ICONS, _ASCII_ICONS
        # Verify 'recycle' exists exactly once (Python dicts guarantee uniqueness
        # of keys, so if it was defined twice the count is still 1 — but we can
        # inspect the value to confirm the right one survived).
        self.assertIn("recycle", _EMOJI_ICONS)
        self.assertIn("recycle", _ASCII_ICONS)
        # The correct final value (not the overwritten 🔄)
        self.assertIn("\u267b", _EMOJI_ICONS["recycle"])  # ♻️
        # ASCII fallback should be a single predictable string, not "[R]" (overwritten)
        self.assertNotEqual(_ASCII_ICONS["recycle"], "[R]")

    def test_no_dead_header_levels_constant(self):
        """HEADER_LEVELS was dead code — it should no longer be exported."""
        import code_assembler.constants as c
        self.assertFalse(
            hasattr(c, "HEADER_LEVELS"),
            "HEADER_LEVELS is dead code and should have been removed"
        )


# ---------------------------------------------------------------------------
# [2] cli — _show_excludes must be callable without error
# ---------------------------------------------------------------------------

class TestCliShowExcludes(unittest.TestCase):

    def test_show_excludes_is_defined(self):
        """_show_excludes must exist in cli module (was missing → AttributeError)."""
        from code_assembler import cli
        self.assertTrue(
            callable(getattr(cli, "_show_excludes", None)),
            "_show_excludes is not defined in cli.py"
        )

    def test_show_excludes_prints_patterns(self):
        """_show_excludes must print at least some of the default patterns."""
        from code_assembler.cli import _show_excludes
        from code_assembler.constants import DEFAULT_EXCLUDE_PATTERNS

        with patch("sys.stdout", new=StringIO()) as fake_out:
            _show_excludes()
            output = fake_out.getvalue()

        # At least one default pattern should appear in the output
        self.assertTrue(
            any(p in output for p in DEFAULT_EXCLUDE_PATTERNS),
            "_show_excludes output doesn't mention any default exclusion pattern"
        )

    def test_main_show_excludes_does_not_crash(self):
        """--show-excludes via main() must not raise AttributeError."""
        from code_assembler.cli import main

        args = argparse.Namespace(
            show_excludes=True,
            interactive=False, config=None, rebuild=None,
            paths=[], extensions=None, output="codebase.md",
            exclude_patterns=None, recursive=True, include_readmes=True,
            use_default_excludes=True, max_size=10.0, since=None,
            clip=False, save_config=None, compress=False,
            compress_level="signatures",
        )
        with patch("code_assembler.cli.parse_args", return_value=args):
            with patch("sys.stdout", new=StringIO()):
                # Must not raise
                main()


# ---------------------------------------------------------------------------
# [3] cli — rebuild errors must be displayed
# ---------------------------------------------------------------------------

class TestCliRebuildErrorDisplay(unittest.TestCase):

    def test_rebuild_errors_are_printed(self):
        """Errors returned by rebuilder.rebuild() must be displayed to the user."""
        from code_assembler.cli import main

        args = argparse.Namespace(
            show_excludes=False, interactive=False, config=None,
            rebuild="fake.md", output_dir="./out", dry_run=False,
            paths=[], extensions=None, output="codebase.md",
            exclude_patterns=None, recursive=True, include_readmes=True,
            use_default_excludes=True, max_size=10.0, since=None,
            clip=False, save_config=None, compress=False,
            compress_level="signatures",
        )

        mock_rebuilder = MagicMock()
        mock_rebuilder.rebuild.return_value = (1, ["Content not found for: src/lost.py"])

        with patch("code_assembler.cli.parse_args", return_value=args):
            # FIX: CodebaseRebuilder is imported lazily inside main() so patch
            # the class in its source module, not in cli's namespace
            with patch("code_assembler.rebuilder.CodebaseRebuilder", return_value=mock_rebuilder):
                with patch("sys.stdout", new=StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()

        self.assertIn("lost.py", output, "Rebuild error was not printed to stdout")

    def test_rebuild_success_count_is_printed(self):
        """Successful rebuild should display file count."""
        from code_assembler.cli import main

        args = argparse.Namespace(
            show_excludes=False, interactive=False, config=None,
            rebuild="snap.md", output_dir="./restored", dry_run=False,
            paths=[], extensions=None, output="codebase.md",
            exclude_patterns=None, recursive=True, include_readmes=True,
            use_default_excludes=True, max_size=10.0, since=None,
            clip=False, save_config=None, compress=False,
            compress_level="signatures",
        )

        mock_rebuilder = MagicMock()
        mock_rebuilder.rebuild.return_value = (5, [])

        with patch("code_assembler.cli.parse_args", return_value=args):
            with patch("code_assembler.rebuilder.CodebaseRebuilder", return_value=mock_rebuilder):
                with patch("sys.stdout", new=StringIO()) as fake_out:
                    main()
                    output = fake_out.getvalue()

        self.assertIn("5", output)


# ---------------------------------------------------------------------------
# [4] config — empty extension string must not crash
# ---------------------------------------------------------------------------

class TestConfigEmptyExtension(unittest.TestCase):

    def test_empty_string_extension_is_skipped(self):
        """An empty string in extensions must be silently skipped, not crash."""
        from code_assembler.config import AssemblerConfig

        # This must not raise IndexError on ext[0]
        config = AssemblerConfig(
            paths=["."],
            extensions=["", ".py", ""],
            use_default_excludes=False,
        )
        self.assertIn(".py", config.extensions)
        self.assertNotIn("", config.extensions)

    def test_only_empty_extensions_produces_no_match(self):
        """All-empty extensions: no crash, but assembler will find no files."""
        from code_assembler.config import AssemblerConfig

        # The initial check `if not self.extensions` runs BEFORE normalization,
        # so [""] passes. After normalization extensions=[] which is valid config
        # (just matches nothing). Should not raise.
        try:
            config = AssemblerConfig(
                paths=["."],
                extensions=[""],
                use_default_excludes=False,
            )
            self.assertEqual(config.extensions, [])
        except Exception as exc:
            self.fail(f"AssemblerConfig raised unexpectedly on empty extension: {exc}")

    def test_invalid_compress_level_raises(self):
        """An invalid compress_level must raise ValueError with a clear message."""
        from code_assembler.config import AssemblerConfig

        with self.assertRaises(ValueError) as ctx:
            AssemblerConfig(
                paths=["."],
                extensions=[".py"],
                use_default_excludes=False,
                compress_level="full",  # invalid
            )
        self.assertIn("compress_level", str(ctx.exception))


# ---------------------------------------------------------------------------
# [5] analyzers — commonpath must not crash on multi-drive Windows paths
# ---------------------------------------------------------------------------

class TestAnalyzersCommonPath(unittest.TestCase):

    def test_commonpath_value_error_fallback(self):
        """
        When os.path.commonpath raises ValueError (Windows multi-drive),
        _get_components must return an empty list gracefully.
        """
        from code_assembler.analyzers import ArchitectureAnalyzer
        from code_assembler.config import FileEntry, CodebaseStats

        entries = [
            FileEntry(path="C:\\src\\main.py", type="file", depth=1),
            FileEntry(path="D:\\lib\\utils.py", type="file", depth=1),
        ]
        stats = CodebaseStats(total_files=2)

        analyzer = ArchitectureAnalyzer(entries, stats)

        with patch("os.path.commonpath", side_effect=ValueError("Paths don't have same drive")):
            # Must not raise
            result = analyzer._get_components()

        # Result should be a list (possibly empty) — not an exception
        self.assertIsInstance(result, list)

    def test_analyze_data_survives_commonpath_error(self):
        """Full analyze_data() call must survive a commonpath failure."""
        from code_assembler.analyzers import ArchitectureAnalyzer
        from code_assembler.config import FileEntry, CodebaseStats

        entries = [FileEntry(path="/a/file.py", type="file", depth=1)]
        stats = CodebaseStats(total_files=1, files_by_ext={".py": 1})

        analyzer = ArchitectureAnalyzer(entries, stats)

        with patch("os.path.commonpath", side_effect=ValueError("bad paths")):
            result = analyzer.analyze_data()

        self.assertIn("components", result)
        self.assertIn("distribution", result)


# ---------------------------------------------------------------------------
# [6] delta — errors in extract_metadata must surface, not be swallowed
# ---------------------------------------------------------------------------

class TestDeltaErrorSurfacing(unittest.TestCase):

    def test_permission_error_is_reported(self):
        """PermissionError on the snapshot file must print a warning, not silently pass."""
        from code_assembler.delta import extract_metadata

        with patch("builtins.open", side_effect=PermissionError("access denied")):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("fake.md")

        self.assertEqual(result, {})
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        # Message contains "Cannot read snapshot (permission denied)"
        self.assertIn("cannot read snapshot", printed.lower())

    def test_corrupted_json_is_reported(self):
        """Invalid JSON in the metadata block must print a warning, not silently pass."""
        from code_assembler.delta import extract_metadata

        bad_md = "<!-- CODE_ASSEMBLER_METADATA\n{not valid json}\n-->"
        with patch("builtins.open", unittest.mock.mock_open(read_data=bad_md)):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("fake.md")

        self.assertEqual(result, {})
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        # Message contains "corrupted (invalid JSON)"
        self.assertIn("corrupted", printed.lower())

    def test_missing_metadata_block_returns_empty_silently(self):
        """A snapshot without a metadata block returns {} without printing anything."""
        from code_assembler.delta import extract_metadata

        plain_md = "# Consolidated Codebase\n\nSome content, no metadata block."
        with patch("builtins.open", unittest.mock.mock_open(read_data=plain_md)):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("fake.md")

        self.assertEqual(result, {})
        mock_print.assert_not_called()

    def test_file_not_found_returns_empty_silently(self):
        """Missing snapshot file returns {} silently (expected caller behaviour)."""
        from code_assembler.delta import extract_metadata

        with patch("builtins.open", side_effect=FileNotFoundError()):
            with patch("builtins.print") as mock_print:
                result = extract_metadata("does_not_exist.md")

        self.assertEqual(result, {})
        mock_print.assert_not_called()


# ---------------------------------------------------------------------------
# [7] utils — Linux clipboard xsel fallback on ANY xclip failure
# ---------------------------------------------------------------------------

class TestClipboardLinuxFallback(unittest.TestCase):

    def _linux_clip(self, text, xclip_exc):
        """Helper: run copy_to_clipboard under Linux with a given xclip exception."""
        from code_assembler.utils import copy_to_clipboard
        from code_assembler.utils import _CLIPBOARD_TIMEOUT

        with patch("platform.system", return_value="Linux"):
            with patch("subprocess.run") as mock_run:
                # First call (xclip) raises the given exception
                # Second call (xsel) succeeds
                mock_run.side_effect = [xclip_exc, MagicMock()]
                result = copy_to_clipboard(text)

        return result, mock_run

    def test_xsel_fallback_on_file_not_found(self):
        """xclip missing (FileNotFoundError) → try xsel."""
        result, mock_run = self._linux_clip("hello", FileNotFoundError())
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)
        xsel_call = mock_run.call_args_list[1]
        self.assertIn("xsel", str(xsel_call))

    def test_xsel_fallback_on_called_process_error(self):
        """
        xclip installed but failing (e.g. no DISPLAY) → CalledProcessError.
        Previously this was caught by the outer except and returned False
        without ever trying xsel. Now xsel must be attempted.
        """
        exc = subprocess.CalledProcessError(1, "xclip")
        result, mock_run = self._linux_clip("hello", exc)
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)
        xsel_call = mock_run.call_args_list[1]
        self.assertIn("xsel", str(xsel_call))

    def test_xsel_fallback_on_timeout(self):
        """xclip timing out → TimeoutExpired → try xsel."""
        exc = subprocess.TimeoutExpired(cmd="xclip", timeout=10)
        result, mock_run = self._linux_clip("hello", exc)
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)


# ---------------------------------------------------------------------------
# [8] utils — subprocess calls must include a timeout
# ---------------------------------------------------------------------------

class TestClipboardTimeout(unittest.TestCase):

    def _capture_run_kwargs(self, system: str, text: str = "test"):
        """Run copy_to_clipboard and capture all kwargs passed to subprocess.run."""
        from code_assembler.utils import copy_to_clipboard

        calls_kwargs = []

        def fake_run(*args, **kwargs):
            calls_kwargs.append(kwargs)
            return MagicMock()

        with patch("platform.system", return_value=system):
            with patch("subprocess.run", side_effect=fake_run):
                copy_to_clipboard(text)

        return calls_kwargs

    def test_windows_clipboard_has_timeout(self):
        kwargs_list = self._capture_run_kwargs("Windows")
        self.assertTrue(len(kwargs_list) > 0)
        self.assertIn("timeout", kwargs_list[0], "subprocess.run on Windows has no timeout")

    def test_macos_clipboard_has_timeout(self):
        kwargs_list = self._capture_run_kwargs("Darwin")
        self.assertTrue(len(kwargs_list) > 0)
        self.assertIn("timeout", kwargs_list[0], "subprocess.run on macOS has no timeout")

    def test_linux_xclip_has_timeout(self):
        kwargs_list = self._capture_run_kwargs("Linux")
        self.assertTrue(len(kwargs_list) > 0)
        self.assertIn("timeout", kwargs_list[0], "subprocess.run for xclip has no timeout")


# ---------------------------------------------------------------------------
# [9] core — write failure must raise OSError (not silently succeed)
# ---------------------------------------------------------------------------

class TestCoreWriteFailure(unittest.TestCase):

    def test_write_failure_raises_oserror(self):
        """
        If write_file_content returns False, assemble_codebase must raise OSError.
        Previously the return value was ignored and a false "Saved" message shown.
        """
        from code_assembler.core import assemble_codebase

        test_dir = tempfile.mkdtemp()
        try:
            src = Path(test_dir) / "src"
            src.mkdir()
            (src / "hello.py").write_text("print('hi')", encoding="utf-8")

            # FIX: write_file_content is imported lazily inside assemble_codebase(),
            # so patch it in the file_io module, not in core's namespace.
            with patch("code_assembler.file_io.write_file_content", return_value=False):
                with self.assertRaises(OSError):
                    assemble_codebase(
                        paths=[str(src)],
                        extensions=[".py"],
                        output=str(Path(test_dir) / "out.md"),
                        show_progress=False,
                    )
        finally:
            shutil.rmtree(test_dir)

    def test_write_success_does_not_raise(self):
        """Normal write path must not raise any exception."""
        from code_assembler.core import assemble_codebase

        test_dir = tempfile.mkdtemp()
        try:
            src = Path(test_dir) / "src"
            src.mkdir()
            (src / "hello.py").write_text("print('hi')", encoding="utf-8")

            # Patch write to succeed (returns True) — we just verify no exception
            with patch("code_assembler.file_io.write_file_content", return_value=True):
                try:
                    assemble_codebase(
                        paths=[str(src)],
                        extensions=[".py"],
                        output=str(Path(test_dir) / "out.md"),
                        show_progress=False,
                    )
                except OSError:
                    self.fail("assemble_codebase raised OSError on a successful write")
        finally:
            shutil.rmtree(test_dir)


# ---------------------------------------------------------------------------
# [10] interactive — use_default_excludes must be False after wizard run
# ---------------------------------------------------------------------------

class TestInteractiveUseDefaultExcludes(unittest.TestCase):

    def test_wizard_sets_use_default_excludes_false(self):
        """
        The wizard manages exclusions itself. It must pass use_default_excludes=False
        to assemble_codebase so AssemblerConfig doesn't add defaults a second time.
        """
        from code_assembler.interactive import InteractiveWizard

        wizard = InteractiveWizard()

        inputs = [
            "1",    # Current directory
            "1",    # Python preset
            "y",    # Use default exclusions
            "n",    # No custom patterns
            "",     # Default output name
            "n",    # No advanced config
            "y",    # Confirm assembly
            "n",    # Don't save config
        ]

        captured_kwargs = {}

        def fake_assemble(**kwargs):
            captured_kwargs.update(kwargs)
            return "# mock content"

        with patch("builtins.input", side_effect=inputs):
            with patch("code_assembler.interactive.os.path.exists", return_value=False):
                with patch("code_assembler.interactive.assemble_codebase", side_effect=fake_assemble):
                    with patch("sys.stdout", new=StringIO()):
                        wizard.run()

        self.assertIn("use_default_excludes", captured_kwargs,
                      "use_default_excludes was not passed to assemble_codebase")
        self.assertFalse(
            captured_kwargs["use_default_excludes"],
            "use_default_excludes must be False when wizard manages exclusions itself"
        )

    def test_wizard_exclusions_not_doubled(self):
        """
        Default patterns must not appear twice when use_default_excludes=False
        and the wizard already merged them into exclude_patterns.
        """
        from code_assembler.interactive import InteractiveWizard
        from code_assembler.constants import DEFAULT_EXCLUDE_PATTERNS

        wizard = InteractiveWizard()
        inputs = ["1", "1", "y", "n", "", "n", "y", "n"]
        captured_kwargs = {}

        def fake_assemble(**kwargs):
            captured_kwargs.update(kwargs)
            return "# mock"

        with patch("builtins.input", side_effect=inputs):
            with patch("code_assembler.interactive.os.path.exists", return_value=False):
                with patch("code_assembler.interactive.assemble_codebase", side_effect=fake_assemble):
                    with patch("sys.stdout", new=StringIO()):
                        wizard.run()

        patterns = captured_kwargs.get("exclude_patterns", [])
        # No pattern should appear more than once
        for p in DEFAULT_EXCLUDE_PATTERNS:
            count = patterns.count(p)
            self.assertLessEqual(
                count, 1,
                f"Pattern '{p}' appears {count} times — use_default_excludes double-application bug"
            )


if __name__ == "__main__":
    unittest.main()
