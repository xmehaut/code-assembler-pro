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


class TestPublicAPI(unittest.TestCase):
    """assemble_modules() must be importable the same way as the rest of
    the public API — omitted from __init__.py when first added, caught
    only while writing README/examples for it, not by a test. Guarded
    here so it can't silently regress."""

    def test_assemble_modules_is_exported_from_the_top_level_package(self):
        import code_assembler
        self.assertTrue(hasattr(code_assembler, "assemble_modules"))
        self.assertIn("assemble_modules", code_assembler.__all__)


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


class TestDependsOnValidation(unittest.TestCase):
    """§6: depends_on is declarative, validated at config-parse time."""

    def test_depends_on_unknown_module_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            resolve_module_configs({
                "extensions": [".py"],
                "modules": {
                    "api": {"paths": ["./api"], "depends_on": ["shaerd"]},
                },
            })
        self.assertIn("unknown module", str(ctx.exception))

    def test_depends_on_self_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            resolve_module_configs({
                "extensions": [".py"],
                "modules": {
                    "api": {"paths": ["./api"], "depends_on": ["api"]},
                },
            })
        self.assertIn("cannot depend_on itself", str(ctx.exception))

    def test_depends_on_valid_reference_is_accepted(self):
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "modules": {
                "shared": {"paths": ["./shared"]},
                "api": {"paths": ["./api"], "depends_on": ["shared"]},
            },
        })
        self.assertEqual(resolved["api"]["depends_on"], ["shared"])
        self.assertEqual(resolved["shared"]["depends_on"], [])

    def test_depends_on_order_in_modules_object_does_not_matter(self):
        """A module may depend on one declared *after* it in the JSON —
        validation only runs once every module name is known."""
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "modules": {
                "api": {"paths": ["./api"], "depends_on": ["shared"]},
                "shared": {"paths": ["./shared"]},
            },
        })
        self.assertEqual(resolved["api"]["depends_on"], ["shared"])

    def test_root_level_depends_on_is_not_inherited(self):
        """A root "depends_on" would apply to every module including the
        one it names — deliberately excluded from inheritance (§6)."""
        resolved = resolve_module_configs({
            "extensions": [".py"],
            "depends_on": ["shared"],
            "modules": {
                "shared": {"paths": ["./shared"]},
                "api": {"paths": ["./api"]},
            },
        })
        self.assertEqual(resolved["shared"]["depends_on"], [])
        self.assertEqual(resolved["api"]["depends_on"], [])


