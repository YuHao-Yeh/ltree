# tests/test_cli/test_parser.py
from ltree.cli.parser import build_parser


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
