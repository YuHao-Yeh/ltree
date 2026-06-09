# ltree/renderers/html.py
from __future__ import annotations

from typing import TYPE_CHECKING
from ltree.renderers.base import BaseRenderer
from ltree.renderers.models import GIT_SYMBOL_MAP

if TYPE_CHECKING:
    from ltree.serializers.types import SerializedNode
    from ltree.core.config import TreeConfig


class HtmlRenderer(BaseRenderer):
    input_type = "serialized"

    def __init__(self, config: TreeConfig):
        super().__init__(config)

    def render(self, node: SerializedNode) -> str:
        lines = []
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append('  <meta charset="utf-8">')
        lines.append("  <title>ltree Directory Directory</title>")  # TBD
        lines.append("  <style>")
        lines.append(
            "    body { background-color: #0b0e14; color: #ffffff; font-family: 'JetBrains Mono', 'Fira Code', monospace; padding: 30px; font-size: 14px; }"
        )
        lines.append(
            "    .tree-table { border-collapse: collapse; width: 100%; margin-top: 20px; }"
        )
        lines.append(
            "    .tree-row { height: 28px; border-bottom: 1px solid #1a1f29; }"
        )
        lines.append("    .tree-row:hover { background-color: #161b22; }")
        lines.append("    .col-perm { width: 100px; color: #00d2ff; opacity: 0.8; }")
        lines.append(
            "    .col-git { width: 40px; text-align: center; font-weight: bold; }"
        )
        lines.append("    .col-git.modified { color: #ffd700; }")
        lines.append("    .col-git.added { color: #00ff88; }")
        lines.append(
            "    .col-size { width: 100px; text-align: right; color: #888888; }"
        )
        lines.append(
            "    .col-time { width: 100px; text-align: right; color: #00e676; }"
        )
        lines.append(
            "    .col-sep { width: 30px; text-align: center; color: #444444; }"
        )
        lines.append("    .col-tree { padding-left: 10px; }")
        lines.append("    .folder { color: #00d2ff; font-weight: bold; }")
        lines.append("    .file { color: #ffffff; }")
        lines.append("    .indent { color: #444444; white-space: pre; }")
        lines.append(
            "    .detail-text { color: #888888; font-size: 12px; font-style: italic; opacity: 0.7; }"
        )
        lines.append("  </style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append('  <table class="tree-table">')

        self._render_recursive(node, lines, indent_str="", is_last=True, is_root=True)

        lines.append("  </table>")
        lines.append("</body>")
        lines.append("</html>")

        return "\n".join(lines)

    def _render_recursive(
        self,
        node: SerializedNode,
        lines: list[str],
        indent_str: str,
        is_last: bool,
        is_root: bool,
    ) -> None:
        meta = node.get("metadata", {})
        fs = meta.get("fs", {})
        git = meta.get("git", {})
        time_meta = meta.get("time", {})

        perm = fs.get("permissions", "") if self.config.show_permission else ""

        git_text = ""
        git_class = ""
        if self.config.show_git and git.get("tracked"):
            status = git.get("status", "clean")
            git_text = GIT_SYMBOL_MAP.get(status, "")
            git_class = status

        size_text = ""
        if self.config.show_size and fs:
            size_bytes = fs.get("size", 0)
            if node["type"] == "file" or size_bytes > 0:
                size_val = (
                    fs.get("size_human") if self.config.human_readable else size_bytes
                )
                unit = "" if self.config.human_readable else " B"
                size_text = f"{size_val}{unit}"

        time_text = (
            time_meta.get("relative_modified", "") if self.config.show_time else ""
        )

        tree_prefix = "" if is_root else ("└── " if is_last else "├── ")
        icon = self.theme_manager.get_icon(node)
        is_dir = node["type"] == "directory"
        name_class = "folder" if is_dir else "file"

        lines.append('    <tr class="tree-row">')
        lines.append(f'      <td class="col-perm">{perm}</td>')
        lines.append(f'      <td class="col-git {git_class}">{git_text}</td>')
        lines.append(f'      <td class="col-size">{size_text}</td>')
        lines.append(f'      <td class="col-time">{time_text}</td>')
        lines.append('      <td class="col-sep"></td>')
        lines.append('      <td class="col-tree">')
        lines.append(f'        <span class="indent">{indent_str}{tree_prefix}</span>')
        lines.append(f"        <span>{icon} </span>")
        lines.append(f'        <span class="{name_class}">{node["name"]}</span>')
        lines.append("      </td>")
        lines.append("    </tr>")

        detail_text = ""
        if is_dir and node.get("is_truncated") and self.config.show_ellipsis:
            stats = node.get("stats", {})
            detail_text = f".. ({stats.get('hidden_dirs', 0)} dirs, {stats.get('hidden_files', 0)} files)"
        elif self.config.show_project and meta.get("project", {}).get("project_type"):
            p = meta["project"]
            detail_text = (
                f"{p.get('name')} v{p.get('version')} ({p.get('project_type')})"
            )

        if detail_text:
            lines.append('    <tr class="tree-row">')
            lines.append('      <td colspan="5"></td>')
            lines.append('      <td class="col-tree">')
            sub_indent = indent_str + ("    " if is_last else "│   ")
            lines.append(f'        <span class="indent">{sub_indent}└── </span>')
            lines.append(f'        <span class="detail-text">{detail_text}</span>')
            lines.append("      </td>")
            lines.append("    </tr>")

        new_indent = (
            indent_str if is_root else indent_str + ("    " if is_last else "│   ")
        )
        children = node.get("children", [])
        for i, child in enumerate(children):
            self._render_recursive(
                child, lines, new_indent, i == len(children) - 1, False
            )
