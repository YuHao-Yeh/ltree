# ltree/tree/filters/folders.py
from typing import TYPE_CHECKING

from ltree.tree.filters.base import TreeFilter

if TYPE_CHECKING:
    from ltree.tree.models import TreeNode


class FoldersOnlyFilter(TreeFilter):
    def apply(self, root: "TreeNode") -> "TreeNode":
        return self._filter_recursive(root)

    def _filter_recursive(self, node: "TreeNode"):
        if not node.is_dir:
            return node

        filtered_children = []
        for child in node.children:
            if child.is_dir:
                self._filter_recursive(child)
                filtered_children.append(child)
            else:
                node.stats.hidden_files += 1
                node.stats.hidden_size += child.size

        node.children = filtered_children

        return node