class TestSiblingsFrontmatter(unittest.TestCase):
    """§7: end-to-end, real files, real frontmatter."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.previous_cwd = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.previous_cwd)
        shutil.rmtree(self.test_dir)

    def _frontmatter(self, path: str) -> dict:
        import yaml
        import re as _re
        content = Path(path).read_text(encoding='utf-8')
        m = _re.match(r'\A---\n(.*?)\n---\n', content, _re.DOTALL)
        self.assertIsNotNone(m, f"No frontmatter found in {path}")
        return yaml.safe_load(m.group(1))

    def test_siblings_lists_every_other_module_never_itself(self):
        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("print('api')", encoding='utf-8')
        (self.root / "shared").mkdir()
        (self.root / "shared" / "core.py").write_text("x = 1", encoding='utf-8')

        result = assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {
                "api": {"paths": ["api"], "description": "REST API", "depends_on": ["shared"]},
                "shared": {"paths": ["shared"], "description": "Shared utils"},
            },
        })
        self.assertEqual(result["failed"], {})

        api_fm = self._frontmatter("codebase_api.md")
        self.assertEqual(api_fm["module"], "api")
        self.assertEqual(api_fm["depends_on"], ["shared"])
        self.assertEqual(len(api_fm["siblings"]), 1)
        sibling = api_fm["siblings"][0]
        self.assertEqual(sibling["module"], "shared")
        self.assertEqual(sibling["file"], "codebase_shared.md")
        self.assertEqual(sibling["description"], "Shared utils")
        self.assertIsInstance(sibling["tokens"], int)

        shared_fm = self._frontmatter("codebase_shared.md")
        self.assertEqual(shared_fm["module"], "shared")
        self.assertEqual(shared_fm["depends_on"], [])
        self.assertEqual([s["module"] for s in shared_fm["siblings"]], ["api"])

    def test_generated_at_is_identical_across_the_batch(self):
        """§9: every frontmatter in the batch must share one generated_at,
        not drift by the milliseconds between per-module regeneration."""
        for mod in ("a", "b", "c"):
            (self.root / mod).mkdir()
            (self.root / mod / "f.py").write_text("x = 1", encoding='utf-8')

        assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {m: {"paths": [m]} for m in ("a", "b", "c")},
        })

        timestamps = {
            self._frontmatter(f"codebase_{m}.md")["generated_at"] for m in ("a", "b", "c")
        }
        self.assertEqual(len(timestamps), 1, f"generated_at differs across the batch: {timestamps}")

    def test_module_with_no_description_has_empty_string_in_sibling_entry(self):
        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("print('api')", encoding='utf-8')
        (self.root / "shared").mkdir()
        (self.root / "shared" / "core.py").write_text("x = 1", encoding='utf-8')

        assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {
                "api": {"paths": ["api"]},
                "shared": {"paths": ["shared"]},  # no description
            },
        })

        api_fm = self._frontmatter("codebase_api.md")
        self.assertEqual(api_fm["siblings"][0]["description"], "")

    def test_single_module_batch_has_empty_siblings_list(self):
        (self.root / "solo").mkdir()
        (self.root / "solo" / "f.py").write_text("x = 1", encoding='utf-8')

        assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {"solo": {"paths": ["solo"]}},
        })

        fm = self._frontmatter("codebase_solo.md")
        self.assertEqual(fm["siblings"], [])

    def test_body_content_is_unaffected_by_frontmatter_patching(self):
        """Phase 2 replaces only the leading frontmatter block — the rest
        of the file (table of contents, file content, hidden metadata)
        must be byte-identical to what phase 1 wrote."""
        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("def handler(): pass", encoding='utf-8')
        (self.root / "shared").mkdir()
        (self.root / "shared" / "core.py").write_text("x = 1", encoding='utf-8')

        assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {
                "api": {"paths": ["api"]},
                "shared": {"paths": ["shared"]},
            },
        })

        content = (self.root / "codebase_api.md").read_text(encoding='utf-8')
        self.assertIn("def handler(): pass", content)
        self.assertIn("CODE_ASSEMBLER_METADATA", content)

    def test_rebuild_still_works_on_a_batch_output_with_siblings(self):
        """The patched frontmatter must not confuse the rebuild parser —
        same guarantee already validated for plain frontmatter/description
        in test_rebuild.py, re-checked here since the frontmatter is now
        rewritten by a second, independent code path (phase 2's regex
        splice) rather than generated once inline."""
        from code_assembler.rebuilder import CodebaseRebuilder

        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("print('hello')", encoding='utf-8')
        (self.root / "shared").mkdir()
        (self.root / "shared" / "core.py").write_text("x = 1", encoding='utf-8')

        assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {
                "api": {"paths": ["api"], "depends_on": ["shared"]},
                "shared": {"paths": ["shared"]},
            },
        })

        rebuilder = CodebaseRebuilder("codebase_api.md", "restored")
        count, errors = rebuilder.rebuild()
        self.assertEqual(errors, [])
        self.assertEqual(count, 1)
        self.assertEqual(
            (self.root / "restored" / "api" / "main.py").read_text(encoding='utf-8'),
            "print('hello')"
        )


    def test_description_with_non_ascii_characters_does_not_break_patching(self):
        """
        Regression: json.dumps() escapes non-ASCII characters as \\uXXXX
        (e.g. an em-dash becomes \\u2014). Phase 2 originally passed the
        regenerated frontmatter straight to re.sub() as the replacement
        argument — re.sub() interprets backslashes in a *string*
        replacement as backreferences (\\1, \\g<name>, ...), and \\u2014
        isn't a valid one, raising "bad escape \\u". Found by running the
        exact JSON from README.md's own Monorepo Assembly example, whose
        description contains an em-dash.
        """
        (self.root / "api").mkdir()
        (self.root / "api" / "main.py").write_text("print('api')", encoding='utf-8')
        (self.root / "shared").mkdir()
        (self.root / "shared" / "core.py").write_text("x = 1", encoding='utf-8')

        result = assemble_modules({
            "extensions": [".py"],
            "output": "codebase.md",
            "show_progress": False,
            "modules": {
                "api": {
                    "paths": ["api"],
                    "description": "REST API — auth, billing, webhooks",
                    "depends_on": ["shared"],
                },
                "shared": {"paths": ["shared"]},
            },
        })

        self.assertEqual(result["failed"], {})
        api_fm = self._frontmatter("codebase_api.md")
        self.assertEqual(api_fm["description"], "REST API — auth, billing, webhooks")


if __name__ == "__main__":
    unittest.main()
