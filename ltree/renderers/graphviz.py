# ltree/renderers/graphviz.py
from __future__ import annotations

from typing import TYPE_CHECKING
from ltree.renderers.base import BaseRenderer

if TYPE_CHECKING:
    from ltree.serializers.types import SerializedNode
    from ltree.core.config import TreeConfig


class GraphvizRenderer(BaseRenderer):
    input_type = "serialized"
    support_theme = True

    def __init__(self, config: TreeConfig):
        super().__init__(config)
        self._node_counter = 0

    def render(self, node: SerializedNode) -> str:
        lines = []
        lines.append("digraph G {")
        lines.append("  rankdir=LR;")
        lines.append('  bgcolor="#0b0e14";')
        lines.append(
            '  node [shape=box, style="filled,rounded", color="#00d2ff", fillcolor="#161b22", fontname="JetBrains Mono", fontcolor="#ffffff", fontsize=10];'
        )
        lines.append('  edge [color="#444444", arrowhead=vee, arrowsize=0.8];')

        self._node_counter = 0
        self._render_recursive(node, lines, parent_id=None)

        lines.append("}")
        return "\n".join(lines)

    def _render_recursive(
        self, node: SerializedNode, lines: list[str], parent_id: str | None
    ) -> str:
        current_id = f"node{self._node_counter}"
        self._node_counter += 1

        is_dir = node["type"] == "directory"
        color = "#00d2ff" if is_dir else "#888888"
        icon = self.theme_manager.get_icon(node).strip()

        label = f"{icon} {node['name']}"
        if not is_dir:
            fs = node.get("metadata", {}).get("fs", {})
            size_val = (
                fs.get("size_human") if self.config.human_readable else fs.get("size")
            )
            if self.config.show_size and size_val is not None:
                unit = "" if self.config.human_readable else " B"
                label += f" ({size_val}{unit})"

        lines.append(f'  {current_id} [label="{label}", color="{color}"];')

        if parent_id is not None:
            lines.append(f"  {parent_id} -> {current_id};")

        children = node.get("children", [])
        for child in children:
            self._render_recursive(child, lines, parent_id=current_id)

        return current_id
