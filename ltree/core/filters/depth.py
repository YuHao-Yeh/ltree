# ltree/core/filters/depth.py
from typing import TYPE_CHECKING

from ltree.core.filters.base import TreeFilter
from ltree.core.models import Stats

if TYPE_CHECKING:
    from ltree.core.models import TreeNode


class MaxDepthFilter(TreeFilter):
    def __init__(self, max_depth: int):
        self.max_depth = max_depth

    def apply(self, root: "TreeNode") -> "TreeNode":
        self._prune_recursive(root, 0)
        return root

    def _prune_recursive(self, node: "TreeNode", curr_depth: int):
        if not node.is_dir:
            return

        if node.is_truncated:
            return

        # TODO: Decouple aggregation from filter
        if curr_depth >= self.max_depth:
            # 1. Calculate the statistics of the pruned subtree
            h_stats = self._calculate_subtree_stats(node)

            # 2. Prune and mark child node
            node.children = []
            node.is_truncated = True
            node.stats.hidden_dirs = h_stats.hidden_dirs
            node.stats.hidden_files = h_stats.hidden_files
            node.stats.hidden_size = h_stats.hidden_size
            node.size = h_stats.hidden_size
            return

        for child in node.children:
            self._prune_recursive(child, curr_depth + 1)

    def _calculate_subtree_stats(self, node: "TreeNode") -> Stats:
        hidden_stats: Stats = Stats(
            hidden_dirs=node.stats.hidden_dirs,
            hidden_files=node.stats.hidden_files,
            hidden_size=node.stats.hidden_size,
        )

        def walk(n: "TreeNode"):
            nonlocal hidden_stats
            for child in n.children:
                if child.is_dir:
                    hidden_stats += child.stats
                    hidden_stats.hidden_dirs += 1

                    if not child.is_truncated:
                        hidden_stats.hidden_size += child.size
                        walk(child)
                else:
                    hidden_stats.hidden_files += 1
                    hidden_stats.hidden_size += child.size

        walk(node)
        return hidden_stats
