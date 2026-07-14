# ltree/rendering/formats/json.py
import json
from typing import TYPE_CHECKING

from ltree.rendering.base import BaseRenderer

if TYPE_CHECKING:
    from ltree.serialization.types import SerializedNode
    from ltree.config.config import TreeConfig


class JsonRenderer(BaseRenderer):
    name = "json"
    aliases = []
    input_type = "serialized"
    support_theme = False

    def __init__(self, config: "TreeConfig", **kwargs):
        super().__init__(config)
        self.indent: int = kwargs.get("indent", 2)
        self.ensure_ascii: bool = kwargs.get("ensure_ascii", False)

    def render(self, node: "SerializedNode") -> str:
        return json.dumps(node, indent=self.indent, ensure_ascii=self.ensure_ascii)
