import json
import os
from rich.console import Console
from rich.filesize import decimal as format_size_rich
from typing import TextIO

from .base import BaseRenderer
from ..core.models import TreeNode
from ..core.config import TreeConfig
from ..constants import ANSI_COLOR_DIR, ANSI_COLOR_FILE, ANSI_COLOR_RESET
from ..core.utils import write_line, format_size_classic


def print_stats(node: TreeNode, config: TreeConfig, fmt: str = "text") -> None:
    s = node.stats
    size_str = ""
    if config.show_size:
        if fmt == "rich":
            size_str = f" ({format_size_rich(node.size)})"
        else:
            size_str = f" ({format_size_classic(node.size, config.human_readable).strip()})"

    if fmt == "rich":
        console = Console()
        console.print(f"\n[bold blue]Summary[/]{size_str}:", style="none")
        console.print(f"  Visible: [bold cyan]{s.visible_dirs:>3}[/] directories, [bold cyan]{s.visible_files:>3}[/] files")
        console.print(f"  Total  : [bold magenta]{s.total_dirs:>3}[/] directories, [bold magenta]{s.total_files:>3}[/] files")
    else:
        print(f"\nSummary{size_str}:")
        print(f"Visible: {s.visible_dirs:>3} directories, {s.visible_files:>3} files")
        print(f"Total  : {s.total_dirs:>3} directories, {s.total_files:>3} files")

class TextRenderer(BaseRenderer):
    def render(self, node: TreeNode, output_file: TextIO) -> None:
        self._render_recursive(node, output_file, "", True, True)

    def _render_recursive(self, node: TreeNode, file: TextIO, indent: str, 
                          is_last: bool, is_root: bool) -> None:
        path_display = node.path.replace("/", os.sep)
        name = path_display if self.config.full_path and not is_root else node.name
        display_name = name + (os.sep if node.is_dir and not name.endswith(os.sep) else "")
        icon = self.icon_provider.get_icon(node.name, node.is_dir)

        size_str = ""
        if self.config.show_size:
            size_str = f"[{format_size_classic(node.size, self.config.human_readable)}] "

        if is_root:
            write_line(file, size_str + icon + display_name)
        else:
            branch = '└── ' if is_last else '├── '
            if self.config.use_color:
                color = ANSI_COLOR_DIR if node.is_dir else ANSI_COLOR_FILE
                display_name = f"{color}{display_name}{ANSI_COLOR_RESET}"
            write_line(file, indent + branch + size_str + icon + display_name)

        # Truncated
        if node.is_truncated and self.config.show_ellipsis:
            ellipsis_indent = indent + ('    ' if is_last else '│   ')
            stats = node.stats
            if self.config.folders_only:
                text = f"... ({stats.hidden_dirs} dirs)"
            else:
                text = f"... ({stats.hidden_dirs} dirs, {stats.hidden_files} files)"
            write_line(file, f"{ellipsis_indent}└── {text}")
            return

        new_indent = indent if is_root else indent + ('    ' if is_last else '│   ')
        for i, child in enumerate(node.children):
            self._render_recursive(child, file, new_indent, i == len(node.children)-1, False)

class JsonRenderer(BaseRenderer):
    def render(self, node: TreeNode, output_file: TextIO) -> None:
        def to_dict(n: TreeNode):
            d = {
                "name": n.name,
                "path": n.path.replace("\\", "/"),
                "type": "directory" if n.is_dir else "file",
                "size_bytes": n.size,
            }
            if self.config.human_readable:
                d["size_human"] = format_size_classic(n.size, True).strip()

            if n.is_dir:
                d["content_summary"] = {
                    "folders": n.stats.total_dirs,
                    "files": n.stats.total_files
                }
                
                if n.is_truncated:
                    d["is_truncated"] = True
                    d["hidden_summary"] = {
                        "hidden_folders": n.stats.hidden_dirs,
                        "hidden_files": n.stats.hidden_files
                    }
                else:
                    d["is_truncated"] = False
                    d["children"] = [to_dict(c) for c in n.children]
            return d
        json.dump(to_dict(node), output_file, indent=4, ensure_ascii=False)

class MarkdownRenderer(BaseRenderer):
    def render(self, node: TreeNode, output_file: TextIO) -> None:
        self._render_recursive(node, output_file, 0)

    def _render_recursive(self, node: TreeNode, file: TextIO, depth: int = 0) -> None:
        indent = "  " * depth
        icon = self.icon_provider.get_icon(node.name, node.is_dir)

        size_str = ""
        if self.config.show_size:
            size_str = f"`{format_size_classic(node.size, self.config.human_readable).strip()}` "

        name_display = f"**{node.name}/**" if node.is_dir else f"`{node.name}`"
        write_line(file, f"{indent}- {icon}{size_str}{name_display}")

        # Truncated
        if node.is_truncated and self.config.show_ellipsis:
            indent = "  " * (depth + 1)
            stats = node.stats
            if self.config.folders_only:
                text = f"... ({stats.hidden_dirs} dirs)"
            else:
                text = f"... ({stats.hidden_dirs} dirs, {stats.hidden_files} files)"
            write_line(file, f"{indent}- {text}")
            return
        
        for child in node.children:
            self._render_recursive(child, file, depth + 1)

class MarkdownBlockRenderer(BaseRenderer):
    def render(self, node: TreeNode, output_file: TextIO) -> None:
        import copy
        tmp_config = copy.copy(self.config)
        tmp_config.use_color = False
        
        write_line(output_file, "```text")
        TextRenderer(tmp_config).render(node, output_file)
        write_line(output_file, "```")
