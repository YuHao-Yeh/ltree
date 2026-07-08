# tests/test_cli/test_validators.py
import argparse
import pytest


from ltree.cli.validators import validate_tree_args


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture
def args():
    args = argparse.Namespace(
        format="",
        color=True,
        full_path=True,
        show_ellipsis=True,
        theme="emoji",
        output="-",
        folders_only=False,
        ex_files=[],
        ex_ext=[],
        add_files=[],
        dirs_first=False,
        regex_exclude=[],
        ex_dirs=[],
        add_dirs=[],
        human_readable=False,
        show_size=True,
        max_depth=None,
    )
    return args


# ======================================================================= #
# Tests: _validate_format
# ======================================================================= #
def test_validate_tree_args_format_text(args, capsys):
    # Case 1: color = True
    args.format = "text"
    args.color = True

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "Warning: Display flags (--color)" in captured.err
    assert "are ignored in 'text' format" in captured.err

    # Case 2: color = False
    args.color = False

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "" in captured.err


def test_validate_tree_args_format_json(args, capsys):
    # Case 1: all conditions satisfied
    args.format = "json"

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "Warning: Display flags" in captured.err
    assert "are ignored in 'json' format" in captured.err

    # Case 2: no flags meet condition
    args.color = False
    args.full_path = False
    args.show_ellipsis = False
    args.theme = "none"

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "" in captured.err


def test_validate_tree_args_format_markdown(args, capsys):
    # Case 1: color = full_path = True
    args.format = "markdown"
    args.color = True
    args.full_path = True

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "--color" in captured.err
    assert "--full-path" in captured.err
    assert "'markdown' format" in captured.err

    # Case 2: color = False
    args.color = False

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "" in captured.err


def test_validate_tree_args_format_block(args, capsys):
    args.format = "md"
    args.full_path = False

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "" in captured.err


def test_validate_tree_args_format_rich(args, capsys):
    # 1. full_path = True
    args.format = "rich"
    args.full_path = True

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "--full-path" in captured.err

    # 2. full_path = False
    args.format = "rich"
    args.full_path = False

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "" in captured.err


# ======================================================================= #
# Tests: _validate_output
# ======================================================================= #
def test_validate_tree_args_output(args, capsys):
    args.format = "yaml"
    args.output = "out.json"
    args.color = True

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "--color has no effect when writing to " in captured.err
    assert "Color output is disabled." in captured.err

    assert "Output file extension" in captured.err
    assert "does not match format" in captured.err


# ======================================================================= #
# Tests: _validate_filters
# ======================================================================= #
def test_validate_tree_args_filters_dirs_only(args, capsys):
    # Case 1.
    args.folders_only = True
    args.exclude = ["*.log", "build/"]
    args.include = ["extra.txt", "src/"]
    args.ex_files = ["*.log"]
    args.ex_ext = [".tmp"]
    args.add_files = ["extra.txt"]
    args.dirs_first = True

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "File filter flags" in captured.err
    assert "have no effect when --dirs-only is enabled" in captured.err
    assert "dirs-first has no effect when --folders-only is active" in captured.err

    assert "File-specific filter patterns" in captured.err
    assert "*.log" in captured.err
    assert "extra.txt" in captured.err
    assert "build/" not in captured.err
    assert "src/" not in captured.err
    assert "dirs-first has no effect when --folders-only is active" in captured.err

    # Case 2.
    args.folders_only = True
    args.exclude = ["build/", "temp/"]
    args.include = ["src/"]
    args.ex_files = []
    args.ex_ext = []
    args.add_files = []
    args.dirs_first = False

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert captured.err == ""


def test_validate_tree_args_filters_regex(args, capsys):
    args.regex_exclude = ["[invalid-regex+"]

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "Invalid regex" in captured.err


def test_validate_tree_args_filters_confliction(args, capsys):
    args.exclude = ["src/", "extra.txt"]
    args.include = ["src/", "extra.txt", "build/"]

    args.ex_dirs = ["src"]
    args.add_dirs = ["src"]
    args.ex_files = ["extra.txt"]
    args.add_files = ["extra.txt"]

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "Directories specified in both exclude and include" in captured.err
    assert "Files specified in both exclude and include" in captured.err

    assert "Patterns specified in both exclude (-I) and include (-A)" in captured.err
    assert "extra.txt" in captured.err
    assert "src/" in captured.err
    assert "build/" not in captured.err


# ======================================================================= #
# Tests: _validate_values
# ======================================================================= #


def test_validate_tree_args_values(args, capsys):
    # Case 1: human readable size
    args.human_readable = True
    args.show_size = False

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "--human has no effect unless --size is enabled." in captured.err

    # Case 2: negative path
    args.human_readable = False
    args.max_depth = -5

    validate_tree_args(args)
    captured = capsys.readouterr()

    assert "--max-depth cannot be negative" in captured.err
    assert args.max_depth == 0
