# ltree/rendering/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, TYPE_CHECKING

from ltree.themes.manager import ThemeManager

if TYPE_CHECKING:
    from typing import TextIO
    from ltree.config.config import TreeConfig
    from ltree.serialization.types import SerializedNode
    from ltree.tree.models import TreeNode


class BaseRenderer(ABC):
    name: str = ""
    aliases: list[str] = []
    input_type: Literal["row", "serialized"] = "serialized"
    support_theme: bool = False

    def __init__(self, config: TreeConfig, **kwargs):
        self.config = config
        self.theme_manager = ThemeManager(config.theme)

    @abstractmethod
    def render(self, node: SerializedNode | TreeNode, output_file: TextIO) -> None:
        pass

    def prepare(self, root: TreeNode) -> TreeNode | SerializedNode:
        if self.input_type == "serialized":
            from ltree.serialization.tree import TreeSerializer

            serializer = TreeSerializer(self.config)
            return serializer.serialize(root)

        return root
