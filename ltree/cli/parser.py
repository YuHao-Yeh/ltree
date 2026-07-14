# ltree/cli/parser.py
import argparse
import re

from ltree import __version__
from ltree.rendering import registry
from ltree.cli.commands.config import (
    run_config_show,
    run_config_locate,
    run_config_validate,
)
from ltree.cli.commands.theme import run_theme, run_theme_preview
from ltree.cli.commands.tree import run_tree
from ltree.config.config import TreeConfig, THEMES


default_config = TreeConfig()


def regex_type(value: str) -> re.Pattern[str]:
    try:
        return re.compile(value)
    except re.error as e:
        raise argparse.ArgumentTypeError(f"Invalid regex '{value}': {e}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ltree: A customizable directory tree viewer.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"ltree-cli {__version__}",
        help="Show ltree-cli current version number.",
    )

    subparsers: argparse._SubParsersAction = parser.add_subparsers(
        title="Subcommands",
        dest="command",
        help="Run 'ltree <command> --help' for details on a specific subcommand.",
    )

    _build_tree_parser(subparsers)
    _build_theme_parser(subparsers)
    _build_config_parser(subparsers)

    return parser


def _build_tree_parser(subparsers: argparse._SubParsersAction) -> None:
    tree_parser: argparse.ArgumentParser = subparsers.add_parser(
        "tree",
        help="Generate and display a directory tree visualization.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # --- Basic Options ---
    basic: argparse._ArgumentGroup = tree_parser.add_argument_group("Basic Options")
    basic.add_argument(
        "start_path",
        nargs="?",
        default=".",
        help="Starting directory path (default: current directory).",
    )
    basic.add_argument(
        "-o",
        "--output",
        default="-",
        help='Output file name. Use "-" for stdout (default).',
    )

    # --- Output Formatting ---
    output = tree_parser.add_argument_group("Output Formatting")
    output.add_argument(
        "-F",
        "--format",
        choices=registry.keys(),
        default="text",
        help="Output format (default: text).",
    )
    output.add_argument(
        "-c",
        "--color",
        action=argparse.BooleanOptionalAction,
        default=None,
        dest="color",
        help="Enable colored output (Ignored in JSON/Markdown).",
    )

    # --- Metadata ---
    meta = tree_parser.add_argument_group("Metadata")
    # permission
    meta.add_argument(
        "--perm",
        action=argparse.BooleanOptionalAction,
        default=default_config.show_permission,
        dest="show_permission",
        help="Show or hide permission (Default: --perm)",
    )
    # git
    meta.add_argument(
        "--git",
        action=argparse.BooleanOptionalAction,
        default=default_config.show_git,
        dest="show_git",
        help="Show or hide git status (Default: --git)",
    )
    # size
    meta.add_argument(
        "-s",
        "--size",
        action=argparse.BooleanOptionalAction,
        default=default_config.show_size,
        dest="show_size",
        help="Show file size (Default: --size).",
    )
    meta.add_argument(
        "-H",
        "--human",
        action="store_true",
        dest="human_readable",
        help="Show size in human-readable format (e.g., 1K 2M).",
    )
    # time
    # [ ] NOTE: Now show_mtime in parser, show_time in TreeConfig, confliction exist.
    meta.add_argument(
        "--mtime",
        action=argparse.BooleanOptionalAction,
        default=default_config.show_time,
        dest="show_mtime",
        help="Show or hide modification time (Default: --mtime)",
    )
    # code
    meta.add_argument(
        "--code",
        action=argparse.BooleanOptionalAction,
        default=default_config.show_code,
        dest="show_code",
        help="Show or hide code info (Default: --no-code)",
    )
    # project
    meta.add_argument(
        "--project",
        action=argparse.BooleanOptionalAction,
        default=default_config.show_project,
        dest="show_project",
        help="Show or hide project (Default: --project)",
    )

    # --- Filtering Rules ---
    filtering = tree_parser.add_argument_group("Filtering Rules")
    filtering.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="show_all",
        help="Show hidden files and directories.",
    )
    filtering.add_argument(
        "-d",
        "--dirs-only",
        action="store_true",
        dest="folders_only",
        help="Only display directories.",
    )
    filtering.add_argument(
        "-I",
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        dest="exclude",
        help="Exclude files / directories (supports wildcards).",
    )
    filtering.add_argument(
        "--re-ex",
        type=regex_type,
        action="append",
        default=[],
        metavar="REGEX",
        dest="regex_exclude",
        help="Exclude paths matching regex pattern.",
    )
    filtering.add_argument(
        "-A",
        "--include",
        action="append",
        default=[],
        metavar="PATTERN",
        dest="include",
        help="Re-include specific files / directories (supports wildcards).",
    )

    # gitignore
    filtering.add_argument(
        "--gitignore",
        action=argparse.BooleanOptionalAction,
        default=default_config.use_gitignore,
        dest="gitignore",
        help="Exclude or include files/directories matched by .gitignore.",
    )

    # --- Display Options ---
    display = tree_parser.add_argument_group("Display Options")
    display.add_argument(
        "-L",
        "--max-depth",
        type=int,
        default=None,
        dest="max_depth",
        help="Limit directory depth.",
    )
    display.add_argument(
        "-f",
        "--full-path",
        action="store_true",
        dest="full_path",
        help="Print the full path prefix (Text format only).",
    )
    display.add_argument(
        "--dirs-first",
        action="store_true",
        dest="dirs_first",
        help="List directories before files.",
    )
    display.add_argument(
        "--ellipsis",
        action="store_true",
        dest="show_ellipsis",
        help='Show "..." when depth is truncated.',
    )

    display.add_argument(
        "--theme",
        choices=THEMES,
        default=default_config.theme,
        dest="theme",
        help="Icon theme (default: emoji).",
    )

    tree_parser.set_defaults(func=run_tree)


