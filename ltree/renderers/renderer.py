# ltree/renderers/exporters.py
import json
import os
from rich.console import Console
from rich.filesize import decimal as format_size_rich
from typing import TYPE_CHECKING

from .base import BaseRenderer
from ltree.core.models import NodeType
from ltree.constants import ANSI_COLOR_DIR, ANSI_COLOR_FILE, ANSI_COLOR_RESET
from ltree.core.utils import write_line, format_size_classic

if TYPE_CHECKING:
    from typing import TextIO
    from ltree.core.config import TreeConfig
    from ltree.serializers.types import SerializedNode


def print_stats(
    node: "SerializedNode", config: "TreeConfig", fmt: str = "text"
) -> None:
    s = node["stats"]
    size_str = ""
    if config.show_size:
        size = node["metadata"].get("fs")["size"]
        if fmt == "rich":
            size_str = f" ({format_size_rich(size)})"
        else:
            size_str = f" ({format_size_classic(size, config.human_readable).strip()})"

    if fmt == "rich":
        console = Console()
        console.print(f"\n[bold blue]Summary[/]{size_str}:", style="none")
        console.print(
            f"  Visible: [bold cyan]{s["visible_dirs"]:>3}[/] directories, "
            f"[bold cyan]{s["visible_files"]:>3}[/] files"
        )
        console.print(
            f"  Total  : [bold magenta]{s["total_dirs"]:>3}[/] directories, "
            f"[bold magenta]{s["total_files"]:>3}[/] files"
        )
    else:
        print(f"\nSummary{size_str}:")
        print(
            f"Visible: {s["visible_dirs"]:>3} directories, {s["visible_files"]:>3} files"
        )
        print(f"Total  : {s["total_dirs"]:>3} directories, {s["total_files"]:>3} files")


class TextRenderer(BaseRenderer):
    def render(self, node: "SerializedNode", output_file: "TextIO") -> None:
        self._render_recursive(node, output_file, "", True, True)

    def _render_recursive(
        self,
        node: "SerializedNode",
        file: "TextIO",
        indent: str,
        is_last: bool,
        is_root: bool,
    ) -> None:
        path_display = node["path"].replace("/", os.sep)
        name = path_display if self.config.full_path and not is_root else node["name"]
        is_dir = bool(node["type"] == NodeType.DIR.value)
        display_name = name + (os.sep if is_dir and not name.endswith(os.sep) else "")
        icon = self.theme_manager.get_icon(node)

        size_str = ""
        if self.config.show_size:
            size = node["metadata"].get("fs")["size"]
            size_str = f"[{format_size_classic(size, self.config.human_readable)}] "

        if is_root:
            write_line(file, size_str + icon + display_name)
        else:
            branch = "└── " if is_last else "├── "
            if self.config.use_color:
                color = ANSI_COLOR_DIR if is_dir else ANSI_COLOR_FILE
                display_name = f"{color}{display_name}{ANSI_COLOR_RESET}"
            write_line(file, indent + branch + size_str + icon + display_name)

        # Truncated
        if node["is_truncated"] and self.config.show_ellipsis:
            ellipsis_indent = indent + ("    " if is_last else "│   ")
            stats = node["stats"]
            if self.config.folders_only:
                text = f"... ({stats["hidden_dirs"]} dirs)"
            else:
                text = (
                    f"... ({stats["hidden_dirs"]} dirs, {stats["hidden_files"]} files)"
                )
            write_line(file, f"{ellipsis_indent}└── {text}")
            return

        new_indent = indent if is_root else indent + ("    " if is_last else "│   ")
        children = node.get("children", [])
        for i, child in enumerate(children):
            self._render_recursive(
                child, file, new_indent, i == len(children) - 1, False
            )


class JsonRenderer(BaseRenderer):
    def render(self, node: "SerializedNode", output_file: "TextIO") -> None:
        def to_dict(n: "SerializedNode"):
            size = n["metadata"].get("fs")["size"]
            stats = n["stats"]
            is_dir = bool(n["type"] == NodeType.DIR.value)
            d = {
                "name": n["name"],
                "path": n["path"].replace("\\", "/"),
                "type": "directory" if is_dir else "file",
                "size_bytes": size,
            }
            if self.config.human_readable:
                d["size_human"] = format_size_classic(size, True).strip()

            if is_dir:
                d["content_summary"] = {
                    "folders": stats["total_dirs"],
                    "files": stats["total_files"],
                }

                if n["is_truncated"]:
                    d["is_truncated"] = True
                    d["hidden_summary"] = {
                        "hidden_folders": stats["hidden_dirs"],
                        "hidden_files": stats["hidden_files"],
                    }
                else:
                    children = n.get("children", [])
                    d["is_truncated"] = False
                    d["children"] = [to_dict(c) for c in children]
            return d

        json.dump(to_dict(node), output_file, indent=4, ensure_ascii=False)


class MarkdownRenderer(BaseRenderer):
    def render(self, node: "SerializedNode", output_file: "TextIO") -> None:
        self._render_recursive(node, output_file, 0)

    def _render_recursive(
        self, node: "SerializedNode", file: "TextIO", depth: int = 0
    ) -> None:
        indent = "  " * depth
        icon = self.theme_manager.get_icon(node)

        size_str = ""
        if self.config.show_size:
            size = node["metadata"].get("fs")["size"]
            size_str = (
                f"`{format_size_classic(size, self.config.human_readable).strip()}` "
            )

        is_dir = bool(node["type"] == NodeType.DIR.value)
        name_display = f"**{node["name"]}/**" if is_dir else f"`{node["name"]}`"
        write_line(file, f"{indent}- {icon}{size_str}{name_display}")

        # Truncated
        if node["is_truncated"] and self.config.show_ellipsis:
            indent = "  " * (depth + 1)
            stats = node["stats"]
            if self.config.folders_only:
                text = f"... ({stats["hidden_dirs"]} dirs)"
            else:
                text = (
                    f"... ({stats["hidden_dirs"]} dirs, {stats["hidden_files"]} files)"
                )
            write_line(file, f"{indent}- {text}")
            return

        children = node.get("children", [])
        for child in children:
            self._render_recursive(child, file, depth + 1)


class MarkdownBlockRenderer(BaseRenderer):
    def render(self, node: "SerializedNode", output_file: "TextIO") -> None:
        import copy

        tmp_config = copy.copy(self.config)
        tmp_config.use_color = False

        write_line(output_file, "```text")
        TextRenderer(tmp_config).render(node, output_file)
        write_line(output_file, "```")
