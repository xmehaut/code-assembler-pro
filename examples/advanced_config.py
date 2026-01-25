"""
Advanced usage example for Code Assembler Pro.
This script demonstrates using a JSON configuration and targets the project itself.
"""
import json
import os
import sys
from pathlib import Path

# --- 1. ENVIRONMENT SETUP ---
# Get the current file path (.../code-assembler-pro/examples/advanced_config.py)
current_file = Path(__file__).resolve()

# Move up one level to find the root of the 'code-assembler-pro' project
# parents[0] = examples
# parents[1] = code-assembler-pro (The root)
project_root = current_file.parents[1]

# Add the 'src' directory to the Python Path so we can import the module
# even if it hasn't been installed via pip yet.
sys.path.append(str(project_root / "src"))

try:
    from code_assembler import assemble_from_config
except ImportError:
    print("❌ Error: Could not import 'code_assembler'.")
    print(f"   Ensure the src directory exists here: {project_root / 'src'}")
    sys.exit(1)

# --- 2. CONFIGURATION DEFINITION ---
print(f"📍 Target analyzed: {project_root}")

# Complete configuration (simulating an assembler_config.json file)
config = {
    # Paths to analyze (here, the project root)
    "paths": [str(project_root)],

    # Extensions to include
    "extensions": [".py", ".md", ".toml", ".j2"],

    # Output file name
    "output": "advanced_output.md",

    # Exclusions (IMPORTANT: exclude heavy folders and the output file itself)
    "exclude_patterns": [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "build",
        "dist",
        ".idea",
        ".vscode",
        "tests",       # Exclude tests for this example
        "examples",    # Exclude examples to avoid recursion
        "*.egg-info"
    ],

    # Behavior options
    "recursive": True,
    "include_readmes": True,
    "show_progress": True,

    # --- v4.1.0 Options (Large File Management) ---
    "max_file_size_mb": 0.5,       # Low threshold for demonstration
    "truncate_large_files": True,  # Enable truncation
    "truncation_limit_lines": 100  # Keep the first 100 lines
}

# --- 3. EXECUTION ---
config_path = "temp_config.json"

# Write the temporary JSON config file
with open(config_path, "w", encoding='utf-8') as f:
    json.dump(config, f, indent=2)

print("⚙️  Starting assembly via JSON configuration...")

try:
    # Run the assembler
    assemble_from_config(config_path)

    print(f"\n✅ Success! The file '{config['output']}' has been generated at the root.")
    print(f"   You can open it to view the result.")

except Exception as e:
    print(f"\n❌ An error occurred: {e}")

finally:
    # Cleanup the temporary file
    if os.path.exists(config_path):
        os.remove(config_path)
        print("🧹 Temporary configuration file cleaned.")