# ltree/cli/commands/tree.py
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from ltree.app.tree import TreeApplication
from ltree.cli.config_builder import build_config
from ltree.cli.validators import validate_tree_args
from ltree.rendering.utils import print_stats

if TYPE_CHECKING:
    from argparse import Namespace


def run_tree(args: Namespace) -> None:
    validate_tree_args(args)

    config = build_config(args)

    app = TreeApplication(config)
    result = app.generate(args.start_path, args.max_depth, args.format)

    is_console = args.output == "-"
    if is_console:
        sys.stdout.write(result.content + "\n")
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.content + "\n")
        print(f"Directory tree written to {args.output}")

    if is_console and result.show_stats:
        print_stats(result.root, config, args.format)
