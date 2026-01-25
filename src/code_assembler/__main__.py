"""
Entry point for the code_assembler package execution.
"""
import sys
from pathlib import Path

# Calculate the 'src' directory path (one level above this file)
src_path = str(Path(__file__).resolve().parent.parent)

# Add it to the Python search path if it's not already there
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Now perform an ABSOLUTE import (without the dot)
# This works because 'src' is in the path, making 'code_assembler' visible
try:
    from code_assembler.cli import main
except ImportError:
    # Fallback for when the package is already properly installed via pip
    from .cli import main

if __name__ == "__main__":
    main()