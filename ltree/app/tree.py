# ltree/app/tree.py
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ltree.core.scanners.scanner import scan_tree
from ltree.core.filters import get_default_filter_pipeline
from ltree.serializers import TreeSerializer
from ltree.renderers import get_renderer_class

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.renderers import BaseRenderer


@dataclass(slots=True)
class RenderResult:
    content: str
    rtype: str


class TreeApplication:
    def __init__(self, config: TreeConfig):
        self.config = config

    def generate(
        self, start_path: str, max_depth: int | None = None, fmt: str = "text"
    ) -> RenderResult:
        # 1. scan
        root = scan_tree(path=start_path, config=self.config, max_depth=max_depth)
        if not root:
            return ""

        # 2. filter
        tree_filter = get_default_filter_pipeline(self.config, max_depth)
        root = tree_filter.apply(root)

        # 3. render
        RendererClass = get_renderer_class(fmt)
        renderer: BaseRenderer = RendererClass(self.config)

        # 4. serialize
        if renderer.input_type == "serialized":
            serializer = TreeSerializer(self.config)
            root_node = serializer.serialize(root)
            return RenderResult(
                content=renderer.render(root_node), rtype=renderer.input_type
            )
        else:
            return RenderResult(
                content=renderer.render(root), rtype=renderer.input_type
            )
