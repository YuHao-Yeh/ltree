# tests/test_renderers/test_utils.py
from ltree.core.models import TreeNode, Stats, NodeType
from ltree.core.config import TreeConfig
from ltree.serializers import TreeSerializer
from ltree.renderers.utils import print_stats


# =======================================================================#
# Test: print stats
# =======================================================================#
def test_print_stats(capsys):
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.stats = Stats(visible_dirs=1, visible_files=2, hidden_dirs=0, hidden_files=0)

    # normal
    config = TreeConfig()
    node = TreeSerializer(config).serialize(root)
    print_stats(node, config)

    captured = capsys.readouterr()
    assert "Summary" in captured.out
    assert "1 directories" in captured.out
    assert "2 files" in captured.out

    # show size
    config.show_size = True
    node = TreeSerializer(config).serialize(root)
    print_stats(node, config)

    captured = capsys.readouterr()
    assert "0 B" in captured.out


def test_print_stats_rich(capsys):
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.stats = Stats(visible_dirs=1, visible_files=2, hidden_dirs=0, hidden_files=0)

    # normal
    config = TreeConfig()
    node = TreeSerializer(config).serialize(root)
    print_stats(node, config, fmt="rich")

    captured = capsys.readouterr()
    assert "Summary" in captured.out
    assert "1 directories" in captured.out
    assert "2 files" in captured.out

    # show size
    config.show_size = True
    node = TreeSerializer(config).serialize(root)
    print_stats(node, config, fmt="rich")

    captured = capsys.readouterr()
    assert "0 bytes" in captured.out
