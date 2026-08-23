"""
Tests for multi-module assembly: `modules`, inheritance/override rules,
and output naming (MODULES_SPEC.md §2-4, §9-11). `depends_on` and
`siblings` are a separate step, not covered here.
"""
import json
import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from code_assembler.config import resolve_module_configs, derive_module_output
from code_assembler.core import assemble_modules, assemble_from_config


class TestDeriveModuleOutput(unittest.TestCase):
    """§4 naming table, exercised directly."""

    def test_default_md_extension(self):
        self.assertEqual(derive_module_output("codebase.md", "api"), "codebase_api.md")

    def test_no_extension_gets_md_appended(self):
        self.assertEqual(derive_module_output("codebase", "api"), "codebase_api.md")

    def test_directory_component_preserved(self):
        self.assertEqual(
            derive_module_output("snapshots/codebase.md", "api"),
            str(Path("snapshots") / "codebase_api.md"),
        )


class TestResolveModuleConfigs(unittest.TestCase):

    def test_root_paths_and_modules_are_mutually_exclusive(self):
        with self.assertRaises(ValueError) as ctx:
            resolve_module_configs({
                "paths": ["./src"],
                "extensions": [".py"],
                "modules": {"api": {"paths": ["./api"]}},
            })
        self.assertIn("mutually exclusive", str(ctx.exception))

    def test_module_without_paths_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            resolve_module_configs({
                "extensions": [".py"],
                "modules": {"api": {}},
            })
        self.assertIn('"paths"', str(ctx.exception))

    def test_module_name_with_slash_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            resolve_module_configs({
                "extensions": [".py"],
                "modules": {"backend/api": {"paths": ["./api"]}},
            })
        self.assertIn("path separator", str(ctx.exception))

    def test_missing_extensions_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            resolve_module_configs({
                "modules": {"api": {"paths": ["./api"]}},
            })
        self.assertIn("extensions", str(ctx.exception))

    def test_module_inherits_root_extensions(self):
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "modules": {"api": {"paths": ["./api"]}},
        })
        self.assertEqual(resolved["api"]["extensions"], [".py"])

    def test_module_extensions_replace_not_merge_root(self):
        """§3: replacement semantics, not merging."""
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "modules": {
                "frontend": {"paths": ["./frontend"], "extensions": [".ts", ".tsx"]},
            },
        })
        self.assertEqual(resolved["frontend"]["extensions"], [".ts", ".tsx"])

    def test_module_exclude_patterns_replace_not_merge_root(self):
        """Same replacement rule for exclude_patterns specifically, since a
        merge would be the one plausible exception — the spec (§3)
        deliberately rejects it for consistency."""
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "exclude_patterns": ["*_generated.py"],
            "modules": {
                "api": {"paths": ["./api"], "exclude_patterns": ["*_test.py"]},
            },
        })
        self.assertEqual(resolved["api"]["exclude_patterns"], ["*_test.py"])

    def test_compress_and_other_scalars_are_inherited(self):
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "compress": True,
            "compress_level": "signatures",
            "modules": {
                "shared": {"paths": ["./shared"]},
                "vendor": {"paths": ["./vendor"], "compress": False},
            },
        })
        self.assertTrue(resolved["shared"]["compress"])
        self.assertFalse(resolved["vendor"]["compress"])

    def test_output_is_derived_when_not_set(self):
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "output": "codebase.md",
            "modules": {"api": {"paths": ["./api"]}},
        })
        self.assertEqual(resolved["api"]["output"], "codebase_api.md")

    def test_module_output_override_wins_over_derivation(self):
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "output": "codebase.md",
            "modules": {
                "api": {"paths": ["./api"], "output": "custom.md"},
            },
        })
        self.assertEqual(resolved["api"]["output"], "custom.md")

    def test_root_paths_key_never_leaks_into_a_module(self):
        """"paths" is excluded from root_defaults — every module must use
        its own, never silently inherit a root one (which can't exist
        anyway per the mutual-exclusivity rule, but belt and suspenders)."""
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "modules": {"api": {"paths": ["./api"]}},
        })
        self.assertEqual(resolved["api"]["paths"], ["./api"])


class TestAssembleModulesBatch(unittest.TestCase):
    """End-to-end: real directories, real files written to disk."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.previous_cwd = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.previous_cwd)
        shutil.rmtree(self.test_dir)

    def test_batch_produces_one_file_per_module(self):
        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("print('api')", encoding='utf-8')
        (self.root / "frontend").mkdir()
        (self.root / "frontend" / "app.ts").write_text("console.log('ui')", encoding='utf-8')

        result = assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {
                "api": {"paths": ["api"]},
                "frontend": {"paths": ["frontend"], "extensions": [".ts"]},
            },
        })

        self.assertEqual(result["failed"], {})
        self.assertEqual(set(result["succeeded"]), {"api", "frontend"})
        self.assertTrue((self.root / "codebase_api.md").exists())
        self.assertTrue((self.root / "codebase_frontend.md").exists())
        self.assertIn("print('api')", (self.root / "codebase_api.md").read_text(encoding='utf-8'))
        self.assertIn("console.log", (self.root / "codebase_frontend.md").read_text(encoding='utf-8'))

    def test_one_bad_module_does_not_abort_the_batch(self):
        """§10 partial-failure policy: the other modules still get built,
        and the failure is reported rather than raised."""
        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("print('ok')", encoding='utf-8')

        result = assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {
                "api": {"paths": ["api"]},
                "ghost": {"paths": ["does_not_exist"]},
            },
        })

        self.assertIn("api", result["succeeded"])
        self.assertIn("ghost", result["failed"])
        self.assertTrue((self.root / "codebase_api.md").exists())
        self.assertFalse((self.root / "codebase_ghost.md").exists())

    def test_assemble_from_config_detects_modules_and_returns_dict(self):
        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("print('ok')", encoding='utf-8')

        config_file = self.root / "batch.json"
        config_file.write_text(json.dumps({
            "extensions": [".py"],
            "show_progress": False,
            "modules": {"api": {"paths": ["api"]}},
        }), encoding='utf-8')

        result = assemble_from_config(str(config_file))
        self.assertIsInstance(result, dict)
        self.assertIn("api", result["succeeded"])

    def test_since_is_rejected_for_a_modules_config(self):
        config_file = self.root / "batch.json"
        config_file.write_text(json.dumps({
            "extensions": [".py"],
            "modules": {"api": {"paths": ["api"]}},
        }), encoding='utf-8')

        with self.assertRaises(ValueError) as ctx:
            assemble_from_config(str(config_file), since="prev.md")
        self.assertIn("--since", str(ctx.exception))

    def test_cli_overrides_are_rejected_for_a_modules_config(self):
        config_file = self.root / "batch.json"
        config_file.write_text(json.dumps({
            "extensions": [".py"],
            "modules": {"api": {"paths": ["api"]}},
        }), encoding='utf-8')

        with self.assertRaises(ValueError) as ctx:
            assemble_from_config(str(config_file), compress=True)
        self.assertIn("CLI overrides", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
