import json
from io import TextIOWrapper
import os
from typing import TextIO
# from rich.filesize import decimal as format_size # Rich 內建的檔案大小格式化

from .base import BaseRenderer
from ..core.models import TreeNode
from ..core.config import TreeConfig
from ..constants import ANSI_COLOR_DIR, ANSI_COLOR_FILE, ANSI_COLOR_RESET
from ..core.utils import write_line


def format_size(size_bytes: float, human: bool = False) -> str:
    if not human:
        return f"{size_bytes:>8} B"
    
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if size_bytes < 1024:
            return f"{size_bytes:>5.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:>5.1f} P"

# def render_text(
#     node: TreeNode,
#     file: TextIO | TextIOWrapper,
#     config: TreeConfig,
#     indent: str = "",
#     is_last: bool = True,
#     is_root: bool = True
# ) -> None:
#     path_display = node.path.replace('\\', '/')
#     name = path_display if config.full_path and not is_root else node.name
#     display_name = name + ("/" if node.is_dir and not name.endswith("/") else "")
    
#     size_str = ""
#     if config.show_size:
#         size_str = f"[{format_size(node.size, config.human_readable)}] "

#     if is_root:
#         write_line(file, size_str + display_name)
#     else:
#         branch = '└── ' if is_last else '├── '
#         if config.use_color:
#             color = ANSI_COLOR_DIR if node.is_dir else ANSI_COLOR_FILE
#             display_name = f"{color}{display_name}{ANSI_COLOR_RESET}"
#         write_line(file, indent + branch + size_str + display_name)

#     # Truncated
#     if node.is_truncated and config.show_ellipsis:
#         ellipsis_indent = indent + ('    ' if is_last else '│   ')
#         stats = node.stats
#         if config.folders_only:
#             text = f"... ({stats.hidden_dirs} dirs)"
#         else:
#             text = f"... ({stats.hidden_dirs} dirs, {stats.hidden_files} files)"
#         write_line(file, f"{ellipsis_indent}└── {text}")
#         return

#     new_indent = indent if is_root else indent + ('    ' if is_last else '│   ')
#     for i, child in enumerate(node.children):
#         render_text(child, file, config, new_indent, i == len(node.children)-1, False)

# def render_json(node: TreeNode, file, config: TreeConfig) -> None:
#     def to_dict(n: TreeNode):
#         d = {
#             "name": n.name,
#             "type": "directory" if n.is_dir else "file",
#             "size_bytes": n.size,
#         }
#         if config.human_readable:
#             d["size_human"] = format_size(n.size, True).strip()

#         if n.is_dir:
#             d.update({
#                 "content_summary": {
#                     "folders": n.stats.total_dirs,
#                     "files": n.stats.total_files
#                 },
#                 "children": [to_dict(c) for c in n.children]
#             })
#         return d
#     json.dump(to_dict(node), file, indent=4)

# def render_markdown(node: TreeNode, file, config: TreeConfig, depth: int = 0) -> None:
#     indent = "  " * depth
#     icon = "📂" if node.is_dir else "📄"

#     size_str = ""
#     if config.show_size:
#         size_str = f"`{format_size(node.size, config.human_readable).strip()}` "

#     name_display = f"**{node.name}/**" if node.is_dir else f"`{node.name}`"
#     write_line(file, f"{indent}- {icon} {size_str}{name_display}")

#     for child in node.children:
#         render_markdown(child, file, config, depth + 1)

# def render_markdown_as_block(node: TreeNode, file, config: TreeConfig) -> None:
#     write_line(file, "```text")                 # or use ```bash
#     import copy
#     tmp_config = copy.copy(config)
#     tmp_config.use_color = False
#     render_text(node, file, tmp_config)
#     write_line(file, "```")

def print_stats(node: TreeNode, config: TreeConfig) -> None:
    s = node.stats
    size_str = ""
    if config.show_size:
        size_str = f" ({format_size(node.size, config.human_readable).strip()})"
        # size_str = f" ({format_size(node.size).strip()})"

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
        
        size_str = ""
        if self.config.show_size:
            size_str = f"[{format_size(node.size, self.config.human_readable)}] "
            # size_str = f"[{format_size(node.size)}] "

        if is_root:
            write_line(file, size_str + display_name)
        else:
            branch = '└── ' if is_last else '├── '
            if self.config.use_color:
                color = ANSI_COLOR_DIR if node.is_dir else ANSI_COLOR_FILE
                display_name = f"{color}{display_name}{ANSI_COLOR_RESET}"
            write_line(file, indent + branch + size_str + display_name)

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
                d["size_human"] = format_size(n.size, True).strip()

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
        icon = "📂" if node.is_dir else "📄"

        size_str = ""
        if self.config.show_size:
            size_str = f"`{format_size(node.size, self.config.human_readable).strip()}` "

        name_display = f"**{node.name}/**" if node.is_dir else f"`{node.name}`"
        write_line(file, f"{indent}- {icon} {size_str}{name_display}")

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
