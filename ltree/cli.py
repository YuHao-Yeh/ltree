import argparse
import sys

from ltree.core.scanners.scanner import scan_tree
from ltree.core.config import TreeConfig
from ltree.renderers.exporters import (
    TextRenderer,
    JsonRenderer,
    MarkdownRenderer,
    MarkdownBlockRenderer,
    print_stats,
)
from ltree.renderers.rich_renderer import RichRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ltree: A customizable directory tree viewer.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # --- Basic ---
    basic = parser.add_argument_group("Basic Options")
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

    # --- Output Format ---
    output = parser.add_argument_group("Output Formatting")
    output.add_argument(
        "-F",
        "--format",
        dest="format",
        choices=["text", "json", "md", "markdown", "block", "rich"],
        default="text",
        help="Output format (default: text).",
    )
    output.add_argument(
        "-c",
        "--color",
        action="store_true",
        help="Enable colored output (Ignore in JSON/Markdown).",
        dest="color",
    )
    output.add_argument(
        "-s", "--size", action="store_true", help="Show file size.", dest="show_size"
    )  # reserved func
    output.add_argument(
        "-H",
        "--human",
        action="store_true",
        dest="human_readable",
        help="Show size in human-readable format (e.g., 1K 2M).",
    )

    # --- Filter Rules ---
    filtering = parser.add_argument_group("Filtering Rules")
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
        help="Only display directories.",
        dest="folders_only",
    )
    filtering.add_argument(
        "--ex-dirs",
        action="append",
        default=[],
        help="Exclude directories.",
        metavar="DIR",
        dest="ex_dirs",
    )
    filtering.add_argument(
        "-I",
        "--ex-files",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Exclude files (supports wildcards).",
        dest="ex_files",
    )
    filtering.add_argument(
        "--ex-ext",
        action="append",
        default=[],
        help="Exclude by file extension (e.g., .log).",
        dest="ex_ext",
    )
    filtering.add_argument(
        "--ex-prefix",
        action="append",
        default=[],
        help="Exclude by prefix.",
        dest="ex_prefix",
    )
    filtering.add_argument(
        "--add-dirs",
        action="append",
        default=[],
        help="Re-include specific directories.",
        dest="add_dirs",
    )
    filtering.add_argument(
        "--add-files",
        action="append",
        default=[],
        help="Re-include specific files.",
        dest="add_files",
    )
    filtering.add_argument(
        "--no-ignore",
        action="store_true",
        dest="no_ignore",
        help="Do not exclude files/directories matched by .gitignore.",
    )
    filtering.add_argument(
        "--re-ex",
        action="append",
        default=[],
        dest="regex_exclude",
        help="Exclude paths matching regex pattern.",
        metavar="REGEX",
    )
    # --- Display Options ---
    display = parser.add_argument_group("Display Options")
    display.add_argument(
        "-L",
        "--max-depth",
        type=int,
        default=None,
        help="Limit directory depth.",
        dest="max_depth",
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
        help="List directories before files.",
        dest="dirs_first",
    )
    display.add_argument(
        "--show-ellipsis",
        action="store_true",
        help='Show "..." when depth is truncated.',
        dest="show_ellipsis",
    )
    display.add_argument(
        "--theme",
        choices=["emoji", "nerd", "none"],
        default="emoji",
        help="Icon theme (default: emoji).",
        dest="theme",
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    ignored_flags = []

    # --- 1. JSON ---
    if args.format == "json":
        if args.color:
            ignored_flags.append("--color")
        if args.full_path:
            ignored_flags.append("--full-path")
        if args.show_ellipsis:
            ignored_flags.append("--show-ellipsis")
        if args.theme != "none":
            ignored_flags.append(f"--theme {args.theme}")

        if ignored_flags:
            flags_str = ", ".join(ignored_flags)
            print(
                f"Warning: Display flags ({flags_str}) are ignored in JSON format.",
                file=sys.stderr,
            )

        if args.show_size and not args.human_readable:
            print(
                "Warning: --size (-s) is redundant in JSON format. "
                "The raw file size ('size_bytes') is always included in the JSON output.\n"
                "         Use --human (-H) if you want to include formatted human-readable sizes ('size_human').",
                file=sys.stderr,
            )

    # --- 2. Markdown ---
    elif args.format in ["md", "markdown"]:
        if args.color:
            ignored_flags.append("--color")
        if args.full_path:
            ignored_flags.append("--full-path")

        if ignored_flags:
            flags_str = ", ".join(ignored_flags)
            print(
                f"Warning: Display flags ({flags_str}) are ignored in Markdown format.",
                file=sys.stderr,
            )

    # --- 3. Block ---
    elif args.format == "block":
        if args.color:
            ignored_flags.append("--color")

        if ignored_flags:
            flags_str = ", ".join(ignored_flags)
            print(
                f"Warning: Display flags ({flags_str}) are ignored in Markdown block format.",
                file=sys.stderr,
            )

    # --- 4. Rich ---
    elif args.format == "rich":
        if args.full_path:
            print(
                "Warning: --full-path might break the visual structure in 'rich' format.",
                file=sys.stderr,
            )

    # --- 5. Global Mutually Exclusive Checks ---
    if (args.output != "-") and args.color:
        print(
            f"Warning: --color (-c) has no effect when saving output to a file '{args.output}'. Color is disabled.",
            file=sys.stderr,
        )

    if args.folders_only:
        file_filters = []
        if args.ex_files:
            file_filters.append("--ex-files (-I)")
        if args.ex_ext:
            file_filters.append("--ex-ext")
        if args.add_files:
            file_filters.append("--add-files")

        if file_filters:
            filters_str = ", ".join(file_filters)
            print(
                f"Warning: File filter flags ({filters_str}) have no effect when --dirs-only (-d) is active.",
                file=sys.stderr,
            )

        if args.dirs_first:
            print(
                "Warning: --dirs-first has no effect when --dirs-only (-d) is active.",
                file=sys.stderr,
            )

    if args.format != "json" and args.human_readable and not args.show_size:
        print(
            "Warning: --human (-H) has no effect unless --size (-s) is also specified.",
            file=sys.stderr,
        )

    if args.max_depth is not None and args.max_depth < 0:
        print(
            f"Warning: --max-depth (-L) cannot be negative ({args.max_depth}). It will be treated as 0 (no recursion).",
            file=sys.stderr,
        )
        args.max_depth = 0

    conflicting_dirs = set(args.ex_dirs) & set(args.add_dirs)
    if conflicting_dirs:
        print(
            f"Warning: Directories {list(conflicting_dirs)} are specified in both exclusion and inclusion arguments. Inclusion takes priority.",
            file=sys.stderr,
        )

    conflicting_files = set(args.ex_files) & set(args.add_files)
    if conflicting_files:
        print(
            f"Warning: Files {list(conflicting_files)} are specified in both exclusion and inclusion arguments. Inclusion takes priority.",
            file=sys.stderr,
        )


def get_renderer_class(args: argparse.Namespace):
    renderers = {
        "text": TextRenderer,
        "json": JsonRenderer,
        "md": MarkdownRenderer,
        "markdown": MarkdownRenderer,
        "block": MarkdownBlockRenderer,
        "rich": RichRenderer,
    }
    return renderers.get(args.format, TextRenderer)


def run(args: argparse.Namespace) -> None:
    validate_args(args)

    config = TreeConfig()
    config.apply_args(args)

    is_console = args.output == "-"
    if is_console:
        output_file = sys.stdout
    else:
        output_file = open(args.output, "w", encoding="utf-8")

    try:
        root = scan_tree(path=args.start_path, config=config, max_depth=args.max_depth)

        if not root:
            return

        RendererClass = get_renderer_class(args)
        renderer = RendererClass(config)
        renderer.render(root, output_file)

        if is_console and args.format != "json":
            print_stats(root, config, args.format)

    finally:
        if not is_console:
            output_file.close()
            print(f"Directory tree written to {args.output}")


def main():
    run(parse_args())


if __name__ == "__main__":
    main()
