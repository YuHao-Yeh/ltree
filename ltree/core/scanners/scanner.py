# ltree/core/scanners/scanner.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.core.metadata import MetadataPipeline, get_default_pipeline
from ltree.core.scanners.aggregation import aggregate_tree
from ltree.core.scanners.filters import CompositeFilter
from ltree.core.scanners.traversal import traverse_path

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode


class Scanner:
    def __init__(
        self,
        config: "TreeConfig",
        pipeline: MetadataPipeline | None = None,
        node_filter: CompositeFilter | None = None,
    ):
        self.config = config
        self.pipeline = pipeline or get_default_pipeline(config)
        self.node_filter = node_filter or CompositeFilter()

    def scan(self, path: Path | str, max_depth: int | None = None) -> "TreeNode" | None:
        root_path = Path(path).resolve()
        if not root_path.exists():
            print(f"Error: Path '{path}' does not exist.", file=sys.stderr)
            return None

        self.config.root_path = str(root_path)
        self.config.load_gitignore(self.config.root_path)

        root_node = traverse_path(
            root_path,
            self.config,
            max_depth=max_depth,
            curr_depth=0,
            pipeline=self.pipeline,
            node_filter=self.node_filter,
        )

        if root_node:
            aggregate_tree(root_node)

        return root_node


def scan_tree(
    path: str | Path,
    config: "TreeConfig",
    max_depth: int | None = None,
) -> "TreeNode" | None:
    scanner = Scanner(config)
    return scanner.scan(path, max_depth=max_depth)
