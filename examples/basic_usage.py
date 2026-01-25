"""
Basic usage example for Code Assembler Pro.
This script demonstrates a direct function call to consolidate code.
"""
import sys
from pathlib import Path

# Setup path to find code_assembler in the src directory
current_file = Path(__file__).resolve()
project_root = current_file.parents[1]
sys.path.append(str(project_root / "src"))

try:
    from code_assembler import assemble_codebase
except ImportError:
    print("❌ Error: Could not import 'code_assembler'.")
    sys.exit(1)

# Target the project root for this example
target_dir = project_root

print(f"Analyzing: {target_dir}")

# Simple assembly with direct arguments
markdown_content = assemble_codebase(
    paths=[str(target_dir)],
    extensions=[".py", ".md", ".toml"],
    output="example_output.md",
    exclude_patterns=[
        "__pycache__",
        "tests",
        "examples",
        ".venv",
        ".git",
        "build",
        "dist"
    ],
    truncate_large_files=True,
    truncation_limit_lines=500
)

print(f"\n✅ Done! Generated file size: {len(markdown_content):,} characters.")
print(f"💾 Saved to: example_output.md")