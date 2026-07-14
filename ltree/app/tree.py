# ltree/app/tree.py
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ltree.rendering import registry
from ltree.tree.filters import get_default_filter_pipeline
from ltree.tree.scan.scanner import scan_tree

if TYPE_CHECKING:
    from ltree.config.config import TreeConfig
    from ltree.rendering import BaseRenderer
    from ltree.tree.models import TreeNode


@dataclass(slots=True)
class RenderResult:
    content: str
    root: TreeNode | None = None
    show_stats: bool = False


class TreeApplication:
    def __init__(self, config: TreeConfig):
        self.config = config

    def generate(
        self, start_path: str, max_depth: int | None = None, fmt: str = "text"
    ) -> RenderResult:
        # 1. scan
        root = scan_tree(path=start_path, config=self.config, max_depth=max_depth)
        if not root:
            return RenderResult(content="", show_stats=False)

        # 2. filter
        tree_filter = get_default_filter_pipeline(self.config, max_depth)
        root = tree_filter.apply(root)

        # 3. render
        RendererClass = registry.get(fmt)
        if RendererClass is None:
            raise ValueError(f"Unknown renderer: {fmt}")
        renderer: BaseRenderer = RendererClass(self.config)

        # 4. serialize
        data = renderer.prepare(root)
        content = renderer.render(data)
        return RenderResult(
            content=content,
            root=root,
            show_stats=renderer.input_type == "row",
        )
