# tests/test_tree/test_scan/test_context.py
import os

from ltree.tree.scan.context import _relative_path


# ======================================================================= #
# Tests: _relative_path()
# ======================================================================= #
def test_relative_path_logic():
    base = os.sep + os.path.join("Users", "user", "project")
    src = os.sep + os.path.join("Users", "user", "project", "src")
    fp = os.sep + os.path.join("Users", "user", "project", "src", "utils", "helper.py")

    # Case A: same path
    assert _relative_path(base, base) == "."

    # Case B: sub-directories
    assert _relative_path(src, base) == "src"

    # Case C: deep archives
    assert _relative_path(fp, base) == "src/utils/helper.py"


def test_relative_path_with_trailing_sep():
    base = os.path.join("home", "user", "project")
    full = os.path.join("home", "user", "project", "data", "db.sqlite")

    res = _relative_path(full, base)
    assert res == "data/db.sqlite"
    assert not res.startswith(os.sep)
