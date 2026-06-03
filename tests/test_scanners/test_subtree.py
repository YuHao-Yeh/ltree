# tests/test_scanners/test_subtree.py
import pytest
from unittest.mock import patch

from ltree.core.config import TreeConfig
from ltree.core.scanners.subtree import count_subtree


# =======================================================================#
# Fixture
# =======================================================================#
# tmp_path/
# ├── sub_dir/          (dir)
# │   ├── file2.txt     (file, 20 bytes)
# │   └── file3.txt     (file, 26 bytes)
# ├── excluded_dir/     (dir)
# │   └── file4.txt     (file, 5 bytes)
# └── file1.txt         (file, 10 bytes)
# =======================================================================#
@pytest.fixture
def test_dir(tmp_path):
    sub = tmp_path / "sub_dir"
    sub.mkdir()
    (sub / "file2.txt").write_text("01234567890123456789")  # 20 bytes
    (sub / "file3.txt").write_text("abcdefghijklmnopqrstuvwxyz")  # 26 bytes

    ex_dir = tmp_path / "excluded_dir"
    ex_dir.mkdir()
    (ex_dir / "file4.txt").write_text("hello")  # 5 bytes

    (tmp_path / "file1.txt").write_text("0123456789")  # 10 bytes
    return tmp_path


# =======================================================================#
# Test: count_subtree()
# =======================================================================#
def test_count_subtree_basic_scanning(test_dir):
    config = TreeConfig()
    config.root_path = str(test_dir)
    config.exclude_dirs = {"excluded_dir"}
    config.exclude_files = {"file2.txt"}

    dirs, files, size = count_subtree(test_dir, config)

    # Scanned dir: sub_dir/
    # Scanned file: file1.txt (10), sub_dir/file3.txt (26) = 2
    # Total size: 10 + 26 = 36
    assert dirs == 1
    assert files == 2
    assert size == 36

    assert str(test_dir) in config._subtree_cache
    assert config._subtree_cache[str(test_dir)] == (1, 2, 36)


def test_count_subtree_cache_hit(test_dir):
    config = TreeConfig()
    cache_key = str(test_dir)

    config._subtree_cache[cache_key] = (10, 20, 300)

    dirs, files, size = count_subtree(test_dir, config)

    assert dirs == 10
    assert files == 20
    assert size == 300


def test_count_subtree_file_stat_os_error(test_dir):
    config = TreeConfig()
    config.root_path = str(test_dir)
    config.exclude_dirs = {"excluded_dir"}

    with patch("pathlib.Path.stat", side_effect=OSError):
        dirs, files, size = count_subtree(test_dir, config)

        assert dirs == 1
        assert files == 3
        assert size == 0
