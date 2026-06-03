# tests/test_filters/test_tree_filters.py
import pytest
from pathlib import Path

from ltree.core.models import TreeNode, NodeType, Stats
from ltree.core.config import TreeConfig
from ltree.core.filters import (
    MaxDepthFilter,
    FoldersOnlyFilter,
    SortFilter,
    get_default_filter_pipeline,
)


# ======================================================================= #
# Fixtures
# ======================================================================= #
# root/
# ├── b_dir/                (dir)
# │   └── file_b.txt        (file, 20 bytes)
# ├── a_dir/                (dir)
# │   ├── file_a.txt        (file, 10 bytes)
# │   └── nested_dir/       (dir)
# │       └── file_c.txt    (file, 50 bytes)
# └── file_root.txt         (file, 5 bytes)
# ======================================================================= #
@pytest.fixture
def setup_subtree():
    root = TreeNode(path=Path("root"), ntype=NodeType.DIR)

    b_dir = TreeNode(path=Path("root/b_dir"), ntype=NodeType.DIR)
    file_b = TreeNode(path=Path("root/b_dir/file_b.txt"), ntype=NodeType.FILE)
    file_b.size = 20
    b_dir.stats.visible_files += 1
    b_dir.children.append(file_b)

    a_dir = TreeNode(path=Path("root/a_dir"), ntype=NodeType.DIR)
    file_a = TreeNode(path=Path("root/a_dir/file_a.txt"), ntype=NodeType.FILE)
    file_a.size = 10

    nested_dir = TreeNode(path=Path("root/a_dir/nested_dir"), ntype=NodeType.DIR)
    file_c = TreeNode(
        path=Path("root/a_dir/nested_dir/file_c.txt"), ntype=NodeType.FILE
    )
    file_c.size = 50
    nested_dir.stats.visible_files += 1
    nested_dir.children.append(file_c)
    a_dir.stats.visible_files += 1
    a_dir.stats.visible_dirs += 1
    a_dir.children.extend([file_a, nested_dir])

    file_root = TreeNode(path=Path("root/file_root.txt"), ntype=NodeType.FILE)
    file_root.size = 5

    root.stats.visible_dirs = 2
    root.stats.visible_files = 4
    root.children.extend([b_dir, a_dir, file_root])
    return root


# ======================================================================= #
# Test: MaxDepthFilter
# ======================================================================= #
def test_max_depth_filter_truncation(setup_subtree):
    f = MaxDepthFilter(max_depth=1)
    root = f.apply(setup_subtree)

    b_dir = next(c for c in root.children if c.name == "b_dir")
    a_dir = next(c for c in root.children if c.name == "a_dir")

    assert b_dir.is_truncated is True
    assert len(b_dir.children) == 0
    assert b_dir.stats.hidden_files == 1
    assert b_dir.stats.hidden_dirs == 0
    assert b_dir.size == 20

    assert a_dir.is_truncated is True
    assert len(a_dir.children) == 0
    assert a_dir.stats.hidden_dirs == 1
    assert a_dir.stats.hidden_files == 2
    assert a_dir.size == 60


def test_max_depth_filter_skips_already_truncated():
    node = TreeNode(path=Path("truncated_dir"), ntype=NodeType.DIR, is_truncated=True)
    node.stats = Stats(hidden_files=10, hidden_dirs=5)
    node.size = 1000

    f = MaxDepthFilter(max_depth=0)
    res = f.apply(node)

    assert res.is_truncated is True
    assert res.stats.hidden_files == 10
    assert res.stats.hidden_dirs == 5
    assert res.size == 1000


def test_calculate_subtree_stats_truncated_child():
    """
    root/       (dir)
    └── src/    (dir, 100 bytes, truncated)
    """
    root = TreeNode(path="root", ntype=NodeType.DIR)

    src = TreeNode(path="root/src", ntype=NodeType.DIR, is_truncated=True)
    src.stats = Stats(hidden_dirs=2, hidden_files=5, hidden_size=100)
    src.size = 100
    root.stats.visible_dirs += 1
    root.children.append(src)

    filter = MaxDepthFilter(0)

    stats = filter._calculate_subtree_stats(root)
    print(stats)

    assert stats.hidden_dirs == 3
    assert stats.hidden_files == 5

    assert stats.hidden_size == 100


# ======================================================================= #
# Tests: FoldersOnlyFilter
# ======================================================================= #
def test_folders_only_filter(setup_subtree):
    f = FoldersOnlyFilter()
    root = f.apply(setup_subtree)

    assert all(c.is_dir for c in root.children)
    assert root.stats.hidden_files == 1
    assert root.stats.hidden_size == 5


def test_folders_only_filter_file():
    node = TreeNode(path=Path("test_file.txt"), ntype=NodeType.FILE)
    node.size = 10

    f = FoldersOnlyFilter()
    root = f.apply(node)

    assert root == node


# ======================================================================= #
# Tests: SortFilter
# ======================================================================= #
def test_sort_filter_alphabetical_and_dirs_first(setup_subtree):
    f = SortFilter(dirs_first=True)
    root = f.apply(setup_subtree)

    # Order: a_dir -> b_dir -> file_root.txt
    assert [c.name for c in root.children] == ["a_dir", "b_dir", "file_root.txt"]


# ======================================================================= #
# Tests: FilterPipeline
# ======================================================================= #
def test_filter_pipeline_get_default(setup_subtree):
    config = TreeConfig()

    config.folders_only = True
    config.dirs_first = True
    pipeline = get_default_filter_pipeline(config=config, max_depth=1)

    root = pipeline.apply(setup_subtree)

    # 1. MaxDepth prune level 1 -> truncated dir
    # 2. FoldersOnly remove file_root.txt -> a_dir, b_dir left
    # 3. SortFilter sort a_dir, b_dir
    assert all(c.is_truncated for c in root.children)
    assert [c.name for c in root.children] == ["a_dir", "b_dir"]


def test_filter_pipeline_get_default_only_dir_first(setup_subtree):
    config = TreeConfig()

    config.folders_only = False
    pipeline = get_default_filter_pipeline(config=config, max_depth=None)

    root = pipeline.apply(setup_subtree)

    assert [c.name for c in root.children] == ["a_dir", "b_dir", "file_root.txt"]
