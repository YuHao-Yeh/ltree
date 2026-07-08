# ltree/cli/validators.py
import argparse
import re
import sys
from pathlib import Path


def _warn(message: str) -> None:
    print(
        f"Warning: {message}",
        file=sys.stderr,
    )


def validate_tree_args(args: argparse.Namespace) -> None:
    _validate_format(args)
    _validate_output(args)
    _validate_filters(args)
    _validate_values(args)


def _validate_format(args: argparse.Namespace) -> None:
    ignored_flags: list[str] = []

    if args.format in {"text"}:
        if args.color:
            ignored_flags.append("--color")

    # JSON / YAML
    if args.format in {"json", "yaml"}:
        if args.color:
            ignored_flags.append("--color")

        if args.full_path:
            ignored_flags.append("--full-path")

        if args.show_ellipsis:
            ignored_flags.append("--ellipsis")

        if args.theme != "none":
            ignored_flags.append(f"--theme {args.theme}")

    # Markdown / Block
    elif args.format in {"md", "markdown", "block"}:
        if args.color:
            ignored_flags.append("--color")

        if args.format in {"md", "markdown"} and args.full_path:
            ignored_flags.append("--full-path")

    # Rich
    elif args.format in {"rich"}:
        if args.full_path:
            ignored_flags.append("--full-path")

    # Graphviz

    if ignored_flags:
        _warn(
            f"Display flags ({', '.join(ignored_flags)}) "
            f"are ignored in '{args.format}' format."
        )


def _validate_output(args: argparse.Namespace) -> None:
    if args.output != "-" and args.color:
        _warn(
            f"--color has no effect when writing to '{args.output}'. "
            "Color output is disabled."
        )

    # Optional extension hint
    expected_extensions = {
        "json": ".json",
        "yaml": ".yaml",
        "html": ".html",
        "graphviz": ".dot",
        "markdown": ".md",
        "md": ".md",
    }

    expected = expected_extensions.get(args.format)
    filepath = Path(args.output)

    if (
        expected
        and args.output != "-"
        and filepath.suffix
        and filepath.suffix != expected
    ):
        _warn(
            f"Output file extension '{Path(args.output).suffix}' "
            f"does not match format '{args.format}' "
            f"(expected '{expected}')."
        )


def _validate_filters(args: argparse.Namespace) -> None:
    # dirs-only makes file filters useless
    if args.folders_only:
        # ------------------------------------------------------------- #
        # legacy filter:
        ignored = []

        if args.ex_files:
            ignored.append("--ex-files")

        if args.ex_ext:
            ignored.append("--ex-ext")

        if args.add_files:
            ignored.append("--add-files")

        if ignored:
            _warn(
                f"File filter flags ({', '.join(ignored)}) "
                f"have no effect when --dirs-only is enabled."
            )
        # ------------------------------------------------------------- #
        # new:
        all_patterns = getattr(args, "exclude", []) + getattr(args, "include", [])
        ignored_file_patterns = [pat for pat in all_patterns if not pat.endswith("/")]

        if ignored_file_patterns:
            _warn(
                f"File-specific filter patterns {sorted(ignored_file_patterns)} "
                "have no effect when --dirs-only is enabled."
            )

        if args.dirs_first:
            _warn("--dirs-first has no effect when --folders-only is active.")

    # regex validation
    valid_patterns = []
    for pattern in getattr(args, "regex_exclude", []):
        try:
            valid_patterns.append(re.compile(pattern))
        except re.error as exc:
            _warn(f"Invalid regex '{pattern}': {exc}")
    args.regex_exclude = valid_patterns

    # ----------------------------------------------------------------- #
    # legacy filter:
    # conflicting include / exclude directories
    conflicting_dirs = set(args.ex_dirs) & set(args.add_dirs)
    if conflicting_dirs:
        _warn(
            "Directories specified in both exclude and include: "
            f"{sorted(conflicting_dirs)}. "
            "Inclusion takes priority."
        )

    # conflicting include / exclude files
    conflicting_files = set(args.ex_files) & set(args.add_files)
    if conflicting_files:
        _warn(
            "Files specified in both exclude and include: "
            f"{sorted(conflicting_files)}. "
            "Inclusion takes priority."
        )
    # ----------------------------------------------------------------- #
    # new:
    conflicting_patterns = set(getattr(args, "exclude", [])) & set(
        getattr(args, "include", [])
    )
    if conflicting_patterns:
        _warn(
            "Patterns specified in both exclude (-I) and include (-A): "
            f"{sorted(list(conflicting_patterns))}. "
            "Inclusion takes priority."
        )


def _validate_values(args: argparse.Namespace) -> None:
    # human-readable without size
    if args.human_readable and not args.show_size:
        _warn("--human has no effect unless --size is enabled.")

    # negative depth protection
    if args.max_depth is not None and args.max_depth < 0:
        _warn(
            f"--max-depth cannot be negative ({args.max_depth}). "
            "It will be treated as 0."
        )
        args.max_depth = 0
