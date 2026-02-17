"""
Basic programmatic usage of Code Assembler Pro.
Demonstrates how to consolidate code and get the result as a string.
"""
import os
import sys
from pathlib import Path

# Setup path to find code_assembler if not installed via pip
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent / "src"))

from code_assembler import assemble_codebase


def run_demo():
    # On se place mentalement à la racine du projet
    project_root = Path(__file__).resolve().parents[1]

    # On change le répertoire de travail pour que les chemins dans le MD soient propres (src/...)
    os.chdir(project_root)

    print(f"🚀 Assembling context from: src/code_assembler")

    markdown_content = assemble_codebase(
        paths=["src/code_assembler"],  # Chemin relatif propre
        extensions=[".py"],
        output="simple_snapshot.md",
        show_progress=True
    )

if __name__ == "__main__":
    run_demo()