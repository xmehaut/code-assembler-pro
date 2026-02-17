"""
Advanced programmatic usage: JSON configuration and Delta Mode.
This script simulates a real-world workflow: Full assembly followed by an incremental update.
"""
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from code_assembler import assemble_from_config

def run_advanced_demo():
    root = Path(__file__).resolve().parents[1]
    config_path = "demo_config.json"
    output_md = "advanced_snapshot.md"

    # 1. Define a complex configuration
    config = {
        "paths": [str(root / "src")],
        "extensions": [".py", ".j2", "Dockerfile"],
        "output": output_md,
        "exclude_patterns": ["__pycache__", "tests"],
        "truncate_large_files": True,
        "truncation_limit_lines": 100,
        "show_progress": True
    }

    with open(config_path, "w", encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    print("--- STEP 1: Full Project Assembly ---")
    assemble_from_config(config_path)

    print("\n" + "="*40)
    print("--- STEP 2: Delta Mode (Incremental) ---")
    print("Only files modified since Step 1 will be included.")

    # We use the 'since' parameter to trigger Delta Mode
    assemble_from_config(config_path, since=output_md)

    # Cleanup
    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"\n🧹 Temporary config {config_path} cleaned.")

if __name__ == "__main__":
    run_advanced_demo()