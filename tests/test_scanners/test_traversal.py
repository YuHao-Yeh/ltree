# tests/test_scanners/test_traversal.py
import os
import pytest
import stat
from unittest.mock import patch, MagicMock

from ltree.core.config import TreeConfig
from ltree.core.models import TreeNode
from ltree.core.metadata import MetadataPipeline
from ltree.core.scanners.traversal import traverse_path


# =======================================================================#
# Fixture
# =======================================================================#
# tmp_path/
# ├── level1/           (dir)
# │   ├── file2.txt     (file, 20 bytes)
# │   └── file3.txt     (file, 5 bytes)
# └── file1.txt         (file, 10 bytes)
# =======================================================================#
@pytest.fixture
def test_dir(tmp_path):
    level1 = tmp_path / "level1"
    level1.mkdir()
    (level1 / "file2.txt").write_text("01234567890123456789")
    (level1 / "file3.txt").write_text("abcde")

    (tmp_path / "file1.txt").write_text("0123456789")
    return tmp_path


# =======================================================================#
# tmp_path/
# └── file1.txt     (file, 4 bytes)
# =======================================================================#
@pytest.fixture
def test_file(tmp_path):
    fp = tmp_path / "file1.txt"
    fp.write_text("data")
    return fp


# =======================================================================#
# Test: traverse_path()
# =======================================================================#
def test_traverse_path_single_file(test_file, capsys):
    config = TreeConfig()

    # Case 1: scan single file
    node = traverse_path(test_file, config)
    assert node is not None
    assert node.is_dir is False
    assert node.size == 4

    # Case 2: OSError
    with patch("pathlib.Path.is_dir", side_effect=OSError):
        node_os_err = traverse_path(test_file, config)
        assert node_os_err is None
        captured = capsys.readouterr()
        assert "Error: Failed to scan" in captured.err

    # Case 3: stat OSError
    class MockStatResult:
        st_mode = stat.S_IFREG | 0o644

        @property
        def st_size(self):
            raise OSError("Stat size failed")

    with patch("pathlib.Path.stat", return_value=MockStatResult()):
        node_stat_err = traverse_path(test_file, config)
        assert node_stat_err is not None
        assert node_stat_err.size == 0


def test_traverse_path_with_pipeline(test_file):
    config = TreeConfig()

    pipeline = MagicMock(spec=MetadataPipeline)
    node = traverse_path(test_file, config, pipeline=pipeline)

    pipeline.execute.assert_called_once_with(node, config)


def test_traverse_path_file_with_pipeline(test_dir):
    config = TreeConfig()

    pipeline = MagicMock(spec=MetadataPipeline)
    traverse_path(test_dir, config, pipeline=pipeline)

    pipeline.execute.call_count == 5
    calls = pipeline.execute.call_args_list
    child_node_arg = calls[1][0][0]

    assert isinstance(child_node_arg, TreeNode)
    assert child_node_arg.is_dir is False
    assert child_node_arg.path == test_dir / "file1.txt"


def test_traverse_path_dir_with_pipeline(test_dir):
    config = TreeConfig()
    mock_pipeline = MagicMock()

    traverse_path(test_dir, config, max_depth=0, pipeline=mock_pipeline)

    assert mock_pipeline.execute.call_count == 3
    assert mock_pipeline.execute.call_args_list


def test_traverse_path_exclustion(test_dir):
    config = TreeConfig()
    config.exclude_files.add("file3.txt")

    node = traverse_path(test_dir, config)

    assert len(node.children) == 2


def test_traverse_path_folders_only(test_dir):
    config = TreeConfig()
    config.folders_only = True

    node = traverse_path(test_dir, config)

    assert all(c.is_dir for c in node.children)
    assert node.stats.hidden_files == 1
    assert node.stats.hidden_size == 10


def test_traverse_path_max_depth_truncation(test_dir):
    config = TreeConfig()
    config.root_path = str(test_dir)

    node = traverse_path(test_dir, config, max_depth=0)

    truncated_child = next(c for c in node.children if c.name == "level1")
    assert truncated_child.is_truncated is True
    assert truncated_child.stats.hidden_files == 2
    assert truncated_child.stats.hidden_dirs == 0
    assert truncated_child.stats.hidden_size == 25


def test_traverse_path_permission_error(tmp_path, capsys):
    config = TreeConfig()

    with patch("os.scandir", side_effect=PermissionError):
        node = traverse_path(tmp_path, config)

    assert node is None
    captured = capsys.readouterr()
    assert "Error: No permission for the path" in captured.err


def test_traverse_path_no_next_child(test_dir, capsys):
    config = TreeConfig()
    original_scandir = os.scandir

    def mock_scandir(path_str):
        if "level1" in path_str:
            raise PermissionError("No permission for level1")
        return original_scandir(path_str)

    with patch("os.scandir", side_effect=mock_scandir):
        node = traverse_path(test_dir, config)

    child_names = [c.name for c in node.children]
    assert len(child_names) == 1
    assert "level1" not in child_names

    captured = capsys.readouterr()
    assert "Error: No permission for the path" in captured.err


def test_traverse_path_os_error(tmp_path, capsys):
    config = TreeConfig()

    with patch("os.scandir", side_effect=OSError("Disk reading error")):
        node = traverse_path(tmp_path, config)

    assert node is None
    captured = capsys.readouterr()
    assert "Error: Failed to scan" in captured.err
