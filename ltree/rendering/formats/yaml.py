# ltree/rendering/formats/yaml.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ltree.rendering.base import BaseRenderer

if TYPE_CHECKING:
    from ltree.config.config import TreeConfig
    from ltree.serialization.types import SerializedNode


class YamlRenderer(BaseRenderer):
    name = "yaml"
    aliases = []
    input_type = "serialized"
    support_theme = False

    def __init__(self, config: TreeConfig, **kwargs):
        super().__init__(config)
        self.indent: int = kwargs.get("indent", 2)
        self.sort_keys: bool = kwargs.get("sort_keys", False)

    def render(self, node: SerializedNode) -> str:
        try:
            import yaml
        except ImportError:
            return (
                "Error: No available 'pyyaml' library for YAML export.\n"
                "Install it using: `pip install pyyaml`"
            )

        return yaml.dump(
            node,
            default_flow_style=False,
            indent=self.indent,
            allow_unicode=True,
            sort_keys=self.sort_keys,
        )
