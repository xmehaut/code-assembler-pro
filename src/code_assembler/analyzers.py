"""
Architecture and Quality analyzers for Code Assembler Pro.

This module extracts structural data and patterns from the codebase
without handling formatting (delegated to templates).
"""
import os
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set, Any

from .config import FileEntry, CodebaseStats
from .constants import LANGUAGE_MAP


class ArchitectureAnalyzer:
    """Analyzes codebase structure and detects patterns, returning raw data."""

    def __init__(self, entries: List[FileEntry], stats: CodebaseStats):
        """
        Initialize analyzer.

        Args:
            entries: List of file entries
            stats: Codebase statistics
        """
        self.entries = entries
        self.stats = stats

    def analyze_data(self) -> Dict[str, Any]:
        """
        Perform complete architecture analysis and return raw data.
        """
        # Calculate depth distribution first to update self.stats.max_depth
        depth_dist = self._get_depth_distribution()

        return {
            "components": self._get_components(),
            "distribution": self._get_distribution(),
            "patterns": self._get_patterns(),
            "max_depth": self.stats.max_depth,
            "depth_distribution": depth_dist
        }

    def _get_components(self) -> List[Dict[str, Any]]:
        """Identify top-level components relative to the entries."""
        if not self.entries:
            return []

        # Find the common path to determine the root
        all_paths = [Path(e.path) for e in self.entries]
        root_path = Path(os.path.commonpath([str(p) for p in all_paths]))

        results = []
        top_dirs = set()

        for entry in self.entries:
            try:
                # Calculate relative path from common root
                rel_path = Path(entry.path).relative_to(root_path)
                if len(rel_path.parts) > 1:
                    top_dirs.add(rel_path.parts[0])
            except ValueError:
                continue

        for dir_name in sorted(top_dirs):
            # Count files belonging to this component
            count = sum(1 for e in self.entries if e.is_file and dir_name in Path(e.path).parts)
            results.append({"name": dir_name, "count": count})

        return results

    def _get_depth_distribution(self) -> Dict[int, int]:
        """Count files at each directory depth level and sync max_depth."""
        depth_counts = defaultdict(int)
        for e in self.entries:
            if e.is_file:
                depth_counts[e.depth] += 1

        if depth_counts:
            self.stats.max_depth = max(depth_counts.keys())

        return dict(sorted(depth_counts.items()))

    def _get_distribution(self) -> List[Dict[str, Any]]:
        """Get file distribution by extension and language."""
        results = []
        if not self.stats.files_by_ext:
            return results

        # Sort by count descending
        sorted_exts = sorted(
            self.stats.files_by_ext.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for ext, count in sorted_exts:
            lang = LANGUAGE_MAP.get(ext, "unknown")
            percentage = (count / self.stats.total_files * 100) if self.stats.total_files > 0 else 0
            results.append({
                "ext": ext,
                "lang": lang,
                "count": count,
                "percentage": round(percentage, 1)
            })
        return results

    def _get_patterns(self) -> List[str]:
        """Detect common design patterns based on filenames."""
        dir_files: Dict[str, Set[str]] = defaultdict(set)
        for entry in self.entries:
            if entry.is_file:
                parent = str(Path(entry.path).parent)
                filename = Path(entry.path).name.lower()
                dir_files[parent].add(filename)

        detected = []
        patterns_map = {
            'MVC': {
                'indicators': ['model.py', 'view.py', 'controller.py'],
                'description': 'Model-View-Controller pattern detected'
            },
            'Testing': {
                'indicators': ['test_', '__test__', 'tests.py', 'test.py'],
                'description': 'Organized test structure'
            },
            'Configuration': {
                'indicators': ['.env', 'config.py', 'settings.py', 'config.yml', 'pyproject.toml'],
                'description': 'Centralized configuration files'
            },
            'Documentation': {
                'indicators': ['readme.md', 'docs/', 'documentation/'],
                'description': 'Structured documentation'
            },
            'API': {
                'indicators': ['routes.py', 'api.py', 'endpoints.py', 'views.py'],
                'description': 'API/Routes architecture'
            },
            'Database': {
                'indicators': ['models.py', 'schema.py', 'migrations/', 'db.py'],
                'description': 'Persistence/Database layer'
            },
        }

        for pattern_info in patterns_map.values():
            for files in dir_files.values():
                if any(any(ind in f for f in files) for ind in pattern_info['indicators']):
                    detected.append(pattern_info['description'])
                    break

        return sorted(list(set(detected)))
