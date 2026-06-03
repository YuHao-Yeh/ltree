# tests/test_legacy/test_legacy_scanner.py
import os
import platform
import pytest
from unittest.mock import patch

from ltree._core.scanner import scan_tree
from ltree.core.config import TreeConfig


# =======================================================================#
# Fixture
# =======================================================================#
# tmp_path/
# ├── __pycache__/      (dir)
# ├── .hidden_file      (file, 0 bytes)
# ├── file1.txt         (file, 10 bytes)
# └── level1/           (dir)
#     ├── file2.txt     (20 bytes)
#     └── level2/       (dir)
# =======================================================================#
@pytest.fixture
def setup_subtree(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    level1 = tmp_path / "level1"
    level1.mkdir()
    (level1 / "level2").mkdir()

    (tmp_path / ".hidden_file").write_text("")  # 0 bytes
    (tmp_path / "file1.txt").write_text("0123456789")  # 10 bytes
    (level1 / "file2.txt").write_text("01234567890123456789")  # 20 bytes


# =======================================================================#
# Test: Basic Tests
# =======================================================================#
def test_scan_tree_stats(tmp_path, setup_subtree):
    config = TreeConfig()
    root_node = scan_tree(str(tmp_path), config)

    assert root_node.stats.visible_files == 2  # file1, file2
    assert root_node.stats.visible_dirs == 2  # level1, level2
    assert root_node.size == 30  # 10 + 20


def test_scan_tree_file(tmp_path, setup_subtree):
    config = TreeConfig()

    fp = tmp_path / "file1.txt"
    f1_node = scan_tree(str(fp), config)

    assert f1_node.is_dir is False
    assert f1_node.size == 10


def test_scan_tree_system_root_fallback():
    config = TreeConfig()
    root_path = "C:\\" if platform.system() == "Windows" else "/"

    with patch("os.scandir") as mock_scandir:
        mock_scandir.return_value.__enter__.return_value = []

        root_node = scan_tree(root_path, config, max_depth=0)

    assert root_node is not None
    assert root_node.name == root_path


# =======================================================================#
# Test: Options & Filtering Tests
# =======================================================================#
def test_scan_tree_show_all(tmp_path, setup_subtree):
    config = TreeConfig()
    config.show_all = True

    root_node = scan_tree(str(tmp_path), config)
    # visible: file1, file2, .hidden_file
    assert root_node.stats.visible_files == 3
    # visible: level1, level2
    assert root_node.stats.visible_dirs == 2


def test_scan_tree_max_depth(tmp_path, setup_subtree):
    config = TreeConfig()
    root_node = scan_tree(str(tmp_path), config, max_depth=0)

    # level1 should be truncated
    level1_node = next(c for c in root_node.children if c.name == "level1")
    assert level1_node.is_truncated is True
    assert root_node.size == 30


def test_scan_tree_folders_only_logic(tmp_path, setup_subtree):
    config = TreeConfig()
    config.folders_only = True
    node = scan_tree(str(tmp_path), config)

    assert all(c.is_dir for c in node.children)
    assert node.stats.visible_files == 0
    assert node.stats.hidden_files == 2
    assert node.size == 30


# =======================================================================#
# Test: Error Handling
# =======================================================================#
def test_scan_tree_path_not_exists(capsys):
    config = TreeConfig()
    scan_tree("non_existent_path_999", config)

    captured = capsys.readouterr()
    assert "Error: Path" in captured.err


def test_scan_tree_os_error_on_getsize(tmp_path, setup_subtree):
    config = TreeConfig()
    file_path = tmp_path / "file1.txt"

    with patch("os.path.getsize", side_effect=OSError):
        f1_node = scan_tree(str(file_path), config)
        assert f1_node.size == 0


def test_scan_tree_permission_error(tmp_path, capsys):
    config = TreeConfig()

    with patch("os.scandir", side_effect=PermissionError):
        scan_tree(str(tmp_path), config)
        captured = capsys.readouterr()
        assert "Error: No permission" in captured.err


def test_scan_tree_os_error(tmp_path, capsys):
    config = TreeConfig()

    with patch("os.scandir", side_effect=OSError):
        scan_tree(str(tmp_path), config)
        captured = capsys.readouterr()
        assert "Error: Failed to scan" in captured.err


def test_scan_tree_skip_none_child(tmp_path, capsys):
    (tmp_path / "dir_a").mkdir()
    (tmp_path / "dir_b").mkdir()

    config = TreeConfig()
    original_scandir = os.scandir

    def mocked_scandir(path):
        if os.path.basename(path) == "dir_b":
            raise PermissionError("Access Denied.")
        return original_scandir(path)

    with patch("os.scandir", side_effect=mocked_scandir):
        root_node = scan_tree(str(tmp_path), config)

    child_names = [c.name for c in root_node.children]
    assert "dir_a" in child_names
    assert "dir_b" not in child_names

    captured = capsys.readouterr()
    assert "Error: No permission for the path" in captured.err
    assert "dir_b" in captured.err

    assert root_node.stats.visible_dirs == 2
