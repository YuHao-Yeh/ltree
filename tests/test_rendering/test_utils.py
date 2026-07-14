# tests/test_rendering/test_utils.py
from ltree.config.config import TreeConfig
from ltree.rendering.utils import print_stats
from ltree.tree.models import TreeNode, Stats, NodeType


# ======================================================================= #
# Tests: print_stats()
# ======================================================================= #
def test_print_stats(capsys):
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.stats = Stats(visible_dirs=1, visible_files=2, hidden_dirs=0, hidden_files=0)

    # normal
    config = TreeConfig()
    print_stats(root, config)

    captured = capsys.readouterr()
    assert "Summary" in captured.out
    assert "1 directories" in captured.out
    assert "2 files" in captured.out

    # show size
    config.show_size = True
    print_stats(root, config)

    captured = capsys.readouterr()
    assert "0 B" in captured.out


def test_print_stats_rich(capsys):
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.stats = Stats(visible_dirs=1, visible_files=2, hidden_dirs=0, hidden_files=0)

    # normal
    config = TreeConfig()
    print_stats(root, config, fmt="rich")

    captured = capsys.readouterr()
    assert "Summary" in captured.out
    assert "1 directories" in captured.out
    assert "2 files" in captured.out

    # show size
    config.show_size = True
    print_stats(root, config, fmt="rich")

    captured = capsys.readouterr()
    assert "0 bytes" in captured.out
