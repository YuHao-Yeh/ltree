import argparse
import pytest
from unittest.mock import patch

from ltree._core.utils import is_excluded, count_subtree
from ltree.core.config import TreeConfig


# =======================================================================#
# Fixture
# =======================================================================#
# tmp_path/
# ├── file1.txt         (file, 10 bytes)
# ├── .hidden_file      (file, 5 bytes)
# └── sub_dir/          (dir)
#     ├── file2.txt     (file, 20 bytes)
#     └── __pycache__/  (dir)
#         └── cache.pyc (file, 100 bytes)
# =======================================================================#
@pytest.fixture
def setup_subtree(tmp_path):
    (tmp_path / "file1.txt").write_text("0123456789")  # 10 bytes
    (tmp_path / ".hidden").write_text("12345")  # 5 bytes

    sub = tmp_path / "sub_dir"
    sub.mkdir()
    (sub / "file2.txt").write_text("01234567890123456789")  # 20 bytes
    sub = tmp_path / "sub_dir"

    pycache = sub / "__pycache__"
    pycache.mkdir()
    (pycache / "cache.pyc").write_text("a" * 100)  # 100 bytes


@pytest.fixture
def base_args():
    return argparse.Namespace(
        start_path=".",
        output="-",
        ex_dirs=[],
        ex_files=[],
        ex_ext=[],
        ex_prefix=[],
        add_dirs=[],
        add_files=[],
        color=False,
        show_size=False,
        full_path=False,
        human_readable=False,
        show_all=False,
        folders_only=False,
        no_ignore=True,
        regex_exclude=[],
        dirs_first=False,
        show_ellipsis=False,
        theme="none",
    )


# =======================================================================#
# Test: is_excluded
# =======================================================================#
def test_is_excluded_priority_1():
    config = TreeConfig()
    config.added_items.add(".gitignore")
    assert is_excluded(".gitignore", is_dir=False, config=config, rel_path=".") is False


def test_is_excluded_priority_2(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log\nnode_modules/")

    config = TreeConfig()
    config.load_gitignore(str(tmp_path))

    assert is_excluded("test.log", False, config, "test.log")
    assert is_excluded("node_modules", True, config, "node_modules")
    assert is_excluded("src", True, config, "src") is False


def test_is_excluded_priority_3(base_args):
    config = TreeConfig()
    base_args.regex_exclude = [r"temp_\d+"]
    base_args.no_ignore = False
    config.apply_args(base_args)

    assert is_excluded("temp_123", True, config, "temp_123")
    assert is_excluded("temp_abc", True, config, "temp_abc") is False


def test_is_excluded_priority_4():
    config = TreeConfig()
    rel_path = "."

    # default
    assert is_excluded("__pycache__", True, config, rel_path)
    assert is_excluded("errors", True, config, rel_path) is False
    assert is_excluded("main.py", False, config, rel_path) is False
    assert is_excluded(".DS_store", False, config, rel_path)
    assert is_excluded("error.log", False, config, rel_path)

    # file
    config.exclude_files.add("id_rsa")
    assert is_excluded("id_rsa", is_dir=False, config=config, rel_path=rel_path)

    # ext
    config.exclude_exts.add(".png")
    assert is_excluded("out.txt", False, config, rel_path) is False
    assert is_excluded("flow.png", False, config, rel_path)
    assert is_excluded("flow.jpg", False, config, rel_path) is False

    # prefix
    config.exclude_prefixes.add("tmp")
    assert is_excluded("tmp_data", True, config, rel_path)
    assert is_excluded("tmpfile.py", False, config, rel_path)

    # pattern
    config.exclude_files.add("*log")
    config._prepare_patterns()
    assert is_excluded("logging.txt", False, config, rel_path) is False
    assert is_excluded("record.log", False, config, rel_path)


def test_is_excluded_priority_5():
    config = TreeConfig()
    config.show_all = False
    rel_path = "."

    # Case A：show_all=False
    config.show_all = False
    assert is_excluded(".env", is_dir=False, config=config, rel_path=rel_path)
    assert is_excluded(".github", is_dir=True, config=config, rel_path=rel_path)

    # special case: current dir (".", "./")
    assert is_excluded(".", True, config, rel_path) is False
    assert is_excluded("./", True, config, rel_path) is False

    # Case B：show_all=True
    config.show_all = True
    assert is_excluded(".env", is_dir=False, config=config, rel_path=rel_path) is False


# =======================================================================#
# Test: count_subtree
# =======================================================================#
def test_count_subtree_logic(tmp_path, setup_subtree):
    # Case A: show_all = False
    config = TreeConfig()
    config.show_all = False
    dirs, files, size = count_subtree(str(tmp_path), config)

    assert dirs == 1  # sub_dir
    assert files == 2  # file1.txt, file2.txt
    assert size == 30  # 10 + 20

    # Case B: show_all = True
    config._subtree_cache.clear()
    config.show_all = True
    config.added_items.add("__pycache__")

    d, f, s = count_subtree(str(tmp_path), config)

    assert d == 2  # sub_dir/, __pycache__
    assert f == 4  # file1.txt, file2.txt, .hidden_file, cache.pyc
    assert s == 135


def test_count_subtree_cache(tmp_path, setup_subtree):
    config = TreeConfig()
    path_str = str(tmp_path)

    count_subtree(path_str, config)

    config._subtree_cache[path_str] = (10, 20, 300)

    d, f, s = count_subtree(path_str, config)
    assert d == 10
    assert f == 20
    assert s == 300


def test_count_subtree_permission_error(tmp_path, setup_subtree):
    config = TreeConfig()

    with patch("os.path.getsize", side_effect=PermissionError):
        dirs, files, size = count_subtree(str(tmp_path), config)
        assert size == 0
        assert dirs == 1
        assert files == 2
