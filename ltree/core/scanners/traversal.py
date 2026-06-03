# ltree/core/scanners/traversal.py
import os
import sys
from pathlib import Path

from ltree.core.config import TreeConfig
from ltree.core.models import TreeNode, NodeType
from ltree.core.metadata import MetadataPipeline
from ltree.core.scanners.filters import CompositeFilter
from ltree.core.scanners.sorting import sort_entries
from ltree.core.scanners.subtree import count_subtree


def traverse_path(
    path: Path,
    config: TreeConfig,
    max_depth: int | None = None,
    curr_depth: int = 0,
    pipeline: MetadataPipeline | None = None,
    node_filter: CompositeFilter | None = None,
) -> TreeNode | None:
    node_filter = node_filter or CompositeFilter()

    try:
        ntype = NodeType.DIR if path.is_dir() else NodeType.FILE
    except OSError as e:
        print(f"Error: Failed to scan '{path}': {e}", file=sys.stderr)
        return None

    node = TreeNode(path=path, ntype=ntype)

    if pipeline:
        pipeline.execute(node, config)

    if ntype == NodeType.FILE:
        if not pipeline:
            try:
                node.size = path.stat().st_size
            except OSError:
                node.size = 0
        return node

    try:
        with os.scandir(str(path)) as it:
            sorted_entries = sort_entries(list(it), config)

            for entry in sorted_entries:
                entry_path = Path(entry.path)
                is_dir = entry.is_dir()

                if node_filter.should_exclude(entry_path, is_dir, config):
                    continue

                # visible file
                if not is_dir:
                    f_size = entry.stat().st_size

                    if config.folders_only:
                        node.stats.hidden_files += 1
                        node.stats.hidden_size += f_size
                        continue

                    node.stats.visible_files += 1

                    child = TreeNode(path=entry_path, ntype=NodeType.FILE)
                    if pipeline:
                        pipeline.execute(child, config)
                    node.children.append(child)
                    continue

                # visible folder
                node.stats.visible_dirs += 1

                if max_depth is not None and curr_depth >= max_depth:
                    # hidden folders & files
                    h_dirs, h_files, h_size = count_subtree(entry_path, config)
                    child = TreeNode(path=entry_path, is_truncated=True)

                    if pipeline:
                        pipeline.execute(child, config)

                    child.stats.hidden_dirs = h_dirs
                    child.stats.hidden_files = h_files
                    child.size = h_size

                    node.children.append(child)
                    continue

                child = traverse_path(
                    entry_path,
                    config,
                    max_depth,
                    curr_depth + 1,
                    pipeline,
                    node_filter,
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
