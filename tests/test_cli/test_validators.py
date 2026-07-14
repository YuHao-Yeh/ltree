# tests/test_cli/test_validators.py
import argparse
import logging
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
        dirs_first=False,
        regex_exclude=[],
        human_readable=False,
        show_size=True,
        max_depth=None,
    )
    return args


# ======================================================================= #
# Tests: _validate_format
# ======================================================================= #
def test_validate_tree_args_format_text(args, caplog):
    # Case 1: color = True
    args.format = "text"
    args.color = True

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "Display flags (--color)" in caplog.text
        assert "are ignored in 'text' format" in caplog.text
    caplog.clear()

    # Case 2: color = False
    args.color = False

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "" in caplog.text


def test_validate_tree_args_format_json(args, caplog):
    # Case 1: all conditions satisfied
    args.format = "json"

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "Display flags" in caplog.text
        assert "are ignored in 'json' format" in caplog.text
    caplog.clear()

    # Case 2: no flags meet condition
    args.color = False
    args.full_path = False
    args.show_ellipsis = False
    args.theme = "none"

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "" in caplog.text


def test_validate_tree_args_format_markdown(args, caplog):
    # Case 1: color = full_path = True
    args.format = "markdown"
    args.color = True
    args.full_path = True

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "--color" in caplog.text
        assert "--full-path" in caplog.text
        assert "'markdown' format" in caplog.text
    caplog.clear()

    # Case 2: color = False
    args.color = False

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "" in caplog.text


def test_validate_tree_args_format_block(args, caplog):
    args.format = "md"
    args.full_path = False

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "" in caplog.text


def test_validate_tree_args_format_rich(args, caplog):
    # 1. full_path = True
    args.format = "rich"
    args.full_path = True

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "--full-path" in caplog.text
    caplog.clear()

    # 2. full_path = False
    args.format = "rich"
    args.full_path = False

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "" in caplog.text


# ======================================================================= #
# Tests: _validate_output
# ======================================================================= #
def test_validate_tree_args_output(args, caplog):
    args.format = "yaml"
    args.output = "out.json"
    args.color = True

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "--color has no effect when writing to " in caplog.text
        assert "Color output is disabled." in caplog.text

        assert "Output file extension" in caplog.text
        assert "does not match format" in caplog.text


# ======================================================================= #
# Tests: _validate_filters
# ======================================================================= #
def test_validate_tree_args_filters_dirs_only(args, caplog):
    # Case 1.
    args.folders_only = True
    args.exclude = ["*.log", "build/"]
    args.include = ["extra.txt", "src/"]
    args.dirs_first = True

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "File-specific filter patterns" in caplog.text
        assert "*.log" in caplog.text
        assert "extra.txt" in caplog.text
        assert "build/" not in caplog.text
        assert "src/" not in caplog.text
        assert "dirs-first has no effect when --folders-only is active" in caplog.text
    caplog.clear()

    # Case 2.
    args.folders_only = True
    args.exclude = ["build/", "temp/"]
    args.include = ["src/"]
    args.dirs_first = False

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert caplog.text == ""


def test_validate_tree_args_filters_regex(args, caplog):
    args.regex_exclude = ["[invalid-regex+"]

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "Invalid regex" in caplog.text


def test_validate_tree_args_filters_confliction(args, caplog):
    args.exclude = ["src/", "extra.txt"]
    args.include = ["src/", "extra.txt", "build/"]

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "Patterns specified in both exclude (-I) and include (-A)" in caplog.text
        assert "extra.txt" in caplog.text
        assert "src/" in caplog.text
        assert "build/" not in caplog.text


# ======================================================================= #
# Tests: _validate_values
# ======================================================================= #
def test_validate_tree_args_values(args, caplog):
    # Case 1: human readable size
    args.human_readable = True
    args.show_size = False

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "--human has no effect unless --size is enabled." in caplog.text
    caplog.clear()

    # Case 2: negative path
    args.human_readable = False
    args.max_depth = -5

    with caplog.at_level(logging.WARNING):
        validate_tree_args(args)
        assert "--max-depth cannot be negative" in caplog.text
        assert args.max_depth == 0
