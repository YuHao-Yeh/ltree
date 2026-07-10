# ltree/core/scanners/subtree.py
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.core.scanners.filters import CompositeFilter
from ltree.core.scanners.models import FilterContext as FCTX

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig


def count_subtree(path: Path, config: TreeConfig) -> tuple[int, int, int]:
    cache_key = str(path)

    if cache_key in config._subtree_cache:
        return config._subtree_cache[cache_key]

    node_filter = CompositeFilter()

    total_dirs = 0
    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(path):
        root_path = Path(root)

        # --- directories ---
        keep_dirs = []
        for dirname in dirs:
            dir_path = root_path / dirname

            if node_filter.should_exclude(FCTX(dir_path, True, config)):
                continue

            total_dirs += 1
            keep_dirs.append(dirname)
        dirs[:] = keep_dirs

        # --- files ---
        for filename in files:
            file_path = root_path / filename

            if node_filter.should_exclude(FCTX(file_path, False, config)):
                continue

            total_files += 1
            try:
                total_size += file_path.stat().st_size
            except OSError:
                pass

    res = (total_dirs, total_files, total_size)
    config._subtree_cache[cache_key] = res
    return res
