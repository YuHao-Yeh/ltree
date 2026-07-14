# tests/test_config.py
import argparse
import json
import logging
import pytest
from unittest.mock import patch

from ltree.config.config import TreeConfig, MatchRules


config_file = "ltree.config.config"


# ======================================================================= #
# Fixtures
# ======================================================================= #
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


# ======================================================================= #
# Tests: MatchRules
# ======================================================================= #
def test_match_rules_add_pattern_and_normalization():
    rules = MatchRules()

    # Null value or /\\
    rules.add_pattern("")
    rules.add_pattern("/")
    rules.add_pattern("\\")
    assert len(rules.literals) == 0
    assert len(rules.globs) == 0

    # Literals
    rules.add_pattern("node_modules/")
    assert "node_modules" in rules.literals

    rules.add_pattern("src\\build\\")
    assert "src/build" in rules.literals

    # Globs
    rules.add_pattern("*.log")
    assert "*.log" in rules.globs

    rules.add_pattern("**/build")
    assert "**/build" in rules.globs

    rules.add_pattern("file?")
    assert "file?" in rules.globs

    rules.add_pattern("temp[0-9]")
    assert "temp[0-9]" in rules.globs


def test_match_rules_matches_literals():
    rules = MatchRules()
    rules.add_pattern("node_modules")
    rules.add_pattern("src/build")

    assert rules.matches("node_modules", "node_modules") is True
    assert rules.matches("nested/node_modules", "node_modules") is True
    assert rules.matches("nested/node_modules/sub", "node_modules") is True
    assert rules.matches("nested/other_folder", "other_folder") is False

    assert rules.matches("src/build", "build") is True
    assert rules.matches("other/src/build", "build") is False


def test_match_rules_matches_globs():
    rules = MatchRules()
    rules.add_pattern("*.log")
    rules.add_pattern("**/build")
    rules.add_pattern("src/**")

    assert rules.matches("src/main.log", "main.log") is True
    assert rules.matches("error.log", "error.log") is True

    assert rules.matches("foo/bar/build", "build") is True
    assert rules.matches("build", "build") is True
    assert rules.matches("src/main.py", "main.py") is True
    assert rules.matches("src", "src") is True

    assert rules.matches("foo/bar/other", "other") is False


# ======================================================================= #
# Tests: TreeConfig._apply_dict_config()
# ======================================================================= #
def test_apply_dict_config_basic_and_lists():
    # empty dict
    config = TreeConfig()
    config._apply_dict_config({})

    assert config.theme == "emoji"
    assert config.use_color is False
    assert config.show_size is False

    # general dict
    config = TreeConfig()
    config_dict = {
        "theme": "nerd",
        "color": True,
        "size": True,
        "human": True,
        "all": True,
        "dirs_only": True,
        "full_path": True,
        "dirs_first": True,
        "show_ellipsis": True,
        "no_ignore": True,
        "exclude": ["custom_dir/", "custom_file", "*.custom_ext", "custom_prefix*"],
        "include": ["__pycache__/", ".DS_Store"],
    }

    config._apply_dict_config(config_dict)

    assert config.theme == "nerd"
    assert config.use_color is True
    assert config.show_size is True
    assert config.human_readable is True
    assert config.show_all is True
    assert config.folders_only is True
    assert config.full_path is True
    assert config.dirs_first is True
    assert config.show_ellipsis is True
    assert config.use_gitignore is False

    assert "custom_dir" in config.exclude.literals
    assert "*.custom_ext" in config.exclude.globs
    assert "__pycache__" in config.include.literals
    assert ".DS_Store" in config.include.literals


# ======================================================================= #
# Tests: TreeConfig.load_config_file() (.ltreerc & pyproject.toml)
# ======================================================================= #
def test_load_config_file_ltreerc_json(tmp_path):
    # temporary .ltreerc
    ltreerc = tmp_path / ".ltreerc"
    ltreerc.write_text(
        json.dumps({"theme": "nerd", "dirs_first": True}), encoding="utf-8"
    )

    config = TreeConfig()
    config.load_config_file(str(tmp_path))

    assert config.theme == "nerd"
    assert config.dirs_first is True


