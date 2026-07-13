# ltree/core/scanners/subtree.py
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.core.scanners.filters import CompositeFilter
from ltree.core.scanners.models import FilterContext as FCTX

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.scanners.filters import NodeFilter


def count_subtree(
    path: Path, config: TreeConfig, node_filter: NodeFilter | None = None
) -> tuple[int, int, int]:
    cache_key = str(path)

    if cache_key in config._subtree_cache:
        return config._subtree_cache[cache_key]

    node_filter = node_filter or CompositeFilter()

    total_dirs = 0
    total_files = 0
    total_size = 0

    stack: list[Path] = [path]

    while stack:
        curr = stack.pop()

        try:
            with os.scandir(curr) as entries:
                for entry in entries:
                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                    except OSError:
                        continue

                    entry_path = Path(entry.path)

                    if node_filter.should_exclude(FCTX(entry_path, is_dir, config)):
                        continue

                    if is_dir:
                        total_dirs += 1
                        stack.append(entry_path)
                    else:
                        total_files += 1
                        try:
                            total_size += entry.stat(follow_symlinks=False).st_size
                        except OSError:
                            pass
        except OSError:
            continue

    res = (total_dirs, total_files, total_size)
    config._subtree_cache[cache_key] = res
    return res
