# tests/test_scanners/test_scanner.py
from unittest.mock import patch

from ltree.core.config import TreeConfig
from ltree.core.models import TreeNode, NodeType
from ltree.core.scanners.scanner import Scanner, scan_tree


scanner_path = "ltree.core.scanners.scanner"


# =======================================================================#
# Tests: Scanner
# =======================================================================#
def test_scanner_non_existent_path(capsys):
    config = TreeConfig()
    scanner = Scanner(config)

    res = scanner.scan("non_existent_path_999")
    assert res is None

    captured = capsys.readouterr()
    assert "Error: Path 'non_existent_path_999' does not exist." in captured.err


@patch(f"{scanner_path}.traverse_path")
@patch(f"{scanner_path}.aggregate_tree")
def test_scanner_success_flow(mock_aggregate, mock_traverse, tmp_path):
    config = TreeConfig()
    scanner = Scanner(config)

    root_node = TreeNode(path=tmp_path, ntype=NodeType.DIR)
    mock_traverse.return_value = root_node

    res = scanner.scan(tmp_path)
    assert res is root_node

    mock_traverse.assert_called_once()
    mock_aggregate.assert_called_once_with(root_node)
    assert config.root_path == str(tmp_path.resolve())


def test_scanner_no_root_node(tmp_path, capsys):
    config = TreeConfig()
    scanner = Scanner(config)

    with patch("os.scandir", side_effect=OSError):
        res = scanner.scan(tmp_path)

    captured = capsys.readouterr()
    assert "Error: Failed to scan" in captured.err

    assert res is None


# =======================================================================#
# Tests: scan_tree()
# =======================================================================#
@patch("ltree.core.scanners.scanner.Scanner.scan")
def test_scan_tree_wrapper(mock_scan, tmp_path):
    config = TreeConfig()
    scan_tree(tmp_path, config, max_depth=2)
    mock_scan.assert_called_once_with(tmp_path, max_depth=2)
