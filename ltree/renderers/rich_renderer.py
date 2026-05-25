import os
from rich.tree import Tree
from rich.console import Console
from rich.filesize import decimal as format_size
from typing import TextIO

from .base import BaseRenderer
from ..core.models import TreeNode
from ..constants import RICH_COLOR_DIR, RICH_COLOR_FILE


class RichRenderer(BaseRenderer):
    def render(self, node: TreeNode, output_file: TextIO) -> None:
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

    def _build_node_label(self, node: TreeNode, is_root: bool = False) -> str:
        icon = self.icon_provider.get_icon(node.name, node.is_dir)
        path_display = node.path.replace("/", os.sep)
        display_name = (
            path_display if (self.config.full_path and not is_root) else node.name
        )

        if node.is_dir:
            name_label = f"{RICH_COLOR_DIR}{display_name}[/]"
        else:
            name_label = f"{RICH_COLOR_FILE}{display_name}[/]"

        label = f"{icon}{name_label}"

        if self.config.show_size:
            size_str = format_size(node.size)
            label += f" [dim]({size_str.strip()})[/]"

        return label

    def _render_recursive(self, node: TreeNode, rich_tree: Tree) -> None:
        # Truncated
        if node.is_truncated and self.config.show_ellipsis:
            stats = node.stats
            if self.config.folders_only:
                text = f"... ({stats.hidden_dirs} dirs)"
            else:
                text = f"... ({stats.hidden_dirs} dirs, {stats.hidden_files} files)"

            rich_tree.add(f"[yellow]{text}[/]")
            return

        for child in node.children:
            child_label = self._build_node_label(child, is_root=False)
            child_rich_node = rich_tree.add(child_label)

            if child.is_dir and (child.children or child.is_truncated):
                self._render_recursive(child, child_rich_node)
