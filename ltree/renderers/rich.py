# ltree/renderers/rich.py
from __future__ import annotations

from typing import TYPE_CHECKING
from rich.console import Console
from rich.text import Text

from ltree.renderers.base import BaseRenderer
from ltree.renderers.row_builder import RowBuilder
from ltree.core.metadata.models import GitStatus

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode
    from ltree.renderers.models import RenderRow


GIT_STYLES = {
    GitStatus.MODIFIED: "yellow",
    GitStatus.ADDED: "green",
    GitStatus.DELETED: "red",
    GitStatus.RENAMED: "blue",
    GitStatus.COPIED: "cyan",
    GitStatus.UNTRACKED: "cyan",
    GitStatus.IGNORED: "dim",
    GitStatus.UNMERGED: "bold red",
    GitStatus.TYPE_CHANGED: "magenta",
    GitStatus.DIRTY: "yellow",
    GitStatus.CLEAN: "white",
}


class RichRenderer(BaseRenderer):
    input_type = "row"
    support_theme = True

    def __init__(self, config: TreeConfig):
        super().__init__(config)
        self.row_builder = RowBuilder(self.config, self.theme_manager)

    def render(self, node: TreeNode) -> str:
        lines: list[Text] = []
        self._render_recursive(node, lines, prefix="", is_last=True, is_root=True)

        color_sys = "auto" if self.config.use_color else None
        console = Console(
            color_system=color_sys,
            force_terminal=self.config.use_color,
            width=1000,
        )

        with console.capture() as capture:
            for line in lines:
                console.print(line)

        return capture.get().rstrip("\n")

    def _render_recursive(
        self,
        node: TreeNode,
        lines: list[Text],
        prefix: str,
        is_last: bool,
        is_root: bool,
    ) -> None:
        if is_root:
            tree_prefix = ""
        else:
            tree_prefix = "└── " if is_last else "├── "

        row = self.row_builder.build(node)

        line = self._format_row(row, prefix, tree_prefix)
        lines.append(line)

        if row.details:
            for detail in row.details:
                meta_prefix = self._format_metadata_prefix(row)
                sub_indent = prefix + ("    " if is_last else "│   ")

                detail_line = Text()
                detail_line.append(" " * len(meta_prefix.plain))
                detail_line.append(f"{sub_indent}└── ", style="dim")
                detail_line.append(detail.text, style="dim italic")

                lines.append(detail_line)

        new_prefix = prefix if is_root else prefix + ("    " if is_last else "│   ")
        children = node.children
        for i, child in enumerate(children):
            self._render_recursive(
                child, lines, new_prefix, i == len(children) - 1, False
            )

    def _format_metadata_prefix(self, row: RenderRow) -> Text:
        prefix = Text()

        # A. PERM - dim cyan
        if self.config.show_permission:
            perm_text = (
                f"{row.permission.text:<10}" if row.permission.text else "-" * 10
            )
            prefix.append(perm_text, style="dim cyan")
            prefix.append("  ")

        # B. GIT - dynamic coloring (based on state)
        if self.config.show_git:
            git_style = GIT_STYLES.get(row.git.status, "white")
            prefix.append(f"{row.git.text:^2}", style=git_style)
            prefix.append("  ")

        # C. SIZE - dim
        if self.config.show_size:
            prefix.append(f"{row.size.text:>8}", style="dim")
            prefix.append("  ")

        # D. TIME - green
        if self.config.show_time:
            prefix.append(f"{row.time.text:>10}", style="green")
            prefix.append("  ")

        return prefix

    def _format_row(self, row: RenderRow, prefix: str, tree_prefix: str) -> Text:
        line = self._format_metadata_prefix(row)
        line.append(f"{prefix}{tree_prefix}", style="dim")
        line.append(f"{row.icon}")

        if row.is_dir:
            line.append(row.name + "/", style="bold cyan")
        else:
            line.append(row.name, style="white")

        return line
