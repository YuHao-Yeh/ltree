# tests/test_scanners/test_aggregate.py
from ltree.core.models import TreeNode, NodeType, Stats
from ltree.core.scanners.aggregation import aggregate_tree


# =======================================================================#
# Test: aggregate_tree()
# =======================================================================#
def test_aggregate_tree_file_node():
    file_node = TreeNode(path="main.py", ntype=NodeType.FILE)
    file_node.size = 100
    aggregate_tree(file_node)
    assert file_node.size == 100


def test_aggregate_tree_truncated_node():
    truncated = TreeNode(path="sub_dir", ntype=NodeType.DIR, is_truncated=True)
    truncated.stats.hidden_size = 500
    aggregate_tree(truncated)

    assert truncated.size == 500


# =======================================================================#
# Test: aggregate_reset()
# =======================================================================#
def test_aggregate_tree_structure():
    # root/             (dir, hidden size=5 bytes)
    # ├── level1/       (dir)
    # │   └── file2.txt (file, 20 bytes)
    # └── file1.txt     (file, 10 bytes)
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.stats = Stats()

    level1 = TreeNode(path="root/level1", ntype=NodeType.DIR)
    level1.stats = Stats(visible_files=1)
    root.stats.visible_dirs += 1
    file2 = TreeNode(path="root/level1/file2.txt", ntype=NodeType.FILE)
    file2.size = 20
    level1.stats.visible_files += 1
    level1.children.append(file2)

    file1 = TreeNode(path="root/file1.txt", ntype=NodeType.FILE)
    file1.size = 10
    root.stats.visible_files += 1

    root.children.extend([level1, file1])
    root.stats.hidden_size = 5

    aggregate_tree(root)

    # hidden_size (5) + file1 (10) + level1 (20) = 35
    assert root.size == 35
    assert level1.size == 20

    assert root.stats.visible_dirs == 1
    assert root.stats.visible_files == 2
