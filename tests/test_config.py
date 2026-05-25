import argparse
import json
import pytest
import re
import sys
from unittest.mock import patch

from ltree.core.config import TreeConfig


#=======================================================================#
# Fixture
#=======================================================================#
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
        theme='none',
    )

#=======================================================================#
# Test: TreeConfig.apply_args()
#=======================================================================#
def test_config_apply_args_exclusions(base_args):
    config = TreeConfig()
    
    base_args.ex_dirs = ['my_node_modules', 'temp_dir']
    base_args.ex_files = ['config.secret', 'data.db']
    base_args.ex_ext = ['.log', '.tmp']
    base_args.ex_prefix = ['test_', 'tmp_']
    
    config.apply_args(base_args)
    
    assert 'my_node_modules' in config.exclude_dirs
    assert 'config.secret' in config.exclude_files
    assert '.log' in config.exclude_exts
    assert 'test_' in config.exclude_prefixes

def test_config_apply_args_reinclude(base_args):
    config = TreeConfig()
    
    assert '__pycache__' in config.exclude_dirs

    config.exclude_files.add('tree.txt')

    base_args.add_dirs = ['__pycache__']
    base_args.add_files = ['tree.txt']

    config.apply_args(base_args)
    
    
    assert '__pycache__' not in config.exclude_dirs
    assert 'tree.txt' not in config.exclude_files
    
    assert '__pycache__' in config.added_items
    assert 'tree.txt' in config.added_items

def test_config_color_logic(base_args):
    config = TreeConfig()
    
    # Case A: console output with color
    base_args.output = "-"
    base_args.color = True
    config.apply_args(base_args)
    assert config.use_color is True
    
    # Case B：file output with no color
    base_args.output = "out.txt"
    base_args.color = True
    config.apply_args(base_args)
    assert config.use_color is False

def test_config_pattern_preparation(base_args):
    config = TreeConfig()

    base_args.ex_files = ['*.log', 'debug_?_test.txt', 'fixed_name.txt']
    
    config.apply_args(base_args)

    assert '*.log' in config._pattern_files
    assert 'debug_?_test.txt' in config._pattern_files

    assert 'fixed_name.txt' in config._exact_files
    assert '*.log' not in config._exact_files

def test_config_flag_sync(base_args):
    config = TreeConfig()
    
    base_args.show_size = True
    base_args.folders_only = True
    base_args.full_path = True
    base_args.dirs_first = True
    base_args.human_readable = True
    base_args.show_all = True
    base_args.show_ellipsis = True
    
    config.apply_args(base_args)
    
    assert config.show_size is True
    assert config.folders_only is True
    assert config.full_path is True
    assert config.dirs_first is True
    assert config.human_readable is True
    assert config.show_all is True
    assert config.show_ellipsis is True

def test_config_regex_compilation(base_args):
    config = TreeConfig()
    
    base_args.regex_exclude = [r"temp_\d+", r".*\.tmp$"]
        
    config.apply_args(base_args)
    
    assert len(config.regex_exclude_patterns) == 2
    assert isinstance(config.regex_exclude_patterns[0], re.Pattern)
    
    pattern = config.regex_exclude_patterns[0]
    assert pattern.search("temp_123") is not None
    assert pattern.search("temp_abc") is None

def test_config_invalid_regex_handling(base_args, capsys):
    config = TreeConfig()

    base_args.regex_exclude = [r"[0-9+"]
    
    config.apply_args(base_args)
    
    captured = capsys.readouterr()
    assert "Warning: Invalid regex" in captured.out
    assert len(config.regex_exclude_patterns) == 0

def test_apply_args_overrides_config_properly(tmp_path, base_args):
    ltreerc = tmp_path / ".ltreerc"
    ltreerc.write_text(json.dumps({"theme": "nerd", "size": True}), encoding="utf-8")
    
    base_args.start_path = str(tmp_path)
    base_args.show_size = False
    base_args.theme = "emoji"
    
    config = TreeConfig()
    with patch.object(sys, 'argv', ['ltree']):
        config.apply_args(base_args)

        assert config.theme == "nerd"
        assert config.show_size is True

    config = TreeConfig()
    with patch.object(sys, 'argv', ['ltree', '--theme', 'none']):
        base_args.theme = "none"
        config.apply_args(base_args)

        assert config.theme == "none"
        assert config.show_size is True

#=======================================================================#
# Test: TreeConfig._apply_dict_config()
#=======================================================================#
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
        "ex_dirs": ["custom_dir"],
        "ex_files": ["custom_file"],
        "ex_ext": [".custom_ext"],
        "ex_prefix": ["custom_prefix"],
        "add_dirs": ["__pycache__"],
        "add_files": [".DS_Store"]
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

    assert "custom_dir" in config.exclude_dirs
    assert "custom_file" in config.exclude_files
    assert ".custom_ext" in config.exclude_exts
    assert "custom_prefix" in config.exclude_prefixes
    
    assert "__pycache__" not in config.exclude_dirs
    assert ".DS_Store" not in config.exclude_files

#=======================================================================#
# Test: TreeConfig.load_config_file() (.ltreerc & pyproject.toml)
#=======================================================================#
def test_load_config_file_ltreerc_json(tmp_path):
    # temporary .ltreerc
    ltreerc = tmp_path / ".ltreerc"
    ltreerc.write_text(json.dumps({"theme": "nerd", "dirs_first": True}), encoding="utf-8")
    
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

def test_load_config_file_corrupted_json_warning(tmp_path, capsys):
    ltreerc = tmp_path / ".ltreerc"
    ltreerc.write_text("{invalid json", encoding="utf-8")
    
    config = TreeConfig()
    config.load_config_file(str(tmp_path))
    
    captured = capsys.readouterr()
    assert "Warning: Failed to parse .ltreerc" in captured.err

def test_load_config_file_corrupted_toml_warning(tmp_path, capsys):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.ltree]\ninvalid_toml = = =", encoding="utf-8")
    
    config = TreeConfig()
    config.load_config_file(str(tmp_path))
    
    captured = capsys.readouterr()
    assert "Warning: Failed to parse pyproject.toml" in captured.err

def test_load_config_file_no_tomllib_warning(tmp_path, capsys):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.ltree]\ntheme = 'nerd'", encoding="utf-8")
    
    with patch("ltree.core.config.tomllib", None):
        from ltree.core.config import TreeConfig
        config = TreeConfig()
        config.load_config_file(str(tmp_path))
        
    captured = capsys.readouterr()
    assert "Warning: pyproject.toml found but cannot be parsed because 'tomli' is not installed" in captured.err

#=======================================================================#
# Test: TreeConfig.load_gitignore()
#=======================================================================#
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

def test_load_gitignore_open_error(capsys):
    config = TreeConfig()
    
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            config.load_gitignore("/dummy/path")
    
    captured = capsys.readouterr()
    
    assert "Warning: Could not load .gitignore: Permission denied" in captured.out
    assert config.gitignore_spec is None

def test_load_gitignore_parse_error(tmp_path, capsys):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log")

    config = TreeConfig()
    
    with patch("pathspec.PathSpec.from_lines", side_effect=Exception("Unexpected Parser Error")):
        config.load_gitignore(str(tmp_path))
    
    captured = capsys.readouterr()
    
    assert "Warning: Could not load .gitignore: Unexpected Parser Error" in captured.out
    assert config.gitignore_spec is None