def _build_theme_parser(subparsers: argparse._SubParsersAction) -> None:
    theme_parser: argparse.ArgumentParser = subparsers.add_parser(
        "theme",
        help="Manage and list available icon themes.",
    )

    theme_sub = theme_parser.add_subparsers(dest="theme_command", required=True)

    list_parser = theme_sub.add_parser("list", help="List all available icon themes.")
    list_parser.set_defaults(func=run_theme)

    preview_parser = theme_sub.add_parser(
        "preview", help="Preview icons for a specific theme."
    )
    preview_parser.add_argument(
        "theme_name", choices=["emoji", "nerd", "none"], help="Theme to preview."
    )
    preview_parser.set_defaults(func=run_theme_preview)


def _build_config_parser(subparsers: argparse._SubParsersAction) -> None:
    config_parser = subparsers.add_parser(
        "config",
        help="Inspect and manage ltree configuration.",
    )

    config_sub = config_parser.add_subparsers(dest="config_command", required=True)

    # ------------------------------------------------------------------
    # config show
    show_parser = config_sub.add_parser(
        "show",
        help="Show the merged configuration currently in effect.",
    )
    show_parser.add_argument(
        "start_path",
        nargs="?",
        default=".",
        help="Directory used to resolve configuration files.",
    )
    show_parser.set_defaults(func=run_config_show)

    # ------------------------------------------------------------------
    # config locate
    locate_parser = config_sub.add_parser(
        "locate",
        help="Locate configuration files from the current directory upwards.",
    )
    locate_parser.add_argument(
        "start_path",
        nargs="?",
        default=".",
        help="Directory used to search configuration files.",
    )
    locate_parser.set_defaults(func=run_config_locate)

    # ------------------------------------------------------------------
    # config validate
    validate_parser = config_sub.add_parser(
        "validate",
        help="Validate all discovered configuration files.",
    )
    validate_parser.add_argument(
        "start_path",
        nargs="?",
        default=".",
        help="Directory used to search configuration files.",
    )
    validate_parser.set_defaults(func=run_config_validate)
