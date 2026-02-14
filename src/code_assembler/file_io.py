"""
File I/O operations for Code Assembler Pro.

This module handles all file reading and encoding detection operations.
"""

import chardet
from typing import Optional


def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file with intelligent fallback.
    Reads only a sample (64KB) to avoid loading huge files into memory.
    """
    SAMPLE_SIZE = 65536  # 64KB is enough for reliable detection

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(SAMPLE_SIZE)
        return 'utf-8'
    except UnicodeDecodeError:
        pass
    except FileNotFoundError:
        raise

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(SAMPLE_SIZE)
            result = chardet.detect(raw_data)
            detected_encoding = result.get('encoding')
            return detected_encoding if detected_encoding else 'utf-8'
    except Exception:
        return 'utf-8'


def read_file_content(file_path: str, encoding: Optional[str] = None) -> str:
    """
    Read the content of a file with automatic encoding detection.
    """
    try:
        if encoding is None:
            encoding = detect_encoding(file_path)

        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            return f.read()

    except FileNotFoundError:
        return f"[ERROR] File not found: {file_path}"
    except PermissionError:
        return f"[ERROR] Permission denied: {file_path}"
    except Exception as e:
        return f"[ERROR] Error reading file: {str(e)}"


def write_file_content(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Write content to a file.
    """
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[ERROR] Error writing file {file_path}: {e}")
        return False


def read_file_head(file_path: str, max_lines: int, encoding: Optional[str] = None) -> str:
    """
    Read only the first N lines of a file.
    """
    if encoding is None:
        encoding = detect_encoding(file_path)

    lines = []
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break
                lines.append(line)
        return "".join(lines)
    except Exception as e:
        return f"[ERROR] Error reading file head: {str(e)}"