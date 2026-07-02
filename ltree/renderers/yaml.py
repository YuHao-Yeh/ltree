# ltree/renderers/yaml.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ltree.renderers.base import BaseRenderer

if TYPE_CHECKING:
    from ltree.serializers.types import SerializedNode
    from ltree.core.config import TreeConfig


class YamlRenderer(BaseRenderer):
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
