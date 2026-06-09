# ltree/renderers/markdown.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ltree.renderers.base import BaseRenderer

if TYPE_CHECKING:
    from ltree.serializers.types import SerializedNode
    from ltree.core.config import TreeConfig


class MarkdownRenderer(BaseRenderer):
    input_type = "serialized"

    def __init__(self, config: TreeConfig):
        super().__init__(config)

    def render(self, node: SerializedNode) -> str:
        lines: list[str] = []
        self._render_recursive(node, lines, depth=0)
        return "\n".join(lines)

    def _render_recursive(
        self, node: SerializedNode, lines: list[str], depth: int
    ) -> None:
        indent = "  " * depth
        icon = self.theme_manager.get_icon(node)

        size_str = ""
        if self.config.show_size:
            fs = node["metadata"].get("fs", {})
            size_val, unit = fs.get("size"), "B"

            if self.config.human_readable:
                size_val = fs.get("size_human")
                unit = ""

            if size_val is not None:
                display_val = f"{size_val} {unit}".strip()
                size_str = f"`{display_val}` "

        version_str = ""
        if self.config.show_project:
            project = node["metadata"].get("project", {})
            version = project.get("version")
            if version is not None:
                version_str = f" (v{version})"

        is_dir = bool(node["type"] == "directory")
        name_display = f"**{node['name']}/**" if is_dir else f"`{node['name']}`"

        lines.append(f"{indent}- {icon}{size_str}{name_display}{version_str}")

        # Truncated
        if node["is_truncated"] and self.config.show_ellipsis:
            sub_indent = "  " * (depth + 1)
            stats = node.get("stats", {})
            if self.config.folders_only:
                lines.append(f"{sub_indent}- ... ({stats.get('hidden_dirs', 0)} dirs)")
            else:
                lines.append(
                    f"{sub_indent}- ... ({stats.get('hidden_dirs', 0)} dirs, {stats.get('hidden_files', 0)} files)"
                )
            return

        children = node.get("children", [])
        for child in children:
            self._render_recursive(child, lines, depth + 1)
