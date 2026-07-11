# ltree/renderers/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, TYPE_CHECKING

from ltree.serializers import TreeSerializer
from ltree.themes.manager import ThemeManager

if TYPE_CHECKING:
    from typing import TextIO
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode
    from ltree.serializers.types import SerializedNode


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
            serializer = TreeSerializer(self.config)
            return serializer.serialize(root)

        return root
