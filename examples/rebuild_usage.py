"""
Rebuild Engine Demo (New in v4.4).
Demonstrates how to reconstruct a project structure from a Markdown snapshot.
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from code_assembler.rebuilder import CodebaseRebuilder

def run_rebuild_demo():
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)
    # 1. We need a source Markdown file with metadata
    # (Run basic_usage.py first to generate 'simple_snapshot.md')
    md_input = "simple_snapshot.md"
    target_dir = "./reconstructed_project"

    if not Path(md_input).exists():
        print(f"❌ Error: '{md_input}' not found.")
        print("Please run 'python basic_usage.py' first to generate a snapshot.")
        return

    print(f"🏗️  Starting reconstruction into: {target_dir}")

    # 2. Initialize the Rebuilder
    rebuilder = CodebaseRebuilder(
        md_path=md_input,
        output_dir=target_dir,
        dry_run=False  # Set to True to preview without writing
    )

    # 3. Execute Rebuild
    count, errors = rebuilder.rebuild()

    if errors:
        print(f"\n⚠️  Rebuild completed with {len(errors)} warnings:")
        for err in errors:
            print(f"   - {err}")

    print(f"\n✅ Done! {count} files reconstructed successfully.")

if __name__ == "__main__":
    run_rebuild_demo()