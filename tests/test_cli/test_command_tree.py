# tests/test_cli/test_command_tree.py
import argparse

from ltree.cli.commands.tree import run_tree

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
