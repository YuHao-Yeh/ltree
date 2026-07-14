# ltree/cli/config_builder.py
from __future__ import annotations

import logging
import re
import sys
from typing import TYPE_CHECKING

from ltree.core.config import TreeConfig

if TYPE_CHECKING:
    from argparse import Namespace

logger = logging.getLogger(__name__)


def build_config(args: Namespace) -> TreeConfig:
    config = TreeConfig()

    # 1. preset profile (.ltreerc / pyproject.toml)
    start_path = getattr(args, "start_path", ".")
    config.load_config_file(start_path)

    # 2. common settings
    config.use_gitignore = args.gitignore

    # output fmtargs.format
    if args.color is None:
        is_console = args.output == "-"
        config.use_color = is_console and sys.stdout.isatty()
    else:
        config.use_color = args.color
    # metadata
    if not args.show_permission:
        config.show_permission = False
    if not args.show_git:
        config.show_git = False
    if args.show_size:
        config.show_size = True
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
        if isinstance(pattern, re.Pattern):
            config.regex_exclude_patterns.append(pattern)
        else:
            try:
                config.regex_exclude_patterns.append(re.compile(pattern))
            except re.error as e:
                logger.warning("Invalid regex '%s': %s", pattern, e)

    # 5. include & exclude
    for pattern in getattr(args, "exclude", []):
        config.exclude.add_pattern(pattern)

    for pattern in getattr(args, "include", []):
        config.include.add_pattern(pattern)

    # 6. color setting
    if args.output != "-":
        config.use_color = False

    return config
