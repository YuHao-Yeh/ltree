import argparse
import copy
import io
import pytest
import sys
from unittest.mock import MagicMock, patch, mock_open

from ltree.cli import parse_args, validate_args, run, main


# =======================================================================#
# Fixture
# =======================================================================#
CLI_MODULE = "ltree.cli"
RENDERER_PATH = "ltree.renderers"


@pytest.fixture
def base_args():
    return argparse.Namespace(
        start_path=".",
        output="-",
        format="text",
        max_depth=None,
        color=False,
        show_size=False,
        human_readable=False,
        show_all=False,
        folders_only=False,
        no_ignore=True,
        regex_exclude=[],
        dirs_first=False,
        show_ellipsis=False,
        ex_dirs=[],
        ex_files=[],
        ex_ext=[],
        ex_prefix=[],
        add_dirs=[],
        add_files=[],
        full_path=False,
        theme="none",
    )


def create_mock_root(size=1024):
    root = MagicMock()
    root.size = size
    root.stats.visible_dirs = 1
    root.stats.visible_files = 1
    root.stats.total_dirs = 1
    root.stats.total_files = 1
    return root


# =======================================================================#
# Test: parse_arg
# =======================================================================#
def test_parse_args_defaults():
    with patch.object(sys, "argv", ["list-tree"]):
        args = parse_args()
        assert args.start_path == "."
        assert args.output == "-"
        assert args.format == "text"


def test_parse_args_custom():
    test_args = [
        "list-tree",
        "my_path",
        "-o",
        "out.txt",
        "-F",
        "json",
        "-L",
        "2",
        "-f",
        "-a",
        "--dirs-first",
    ]
    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.start_path == "my_path"
        assert args.output == "out.txt"
        assert args.format == "json"
        assert args.max_depth == 2
        assert args.full_path is True
        assert args.show_all is True
        assert args.dirs_first is True


# =======================================================================#
# Test: validate_args (Warnings and Errors)
# =======================================================================#
# 1.JSON
def test_validate_args_json_ignored_flags(capsys, base_args):
    args = copy.copy(base_args)
    args.format = "json"
    args.color = True
    args.full_path = True
    args.show_ellipsis = True
    args.theme = "emoji"

    validate_args(args)
    captured = capsys.readouterr()
    assert "Warning: Display flags" in captured.err
    assert "--color" in captured.err
    assert "--full-path" in captured.err
    assert "--show-ellipsis" in captured.err
    assert "--theme emoji" in captured.err


def test_validate_args_json_size_redundant(capsys, base_args):
    args = base_args
    args.format = "json"
    args.show_size = True
    args.human_readable = False

    validate_args(args)
    captured = capsys.readouterr()
    assert "redundant in JSON format" in captured.err


# 2. Markdown
def test_validate_args_markdown_ignored_flags(capsys, base_args):
    args = copy.copy(base_args)
    args.format = "md"
    args.color = True
    args.full_path = True

    validate_args(args)
    captured = capsys.readouterr()
    assert "Warning: Display flags" in captured.err
    assert "ignored in Markdown format" in captured.err


# 3. Block
def test_validate_args_block_ignored_flags(capsys, base_args):
    args = copy.copy(base_args)
    args.format = "block"
    args.color = True

    validate_args(args)
    captured = capsys.readouterr()
    assert "Warning: Display flags" in captured.err
    assert "ignored in Markdown block format" in captured.err


# 4. Rich
def test_validate_args_rich_ignored_flags(capsys, base_args):
    args = copy.copy(base_args)
    args.format = "rich"
    args.full_path = True

    validate_args(args)
    captured = capsys.readouterr()
    assert "might break the visual structure" in captured.err


# 5. Global
def test_validate_args_file_output_with_color(capsys, base_args):
    args = copy.copy(base_args)
    args.output = "out.txt"
    args.color = True

    validate_args(args)
    captured = capsys.readouterr()
    assert "has no effect when saving output to a file" in captured.err


