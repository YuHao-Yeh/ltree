import json
from io import TextIOWrapper
from typing import TextIO

from .schema import TreeNode
from .config import TreeConfig
from .constants import COLOR_DIR, COLOR_FILE, COLOR_RESET
from .utils import write_line


def format_size(size_bytes: float, human: bool = False):
    if not human:
        return f"{size_bytes:>8} B"
    
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if size_bytes < 1024:
            return f"{size_bytes:>5.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:>5.1f} P"

def render_text(
    node: TreeNode,
    file: TextIO | TextIOWrapper,
    config: TreeConfig,
    indent: str = "",
    is_last: bool = True,
    is_root: bool = True
):
    path_display = node.path.replace('\\', '/')
    name = path_display if config.full_path and not is_root else node.name
    display_name = name + ("/" if node.is_dir and not name.endswith("/") else "")
    
    size_str = ""
    if config.show_size:
        size_str = f"[{format_size(node.size, config.human_readable)}] "

    if is_root:
        write_line(file, size_str + display_name)
    else:
        branch = '└── ' if is_last else '├── '
        if config.use_color:
            color = COLOR_DIR if node.is_dir else COLOR_FILE
            display_name = f"{color}{display_name}{COLOR_RESET}"
        write_line(file, indent + branch + size_str + display_name)

    # Truncated
    if node.is_truncated and config.show_ellipsis:
        ellipsis_indent = indent + ('    ' if is_last else '│   ')
        stats = node.stats
        if config.folders_only:
            text = f"... ({stats.hidden_dirs} dirs)"
        else:
            text = f"... ({stats.hidden_dirs} dirs, {stats.hidden_files} files)"
        write_line(file, f"{ellipsis_indent}└── {text}")
        return

    new_indent = indent if is_root else indent + ('    ' if is_last else '│   ')
    for i, child in enumerate(node.children):
        render_text(child, file, config, new_indent, i == len(node.children)-1, False)

def render_json(node: TreeNode, file, config: TreeConfig):
    def to_dict(n: TreeNode):
        d = {
            "name": n.name,
            "type": "directory" if n.is_dir else "file",
            "size_bytes": n.size,
        }
        if config.human_readable:
            d["size_human"] = format_size(n.size, True).strip()

        if n.is_dir:
            d.update({
                "content_summary": {
                    "folders": n.stats.total_dirs,
                    "files": n.stats.total_files
                },
                "children": [to_dict(c) for c in n.children]
            })
        return d
    json.dump(to_dict(node), file, indent=4)

def render_markdown(node, file, config: TreeConfig, depth=0):
    indent = "  " * depth
    icon = "📂" if node.is_dir else "📄"

    size_str = ""
    if config.show_size:
        size_str = f"`{format_size(node.size, config.human_readable).strip()}` "

    name_display = f"**{node.name}/**" if node.is_dir else f"`{node.name}`"
    write_line(file, f"{indent}- {icon} {size_str}{name_display}")

    for child in node.children:
        render_markdown(child, file, config, depth + 1)

def render_markdown_as_block(node, file, config: TreeConfig):
    write_line(file, "```text")                 # or use ```bash
    import copy
    tmp_config = copy.copy(config)
    tmp_config.use_color = False
    render_text(node, file, tmp_config)
    write_line(file, "```")

def print_stats(node: TreeNode, config: TreeConfig):
    s = node.stats
    size_str = ""
    if config.show_size:
        size_str = f" ({format_size(node.size, config.human_readable).strip()})"

    print(f"\nSummary{size_str}:")
    print(f"Visible: {s.visible_dirs:>3} directories, {s.visible_files:>3} files")
    print(f"Total  : {s.total_dirs:>3} directories, {s.total_files:>3} files")
