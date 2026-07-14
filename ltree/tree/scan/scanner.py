# ltree/tree/scan/scanner.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.metadata import MetadataPipeline, get_default_pipeline
from ltree.tree.scan.aggregation import aggregate_tree
from ltree.tree.scan.ignore import CompositeFilter
from ltree.tree.scan.traversal import traverse_path

if TYPE_CHECKING:
    from ltree.config.config import TreeConfig
    from ltree.tree.models import TreeNode


logger = logging.getLogger(__name__)


class Scanner:
    def __init__(
        self,
        config: TreeConfig,
        pipeline: MetadataPipeline | None = None,
        node_filter: CompositeFilter | None = None,
    ):
        self.config = config
        self.pipeline = pipeline or get_default_pipeline(config)
        self.node_filter = node_filter or CompositeFilter()

    def scan(self, path: Path | str, max_depth: int | None = None) -> "TreeNode" | None:
        root_path = Path(path).resolve()
        if not root_path.exists():
            logger.error("Path '%s' does not exist.", path)
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
    config: TreeConfig,
    max_depth: int | None = None,
) -> TreeNode | None:
    return Scanner(config).scan(path, max_depth=max_depth)
