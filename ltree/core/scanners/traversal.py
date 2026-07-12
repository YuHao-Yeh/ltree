# ltree/core/scanners/traversal.py
from __future__ import annotations

import os
import stat as stat_module
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.core.models import TreeNode, NodeType
from ltree.core.scanners.filters import CompositeFilter
from ltree.core.scanners.models import FilterContext as FCTX
from ltree.core.scanners.sorting import sort_entries
from ltree.core.scanners.subtree import count_subtree

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.metadata import MetadataPipeline


def traverse_path(
    path: Path,
    config: TreeConfig,
    max_depth: int | None = None,
    curr_depth: int = 0,
    pipeline: MetadataPipeline | None = None,
    node_filter: CompositeFilter | None = None,
    *,
    stat: os.stat_result | None = None,
) -> TreeNode | None:
    node_filter = node_filter or CompositeFilter()

    if stat is None:
        try:
            stat = path.lstat()
        except OSError as e:
            print(f"Error: Failed to scan '{path}': {e}", file=sys.stderr)
            return None

    ntype = NodeType.DIR if stat_module.S_ISDIR(stat.st_mode) else NodeType.FILE
    node = TreeNode(path=path, ntype=ntype)

    if pipeline:
        pipeline.execute(node, stat=stat)

    if ntype == NodeType.FILE:
        if not pipeline:
            node.size = stat.st_size
        return node

    try:
        with os.scandir(path) as it:
            sorted_entries = sort_entries(list(it), config)

            for entry in sorted_entries:
                entry_path = Path(entry.path)

                try:
                    entry_stat = entry.stat(follow_symlinks=False)
                    is_dir = stat_module.S_ISDIR(entry_stat.st_mode)
                except OSError as e:
                    print(
                        f"Warning: Failed to stat '{entry.path}': {e}",
                        file=sys.stderr,
                    )
                    continue

                if node_filter.should_exclude(FCTX(entry_path, is_dir, config)):
                    continue

                # visible file
                if not is_dir:
                    f_size = entry_stat.st_size

                    if config.folders_only:
                        node.stats.hidden_files += 1
                        node.stats.hidden_size += f_size
                        continue

                    child = TreeNode(path=entry_path, ntype=NodeType.FILE)
                    if pipeline:
                        pipeline.execute(child, stat=entry_stat)
                    node.children.append(child)
                    continue

                # visible folder
                if max_depth is not None and curr_depth + 1 >= max_depth:
                    # hidden folders & files
                    h_dirs, h_files, h_size = count_subtree(entry_path, config)
                    child = TreeNode(path=entry_path, is_truncated=True)

                    if pipeline:
                        pipeline.execute(child, stat=entry_stat)

                    child.stats.hidden_dirs = h_dirs
                    child.stats.hidden_files = h_files
                    child.stats.hidden_size = h_size

                    node.children.append(child)
                    continue

                child = traverse_path(
                    entry_path,
                    config,
                    max_depth,
                    curr_depth + 1,
                    pipeline,
                    node_filter,
                    stat=entry_stat,
                )
                if child:
                    node.children.append(child)
    except PermissionError:
        print(f"Error: No permission for the path '{path}'", file=sys.stderr)
        return None
    except OSError as e:
        print(f"Error: Failed to scan '{path}': {e}", file=sys.stderr)
        return None

    return node