def test_load_config_file_pyproject_toml(tmp_path):
    # temporary pyproject.toml
    toml_content = """
    [tool.ltree]
    theme = "nerd"
    human = true
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(toml_content, encoding="utf-8")

    config = TreeConfig()
    config.load_config_file(str(tmp_path))

    assert config.theme == "nerd"
    assert config.human_readable is True


def test_load_config_file_climbing_traversal(tmp_path):
    # tmp_path/
    # ├── .ltreerc
    # └── dir1/
    #     └── dir2/
    ltreerc = tmp_path / ".ltreerc"
    ltreerc.write_text(json.dumps({"theme": "nerd"}), encoding="utf-8")

    deep_dir = tmp_path / "dir1" / "dir2"
    deep_dir.mkdir(parents=True)

    config = TreeConfig()
    config.load_config_file(str(deep_dir))

    assert config.theme == "nerd"


def test_load_config_file_corrupted_json_warning(tmp_path, caplog):
    ltreerc = tmp_path / ".ltreerc"
    ltreerc.write_text("{invalid json", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        config = TreeConfig()
        config.load_config_file(str(tmp_path))

    assert "Failed to parse .ltreerc" in caplog.text


def test_load_config_file_corrupted_toml_warning(tmp_path, caplog):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.ltree]\ninvalid_toml = = =", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        config = TreeConfig()
        config.load_config_file(str(tmp_path))

    assert "Failed to parse pyproject.toml" in caplog.text


def test_load_config_file_no_tomllib_warning(tmp_path, caplog):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.ltree]\ntheme = 'nerd'", encoding="utf-8")

    with patch(f"{config_file}.tomllib", None):
        from ltree.config.config import TreeConfig

        with caplog.at_level(logging.WARNING):
            config = TreeConfig()
            config.load_config_file(str(tmp_path))

    assert (
        "pyproject.toml found but cannot be parsed because 'tomli' is not installed"
        in caplog.text
    )


# ======================================================================= #
# Tests: TreeConfig.load_gitignore()
# ======================================================================= #
def test_load_gitignore_success(tmp_path):
    gitignore_file = tmp_path / ".gitignore"
    gitignore_file.write_text("*.log\nnode_modules/\n!important.log")

    config = TreeConfig()
    config.use_gitignore = True
    config.load_gitignore(str(tmp_path))

    assert config.gitignore_spec is not None

    # exclude .log
    assert config.gitignore_spec.match_file("error.log") is True
    # include important.log
    assert config.gitignore_spec.match_file("important.log") is False
    # exclude node_modules dirs
    assert config.gitignore_spec.match_file("node_modules/index.js") is True


def test_load_gitignore_not_found():
    config = TreeConfig()

    config.load_gitignore("/non/existent/path")

    assert config.gitignore_spec is None


def test_disable_gitignore(tmp_path):
    gitignore_file = tmp_path / ".gitignore"
    gitignore_file.write_text("secret.txt")

    config = TreeConfig()
    config.use_gitignore = False
    config.load_gitignore(str(tmp_path))

    assert config.gitignore_spec is None


def test_load_gitignore_open_error(caplog):
    config = TreeConfig()

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            config.load_gitignore("/dummy/path")

    assert "Could not load .gitignore: Permission denied" in caplog.text
    assert config.gitignore_spec is None


def test_load_gitignore_parse_error(tmp_path, caplog):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log")

    config = TreeConfig()

    with patch(
        "pathspec.PathSpec.from_lines", side_effect=Exception("Unexpected Parser Error")
    ):
        with caplog.at_level(logging.WARNING):
            config.load_gitignore(str(tmp_path))

    assert "Could not load .gitignore: Unexpected Parser Error" in caplog.text
    assert config.gitignore_spec is None
