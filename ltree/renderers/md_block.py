# ltree/renderers/md_block.py
from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from ltree.renderers.base import BaseRenderer
from ltree.renderers.text import TextRenderer

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode


class MarkdownBlockRenderer(BaseRenderer):
    input_type = "row"

    def __init__(self, config: TreeConfig):
        super().__init__(config)

    def render(self, node: TreeNode) -> str:
        clean_config = copy.copy(self.config)
        clean_config.use_color = False

        text_tree = TextRenderer(clean_config).render(node)

        return f"```text\n{text_tree}\n```"
