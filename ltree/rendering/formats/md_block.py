# ltree/rendering/formats/md_block.py
from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from ltree.rendering.base import BaseRenderer
from ltree.rendering.formats.text import TextRenderer

if TYPE_CHECKING:
    from ltree.config.config import TreeConfig
    from ltree.tree.models import TreeNode


class MarkdownBlockRenderer(BaseRenderer):
    name = "block"
    aliases = []
    input_type = "row"
    support_theme = True

    def __init__(self, config: TreeConfig):
        super().__init__(config)

    def render(self, node: TreeNode) -> str:
        clean_config = copy.copy(self.config)
        clean_config.use_color = False

        text_tree = TextRenderer(clean_config).render(node)

        return f"```text\n{text_tree}\n```"
