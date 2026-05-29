# ltree/core/scanner/aggregation.py
from ltree.core.models import TreeNode


def aggregate_tree(node: TreeNode) -> None:
    if not node.is_dir:
        return

    if node.is_truncated:
        return

    total_size = node.stats.hidden_size

    for child in node.children:
        aggregate_tree(child)
        total_size += child.size

        node.stats.visible_dirs += child.stats.visible_dirs
        node.stats.visible_files += child.stats.visible_files
        node.stats.hidden_dirs += child.stats.hidden_dirs
        node.stats.hidden_files += child.stats.hidden_files

    node.size = total_size
