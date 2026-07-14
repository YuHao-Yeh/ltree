# ltree/tree/scanner/aggregation.py
from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ltree.tree.models import TreeNode


def aggregate_tree(node: TreeNode) -> None:
    if not node.is_dir:
        return

    node.stats.reset_visible()

    if node.is_truncated:
        node.size = node.stats.hidden_size
        return

    total_size = node.stats.hidden_size

    for child in node.children:
        if child.is_dir:
            aggregate_tree(child)

            node.stats.visible_dirs += 1
            node.stats += child.stats

            total_size += child.size

        else:
            node.stats.visible_files += 1
            total_size += child.size

    node.size = total_size
