# ltree/cli/config_builder.py
from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

from ltree.core.config import TreeConfig

if TYPE_CHECKING:
    from argparse import Namespace


def build_config(args: Namespace) -> TreeConfig:
    config = TreeConfig()

    # 1. preset profile (.ltreerc / pyproject.toml)
    start_path = getattr(args, "start_path", ".")
    config.load_config_file(start_path)

    # 2. common settings
    config.use_gitignore = args.gitignore

    # output fmtargs.format
    if args.color:
        config.use_color = True
    # metadata
    if not args.show_permission:
        config.show_permission = False
    if not args.show_git:
        config.show_git = False
    if not args.show_size:
        config.show_size = False
    if args.human_readable:
        config.human_readable = True
    if not args.show_mtime:
        config.show_time = False
    if args.show_code:
        config.show_code = True
    if args.show_project:
        config.show_project = True
    # filter rules
    if args.show_all:
        config.show_all = True
    if args.folders_only:
        config.folders_only = True
    if args.dirs_first:
        config.dirs_first = True
    # display options
    if args.full_path:
        config.full_path = True
    if args.show_ellipsis:
        config.show_ellipsis = True

    # 3. theme
    if args.theme:
        config.theme = args.theme

    # 4. regex
    regex_patterns = getattr(args, "regex_exclude", [])
    for pattern in regex_patterns:
        try:
            config.regex_exclude_patterns.append(re.compile(pattern))
        except re.error as e:
            print(f"Warning: Invalid regex '{pattern}': {e}", file=sys.stderr)

    # 5. include & exclude
    for dir in args.add_dirs:
        config.exclude_dirs.discard(dir)
        config.added_items.add(dir)
    for file in args.add_files:
        config.exclude_files.discard(file)
        config.added_items.add(file)

    for dir in args.ex_dirs:
        config.exclude_dirs.add(dir)
    for file in args.ex_files:
        config.exclude_files.add(file)
    for ext in args.ex_ext:
        config.exclude_exts.add(ext)
    for pre in args.ex_prefix:
        config.exclude_prefixes.add(pre)

    # 6. color setting
    if args.output != "-":
        config.use_color = False

    # 7. update patterns
    config._prepare_patterns()

    return config