def test_validate_args_folders_only_redundancies(capsys, base_args):
    args = copy.copy(base_args)
    args.folders_only = True
    args.ex_files = ["*.log"]
    args.ex_ext = [".tmp"]
    args.add_files = ["keep.txt"]
    args.dirs_first = True

    validate_args(args)
    captured = capsys.readouterr().err
    assert "File filter flags" in captured
    assert "--ex-files (-I)" in captured
    assert "--ex-ext" in captured
    assert "--add-files" in captured
    assert "--dirs-first has no effect" in captured


def test_validate_args_folders_only_no_filters(capsys, base_args):
    args = copy.copy(base_args)
    args.folders_only = True
    args.ex_files = []
    args.ex_ext = []
    args.add_files = []
    args.dirs_first = False

    validate_args(args)
    captured = capsys.readouterr().err
    assert "File filter flags" not in captured
    assert "--dirs-first has no effect" not in captured


def test_validate_args_human_without_size(capsys, base_args):
    args = copy.copy(base_args)
    args.format = "text"
    args.human_readable = True
    args.show_size = False

    validate_args(args)
    captured = capsys.readouterr()
    assert "unless --size (-s) is also specified" in captured.err


def test_validate_args_negative_max_depth(capsys, base_args):
    args = copy.copy(base_args)
    args.max_depth = -3

    validate_args(args)
    captured = capsys.readouterr()
    assert "cannot be negative" in captured.err
    assert args.max_depth == 0


def test_validate_args_direct_conflicts(capsys, base_args):
    args = copy.copy(base_args)
    args.ex_dirs = ["src"]
    args.add_dirs = ["src"]
    args.ex_files = ["main.py"]
    args.add_files = ["main.py"]

    validate_args(args)
    captured = capsys.readouterr()
    assert "Directories ['src'] are specified in both" in captured.err
    assert "Files ['main.py'] are specified in both" in captured.err


# =======================================================================#
# Test: run
# =======================================================================#
@patch(f"{CLI_MODULE}.scan_tree")
@patch(f"{RENDERER_PATH}.exporters.TextRenderer.render")
@patch("ltree.core.config.TreeConfig.load_config_file")
def test_run_file_output(
    mock_load_config, mock_render_text, mock_scan, base_args, capsys
):
    mock_scan.return_value = create_mock_root()
    base_args.output = "test_output.txt"

    m = mock_open()
    with patch("builtins.open", m):
        run(base_args)

    m.assert_called_once_with("test_output.txt", "w", encoding="utf-8")
    mock_render_text.assert_called_once()

    captured = capsys.readouterr()
    assert "Directory tree written to test_output.txt" in captured.out


@pytest.mark.parametrize(
    "fmt, renderer_class",
    [
        ("text", "exporters.TextRenderer"),
        ("json", "exporters.JsonRenderer"),
        ("md", "exporters.MarkdownRenderer"),
        ("block", "exporters.MarkdownBlockRenderer"),
        ("rich", "rich_renderer.RichRenderer"),
    ],
)
@patch(f"{CLI_MODULE}.scan_tree")
@patch(f"{CLI_MODULE}.print_stats")
def test_run_formats_and_stats(
    mock_print_stats, mock_scan, fmt, renderer_class, base_args
):
    mock_scan.return_value = create_mock_root()
    base_args.format = fmt
    base_args.output = "-"

    with patch(f"{RENDERER_PATH}.{renderer_class}.render") as mock_render:
        with patch("sys.stdout", new_callable=io.StringIO):
            run(base_args)

        mock_render.assert_called_once()
        mock_scan.assert_called_once()
        if fmt != "json":
            mock_print_stats.assert_called_once()


@patch(f"{CLI_MODULE}.scan_tree")
def test_run_no_exist_path(mock_scan, base_args):
    mock_scan.return_value = None

    assert run(base_args) is None


# =======================================================================#
# Test: main entry point
# =======================================================================#
def test_main_entry_point():
    with patch(f"{CLI_MODULE}.parse_args") as mock_parse:
        with patch(f"{CLI_MODULE}.run") as mock_run:
            mock_args = MagicMock()
            mock_parse.return_value = mock_args

            main()

            mock_parse.assert_called_once()
            mock_run.assert_called_once_with(mock_args)
