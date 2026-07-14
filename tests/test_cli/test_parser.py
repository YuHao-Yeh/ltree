# tests/test_cli/test_parser.py
import argparse
import pytest
import re

from ltree.cli.parser import build_parser, regex_type


# ======================================================================= #
# Tests: regex_type()
# ======================================================================= #
def test_regex_type_valid_pattern():
    valid_str = r"temp_\d+"
    result = regex_type(valid_str)

    assert isinstance(result, re.Pattern)
    assert result.pattern == valid_str


def test_regex_type_invalid_pattern():
    invalid_str = r"[0-9+"

    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        regex_type(invalid_str)

    assert "Invalid regex '[0-9+'" in str(exc_info.value)


# ======================================================================= #
# Tests: build_parser()
# ======================================================================= #
def test_build_parser_tree_defaults():
    parser = build_parser()
    args = parser.parse_args(["tree"])

    assert args.command == "tree"
    assert args.start_path == "."
    assert args.output == "-"
    assert args.format == "text"
    assert args.theme == "emoji"

    assert args.show_permission is True
    assert args.show_git is True
    assert args.show_mtime is True


def test_build_parser_tree_opposing_flags():
    parser = build_parser()

    # no- param
    args = parser.parse_args(["tree", "--no-git", "--no-perm", "--no-mtime"])
    assert args.show_git is False
    assert args.show_permission is False
    assert args.show_mtime is False


def test_build_parser_theme_subcommands():
    parser = build_parser()

    # 1. theme list
    args_list = parser.parse_args(["theme", "list"])
    assert args_list.command == "theme"
    assert args_list.theme_command == "list"

    # 2. theme preview
    args_preview = parser.parse_args(["theme", "preview", "nerd"])
    assert args_preview.command == "theme"
    assert args_preview.theme_command == "preview"
    assert args_preview.theme_name == "nerd"


def test_build_parser_invalid_regex(capsys):
    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["tree", "--re-ex", "[0-9+"])

    assert exc_info.value.code == 2

    captured = capsys.readouterr()
    assert "argument --re-ex: Invalid regex '[0-9+'" in captured.err
