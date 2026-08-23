"""
Multi-module (monorepo) assembly demo (New in v4.7).
Demonstrates assembling several sub-projects in a single pass, each into
its own Markdown snapshot, cross-linked via depends_on / siblings.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from code_assembler import assemble_modules


def run_modules_demo():
    root = Path(__file__).resolve().parents[1]

    config = {
        "extensions": [".py"],
        "output": "monorepo_snapshot.md",
        "show_progress": True,
        "modules": {
            # "shared" has no depends_on — nothing else in this demo config
            # is a dependency of it.
            "shared": {
                "paths": [str(root / "src" / "code_assembler")],
                "description": "Core library code",
            },
            # "rebuilder" gets its own extensions override (still .py here,
            # but this is where a module could ask for .ts, .rs, etc.
            # instead of inheriting the root's) and declares a dependency
            # on "shared" — purely declarative, just echoed into its
            # frontmatter, not verified against real imports.
            "tests": {
                "paths": [str(root / "tests")],
                "description": "Test suite",
                "depends_on": ["shared"],
                "exclude_patterns": ["__pycache__"],
            },
        },
    }

    print("--- Assembling every module in one batch ---")
    result = assemble_modules(config)

    print(f"\n{len(result['succeeded'])} succeeded, {len(result['failed'])} failed:")
    for name, output_path in result["succeeded"].items():
        print(f"  ✅ {name} -> {output_path}")
    for name, error in result["failed"].items():
        print(f"  ❌ {name}: {error}")

    print(
        "\nEach output file's frontmatter now lists the others under "
        "'siblings' (name, file, description, token count) and its own "
        "'depends_on' — open one of the generated .md files and look at "
        "the top few lines to see it."
    )


if __name__ == "__main__":
    run_modules_demo()
