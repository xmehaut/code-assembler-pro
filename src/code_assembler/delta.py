"""
Delta analysis engine for Code Assembler Pro.

This module provides the logic to compare the current state of a codebase
against a previously generated Markdown snapshot. It enables "incremental"
updates by identifying which files have been modified, added, or deleted
since the last assembly.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Tuple

_METADATA_RE = re.compile(r'<!-- CODE_ASSEMBLER_METADATA\s+(.*?)\s+-->', re.DOTALL)


def extract_metadata(md_file: str) -> Dict[str, datetime]:
    """Extract the {path: datetime} dict from the hidden metadata block."""
    result: Dict[str, datetime] = {}
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        match = _METADATA_RE.search(content)
        if not match:
            # Old snapshot without metadata — caller treats all files as new
            return result

        data = json.loads(match.group(1))
        for path, date_str in data.get('files', {}).items():
            try:
                result[path] = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                continue

    except FileNotFoundError:
        pass  # Safe: caller checks existence before calling in most paths
    except PermissionError as exc:
        # FIX: was bare `except Exception: pass` — real errors now surface
        print(f"  [!] Cannot read snapshot (permission denied): {exc}")
    except json.JSONDecodeError as exc:
        print(f"  [!] Snapshot metadata is corrupted (invalid JSON): {exc}")
    except Exception as exc:
        print(f"  [!] Unexpected error reading snapshot metadata: {exc}")

    return result


def normalize_key(path: str) -> str:
    """Normalize a path to lowercase forward-slash form."""
    return str(Path(path)).replace('\\', '/').lower().strip('/')


def get_delta(md_file: str, current_files: Set[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    snapshot = extract_metadata(md_file)

    # No metadata → treat everything as new (backwards compat with old snapshots)
    if not snapshot:
        return set(current_files), set(current_files), set()

    modified: Set[str] = set()
    added: Set[str] = set()
    deleted: Set[str] = set()
    matched_keys: Set[str] = set()

    if current_files:
        try:
            common_root = os.path.commonpath(list(current_files))
            if os.path.isfile(common_root):
                common_root = os.path.dirname(common_root)
        except ValueError:
            common_root = os.getcwd()
    else:
        common_root = os.getcwd()

    for abs_path in current_files:
        try:
            rel_path = os.path.relpath(abs_path, common_root).replace('\\', '/')
            if rel_path.startswith('./'):
                rel_path = rel_path[2:]
        except ValueError:
            rel_path = normalize_key(abs_path)

        match_key = None

        if rel_path in snapshot:
            match_key = rel_path
        else:
            for snap_key in snapshot:
                if rel_path.endswith(snap_key) or snap_key.endswith(rel_path):
                    if Path(rel_path).name == Path(snap_key).name:
                        match_key = snap_key
                        break

        if match_key:
            matched_keys.add(match_key)
            if _has_changed(abs_path, snapshot[match_key]):
                modified.add(abs_path)
        else:
            added.add(abs_path)

    for snap_key in snapshot:
        if snap_key not in matched_keys:
            deleted.add(snap_key)

    return modified, added, deleted


def _has_changed(abs_path: str, snapshot_dt: datetime) -> bool:
    try:
        current_mtime = datetime.fromtimestamp(
            os.path.getmtime(abs_path)
        ).replace(second=0, microsecond=0)
        snapshot_mtime = snapshot_dt.replace(second=0, microsecond=0)
        return current_mtime != snapshot_mtime
    except OSError:
        return True


def filter_changed_files(md_file: str, all_files: Set[str]) -> Tuple[Set[str], Set[str]]:
    modified, added, deleted = get_delta(md_file, all_files)
    return modified | added, deleted


def format_delta_summary(modified: Set[str], added: Set[str], deleted: Set[str]) -> str:
    lines = []

    def _fmt(files: Set[str], label: str, icon: str) -> None:
        if not files:
            return
        count = len(files)
        names = sorted(Path(p).name for p in files)
        disp = ', '.join(names[:5]) + (f", ... (+{count - 5})" if count > 5 else "")
        lines.append(f"> {icon} {label} ({count}): {disp}")

    _fmt(modified, "Modified", "✏️ ")
    _fmt(added, "Added", "➕")
    _fmt(deleted, "Deleted", "❌")

    if not lines:
        lines.append("> ✅ No changes detected since last snapshot")
    return '\n'.join(lines)