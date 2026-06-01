import os
import stat
from unittest.mock import patch

from ltree.core.scanner import build_metadata
from ltree.core.models import TreeNode


# ======================================================================= #
# Test: build_metadata
# ======================================================================= #


def test_build_metadata_regular_file():
    node = TreeNode(path="/dummy/test_document.TXT")

    # Simulate permissions for a regular file (stat.S_IFREG) with 0o644.
    mock_mode = stat.S_IFREG | 0o644
    mock_stat = os.stat_result((mock_mode, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    with patch("os.lstat", return_value=mock_stat):
        build_metadata("/dummy/test_document.TXT", node)

    assert node.is_symlink is False
    assert node.is_executable is False
    assert node.extension == ".txt"
    assert node.permissions.startswith("-rw-")


def test_build_metadata_symlink():
    node = TreeNode(path="/dummy/my_symlink")

    mock_mode = stat.S_IFLNK | 0o777
    mock_stat = os.stat_result((mock_mode, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    with patch("os.lstat", return_value=mock_stat):
        build_metadata("/dummy/my_symlink", node)

    assert node.is_symlink is True
    assert node.permissions.startswith("l")


def test_build_metadata_executable():
    node = TreeNode(path="/dummy/runner.sh")

    mock_mode = stat.S_IFREG | stat.S_IXUSR | 0o755
    mock_stat = os.stat_result((mock_mode, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    with patch("os.lstat", return_value=mock_stat):
        build_metadata("/dummy/runner.sh", node)

    assert node.is_executable is True


def test_build_metadata_os_error_handling():
    node = TreeNode(path="/dummy/missing_file.txt")

    with patch("os.lstat", side_effect=OSError("File target not found")):
        build_metadata("/dummy/missing_file.txt", node)

    assert node.is_symlink is False
    assert node.is_executable is False
    assert node.permissions == ""
    assert node.extension == ""
