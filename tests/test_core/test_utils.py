# tests/test_utils.py
import argparse
import io
import os
import pytest
from ltree.core.utils import (
    write_line,
    get_rel_path,
    format_size_classic,
)


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
# Test: get_rel_path
# =======================================================================#
def test_get_rel_path_logic():
    base = os.sep + os.path.join("Users", "user", "project")
    src = os.sep + os.path.join("Users", "user", "project", "src")
    fp = os.sep + os.path.join("Users", "user", "project", "src", "utils", "helper.py")

    # Case A: same path
    assert get_rel_path(base, base) == "."

    # Case B: sub-directories
    assert get_rel_path(src, base) == "src"

    # Case C: deep archives
    assert get_rel_path(fp, base) == "src/utils/helper.py"


def test_get_rel_path_with_trailing_sep():
    base = os.path.join("home", "user", "project")
    full = os.path.join("home", "user", "project", "data", "db.sqlite")

    res = get_rel_path(full, base)
    assert res == "data/db.sqlite"
    assert not res.startswith(os.sep)


# =======================================================================#
# Test: write_line
# =======================================================================#
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


# =======================================================================#
# Test: format_size_classic
# =======================================================================#
def test_format_size_classic():
    # Raw Bytes
    assert format_size_classic(100, human=False) == "     100 B"
    assert format_size_classic(1024, human=False) == "    1024 B"

    # Human Readable
    assert format_size_classic(500, human=True) == "500.0 B"
    assert format_size_classic(1024, human=True) == "  1.0 K"
    assert format_size_classic(1024**2 * 1.5, human=True) == "  1.5 M"
    assert format_size_classic(1024**5 * 1.5, human=True) == "  1.5 P"
