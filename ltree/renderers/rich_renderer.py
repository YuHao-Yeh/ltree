# ltree/renderers/rich_renderer.py
import os
from rich.console import Console
from rich.filesize import decimal as format_size
from rich.text import Text
from rich.tree import Tree
from typing import TYPE_CHECKING

from ltree.renderers.base import BaseRenderer
from ltree.core.models import NodeType

if TYPE_CHECKING:
    from typing import TextIO
    from ltree.serializers.types import SerializedNode


class RichRenderer(BaseRenderer):
    def render(self, node: "SerializedNode", output_file: "TextIO") -> None:
        color_sys = "auto" if self.config.use_color else None
        is_a_tty = hasattr(output_file, "isatty") and output_file.isatty()
        console_width = None if is_a_tty else 1000

        console = Console(
            file=output_file,
            force_terminal=is_a_tty,
            color_system=color_sys,
            width=console_width,
        )

        root_label = self._build_node_label(node, is_root=True)
        rich_tree = Tree(root_label)

        self._render_recursive(node, rich_tree)
        console.print(rich_tree)

    def _build_node_label(self, node: "SerializedNode", is_root: bool = False) -> Text:
        text = Text()

        icon = self.theme_manager.get_icon(node)
        text.append(icon)

        path_display = str(node["path"]).replace("/", os.sep)
        display_name = (
            path_display if (self.config.full_path and not is_root) else node["name"]
        )

        style = self.theme_manager.get_style(node)
        text.append(display_name, style=style)

        if self.config.show_size:
            size_str = format_size(node["metadata"].get("fs")["size"])
            text.append(f" ({size_str.strip()})", style="dim")

        return text

    def _render_recursive(self, node: "SerializedNode", rich_tree: Tree) -> None:
        # Truncated
        if node["is_truncated"] and self.config.show_ellipsis:
            stats = node["stats"]
            if self.config.folders_only:
                text = f"... ({stats["hidden_dirs"]} dirs)"
            else:
                text = (
                    f"... ({stats["hidden_dirs"]} dirs, {stats["hidden_files"]} files)"
                )

            rich_tree.add(Text(text, style="yellow"))
            return

        children: list["SerializedNode"] = node.get("children", [])
        for child in children:
            child_label = self._build_node_label(child, is_root=False)
            child_rich_node = rich_tree.add(child_label)

            if (child["type"] == NodeType.DIR.value) and (
                child.get("children") or child["is_truncated"]
            ):
                self._render_recursive(child, child_rich_node)
