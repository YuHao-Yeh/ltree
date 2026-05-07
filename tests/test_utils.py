import io
import pytest
from unittest.mock import patch
from ltree.utils import is_excluded, count_subtree, write_line
from ltree.config import TreeConfig

#=======================================================================#
# Test: is_excluded
#=======================================================================#
def test_is_excluded_priority_1():
    config = TreeConfig()
    config.added_items.add(".gitignore")
    assert is_excluded(".gitignore", is_dir=False, config=config) is False

def test_is_excluded_priority_2():
    config = TreeConfig()
    
    # default
    assert is_excluded("__pycache__", True, config)
    assert is_excluded("errors", True, config) is False
    assert is_excluded("main.py", False, config) is False
    assert is_excluded(".DS_store", False, config)
    assert is_excluded("error.log", False, config)

    # file
    config.exclude_files.add("id_rsa")
    assert is_excluded("id_rsa", is_dir=False, config=config)

    # ext
    config.exclude_exts.add(".png")
    assert is_excluded("out.txt", False, config) is False
    assert is_excluded("flow.png", False, config)
    assert is_excluded("flow.jpg", False, config) is False

    # prefix
    config.exclude_prefixes.add("tmp")
    assert is_excluded("tmp_data", True, config)
    assert is_excluded("tmpfile.py", False, config)

    # pattern
    config.exclude_files.add("*log")
    config._prepare_patterns()
    assert is_excluded("logging.txt", False, config) is False
    assert is_excluded("record.log", False, config)

def test_is_excluded_priority_3():
    config = TreeConfig()
    config.show_all = False

    # Case A：show_all=False
    config.show_all = False
    assert is_excluded(".env", is_dir=False, config=config)
    assert is_excluded(".github", is_dir=True, config=config)

    # special case: current dir (".", "./")
    assert is_excluded(".", True, config) is False
    assert is_excluded("./", True, config) is False

    # Case B：show_all=True
    config.show_all = True
    assert is_excluded(".env", is_dir=False, config=config) is False

#=======================================================================#
# Fixture
#=======================================================================#
# tmp_path/
# ├── file1.txt         (file, 10 bytes)
# ├── .hidden_file      (file, 5 bytes)
# └── sub_dir/          (dir)
#     ├── file2.txt     (file, 20 bytes)
#     └── __pycache__/  (dir)
#         └── cache.pyc (file, 100 bytes)
#=======================================================================#
@pytest.fixture
def setup_subtree(tmp_path):
    (tmp_path / "file1.txt").write_text("0123456789")       # 10 bytes
    (tmp_path / ".hidden").write_text("12345")              # 5 bytes

    sub = tmp_path / "sub_dir"
    sub.mkdir()
    (sub / "file2.txt").write_text("01234567890123456789")  # 20 bytes
    sub = tmp_path / "sub_dir"
    
    pycache = sub / "__pycache__"
    pycache.mkdir()
    (pycache / "cache.pyc").write_text("a" * 100)           # 100 bytes


#=======================================================================#
# Test: count_subtree
#=======================================================================#
def test_count_subtree_logic(tmp_path, setup_subtree):
    # Case A: show_all = False
    config = TreeConfig()
    config.show_all = False
    dirs, files, size = count_subtree(str(tmp_path), config)

    assert dirs == 1    # sub_dir
    assert files == 2   # file1.txt, file2.txt
    assert size == 30   # 10 + 20

    # Case B: show_all = True
    config.subtree_cache.clear()
    config.show_all = True
    config.added_items.add("__pycache__")

    d, f, s = count_subtree(str(tmp_path), config)

    assert d == 2   # sub_dir/, __pycache__
    assert f == 4   # file1.txt, file2.txt, .hidden_file, cache.pyc
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

#=======================================================================#
# Test: write_line
#=======================================================================#
def test_write_line_success():
    mock_file = io.StringIO()
    
    test_text = "Hello Tree"
    write_line(mock_file, test_text)
    
    assert mock_file.getvalue() == "Hello Tree\n"

def test_write_line_none():
    try:
        write_line(None, "This should not crash")
    except AttributeError:
        pytest.fail("write_line raised AttributeError on None file")

def test_write_line_multiple_calls():
    mock_file = io.StringIO()
    
    write_line(mock_file, "Line 1")
    write_line(mock_file, "Line 2")
    
    assert mock_file.getvalue() == "Line 1\nLine 2\n"
