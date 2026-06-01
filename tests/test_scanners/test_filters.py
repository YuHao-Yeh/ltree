import re
import pathspec
from pathlib import Path

from ltree.core.config import TreeConfig
from ltree.core.scanners.filters import (
    ForceIncludeFilter,
    GitignoreFilter,
    RegexFilter,
    DefaultExcludeFilter,
    HiddenFilter,
    CompositeFilter,
)


# =======================================================================#
# Test: ForceIncludeFilter
# =======================================================================#
def test_force_include_filter():
    f = ForceIncludeFilter()
    config = TreeConfig()
    assert f.should_exclude(Path("src/main.py"), False, config) is False


# =======================================================================#
# Test: GitignoreFilter
# =======================================================================#
def test_gitignore_filter():
    f = GitignoreFilter()
    config = TreeConfig()
    config.root_path = "/dummy/repo"

    # Case 1: no gitignore spec is loaded
    assert f.should_exclude(Path("/dummy/repo/file.txt"), False, config) is False

    # Case 2: gitignore
    config.gitignore_spec = pathspec.PathSpec.from_lines(
        "gitignore", ["*.log", "node_modules/"]
    )
    assert f.should_exclude(Path("/dummy/repo/error.log"), False, config) is True
    assert f.should_exclude(Path("/dummy/repo/node_modules"), True, config) is True
    assert f.should_exclude(Path("/dummy/repo/src/main.py"), False, config) is False


# =======================================================================#
# Test: RegexFilter
# =======================================================================#
def test_regex_filter():
    f = RegexFilter()
    config = TreeConfig()
    config.root_path = "/dummy/repo"

    # Case 1: no regex rule is set
    assert f.should_exclude(Path("/dummy/repo/file.txt"), False, config) is False

    # Case 2: regex exclusion
    config.regex_exclude_patterns = [re.compile(r"temp_\d+"), re.compile(r"\.tmp$")]
    assert f.should_exclude(Path("/dummy/repo/temp_123/data"), True, config) is True
    assert f.should_exclude(Path("/dummy/repo/cache.tmp"), False, config) is True
    assert f.should_exclude(Path("/dummy/repo/template"), False, config) is False


# =======================================================================#
# Test: DefaultExcludeFilter
# =======================================================================#
def test_default_exclude_filter():
    f = DefaultExcludeFilter()
    config = TreeConfig()

    config.exclude_dirs = {"__pycache__"}
    config.exclude_files = {".DS_Store"}
    config.exclude_exts = {".log"}
    config.exclude_prefixes = {"tmp_"}
    config._pattern_files = ["*.bak", "debug_*"]

    # 1. directory
    assert f.should_exclude(Path("__pycache__"), True, config) is True
    assert f.should_exclude(Path("src"), True, config) is False

    # 2. file
    assert f.should_exclude(Path(".DS_Store"), False, config) is True

    # 3. ext
    assert f.should_exclude(Path("error.log"), False, config) is True

    # 4. prefix
    assert f.should_exclude(Path("tmp_cache"), False, config) is True
    assert f.should_exclude(Path("tmp_folder"), True, config) is True

    # 5. glob
    assert f.should_exclude(Path("data.bak"), False, config) is True
    assert f.should_exclude(Path("debug_logs.txt"), False, config) is True
    assert f.should_exclude(Path("release.txt"), False, config) is False


# =======================================================================#
# Test: HiddenFilter
# =======================================================================#
def test_hidden_filter():
    f = HiddenFilter()
    config = TreeConfig()

    # Case 1: show_all = True
    config.show_all = True
    assert f.should_exclude(Path(".env"), False, config) is False

    # Case 2: show_all = False
    config.show_all = False
    assert f.should_exclude(Path(".env"), False, config) is True
    assert f.should_exclude(Path("src"), True, config) is False


# =======================================================================#
# Test: CompositeFilter
# =======================================================================#
def test_composite_filter():
    config = TreeConfig()
    config.added_items = {"src"}

    f = CompositeFilter()

    # Case 1: added_items
    assert f.should_exclude(Path("src"), True, config) is False

    # Case 2: common filter
    config.exclude_files = {"secret.txt"}
    assert f.should_exclude(Path("secret.txt"), False, config) is True
