# ltree/tree/filters/sorting.py
from typing import TYPE_CHECKING

from ltree.tree.filters.base import TreeFilter

if TYPE_CHECKING:
    from ltree.tree.models import TreeNode


class SortFilter(TreeFilter):
    def __init__(self, dirs_first: bool = False):
        self.dirs_first = dirs_first

    def apply(self, root: "TreeNode") -> "TreeNode":
        self._sort_recursive(root)
        return root

    def _sort_recursive(self, node: "TreeNode"):
        if not node.is_dir:
            return

        node.children.sort(
            key=lambda n: (
                not n.is_dir if self.dirs_first else False,
                n.name.lower(),
            )
        )

        for child in node.children:
            self._sort_recursive(child)
