# tests/test_cli/test_command_tree.py
import argparse
from unittest.mock import patch, MagicMock

from ltree.cli.commands.tree import run_tree
from ltree.app.tree import RenderResult

cli_cmd = "ltree.cli.commands"


# ======================================================================= #
# Fixtures
# ======================================================================= #
def build_args(**kwargs):
    defaults = {
        "start_path": ".",
        "output": "-",
        "format": "text",
        "theme": "none",
        "color": False,
        "show_permission": False,
        "show_git": False,
        "show_size": False,
        "human_readable": False,
        "show_mtime": False,
        "show_code": False,
        "show_project": False,
        "show_all": False,
        "folders_only": False,
        "dirs_first": False,
        "full_path": False,
        "show_ellipsis": False,
        "gitignore": False,
        "regex_exclude": [],
        "ex_dirs": [],
        "ex_files": [],
        "ex_ext": [],
        "ex_prefix": [],
        "add_dirs": [],
        "add_files": [],
        "max_depth": None,
    }
    defaults.update(kwargs)

    return argparse.Namespace(**defaults)


# ======================================================================= #
# Tests: run_tree
# ======================================================================= #
def test_run_tree_console_serialized(tmp_path, capsys):
    (tmp_path / "foo.txt").write_text("sample content")
    args = build_args(start_path=tmp_path, format="json")

    run_tree(args)
    captured = capsys.readouterr()

    assert '"name":' in captured.out
    assert "foo.txt" in captured.out
    assert "Summary" not in captured.out


def test_run_tree_console_row_with_stats(tmp_path, capsys):
    (tmp_path / "bar.py").write_text("import sys")
    args = build_args(start_path=tmp_path, format="text")

    run_tree(args)
    captured = capsys.readouterr()

    assert "bar.py" in captured.out
    assert "Summary" in captured.out
    assert "1 files" in captured.out


def test_run_tree_file_output(tmp_path, capsys):
    (tmp_path / "baz.md").write_text("# Hello")
    target_out_file = tmp_path / "tree_report.txt"

    args = build_args(start_path=tmp_path, output=str(target_out_file), format="text")

    run_tree(args)
    captured = capsys.readouterr()

    assert "Directory tree written to" in captured.out

    assert target_out_file.exists()
    content = target_out_file.read_text(encoding="utf-8")
    assert "baz.md" in content


@patch("ltree.core.scanners.scanner.scan_tree")
def test_run_tree_stats_scan_fallback_safety(mock_scan, tmp_path, capsys):
    mock_scan.return_value = None
    args = build_args(start_path=str(tmp_path))

    with patch(f"{cli_cmd}.tree.TreeApplication") as mock_app_cls:
        mock_app = MagicMock()
        mock_app.generate.return_value = RenderResult(content="mock_tree", rtype="row")
        mock_app_cls.return_value = mock_app

        run_tree(args)

    captured = capsys.readouterr()
    assert "mock_tree" in captured.out
    assert "Summary" not in captured.out
