"""
Interactive mode demonstration for Code Assembler Pro.

This script shows how to launch the interactive wizard programmatically.
"""
import sys
from pathlib import Path

# Setup path
current_file = Path(__file__).resolve()
project_root = current_file.parents[1]
sys.path.append(str(project_root / "src"))

try:
    from code_assembler import run_interactive_mode
except ImportError:
    print("❌ Error: Could not import 'code_assembler'.")
    sys.exit(1)

if __name__ == "__main__":
    print("=" * 70)
    print("  Code Assembler Pro - Interactive Demo")
    print("=" * 70)
    print("\nThis will launch the interactive wizard.")
    print("You'll be guided through all configuration steps.\n")

    input("Press Enter to start... ")

    # Launch the wizard
    run_interactive_mode()