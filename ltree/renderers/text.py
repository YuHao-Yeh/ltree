# ltree/renderers/text.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ltree.renderers.base import BaseRenderer
from ltree.renderers.row_builder import RowBuilder
from ltree.renderers.models import RenderRow

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode


class TextRenderer(BaseRenderer):
    input_type = "row"
    support_theme = True

    def __init__(self, config: TreeConfig):
        super().__init__(config)
        self.row_builder = RowBuilder(self.config, self.theme_manager)

    def render(self, node: "TreeNode") -> None:
        lines = []
        self._render_recursive(node, lines, prefix="", is_last=True, is_root=True)
        return "\n".join(lines)

    def _render_recursive(
        self, node: "TreeNode", lines: list, prefix: str, is_last: bool, is_root: bool
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
                meta_width = len(self._format_metadata_prefix(row))
                sub_indent = prefix + ("    " if is_last else "│   ")
                lines.append(f"{' ' * meta_width}" f"{sub_indent}" f"└── {detail.text}")

        new_prefix = prefix if is_root else prefix + ("    " if is_last else "│   ")
        children = node.children
        for i, child in enumerate(children):
            self._render_recursive(
                child, lines, new_prefix, i == len(children) - 1, False
            )

    def _format_metadata_prefix(self, row: RenderRow) -> str:
        # Alignment: PERM(10), GIT(2), SIZE(8), TIME(10)
        meta = []
        if self.config.show_permission:
            meta.append(
                f"{row.permission.text:<10}" if row.permission.text else "-" * 10
            )
        if self.config.show_git:
            meta.append(f"{row.git.text:^2}")
        if self.config.show_size:
            meta.append(f"{row.size.text:>8}")
        if self.config.show_time:
            meta.append(f"{row.time.text:>10}")

        return "  ".join(meta) + "  "

    def _format_row(self, row: RenderRow, prefix: str, tree_prefix: str) -> str:
        meta_prefix = self._format_metadata_prefix(row)
        branch_and_name = f"{prefix}{tree_prefix}{row.icon}{row.name}"
        if row.is_dir:
            branch_and_name += "/"
        return f"{meta_prefix}{branch_and_name}"
