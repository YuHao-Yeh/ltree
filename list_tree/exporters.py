import json

from .schema import TreeNode
from .config import TreeConfig
from .constants import COLOR_DIR, COLOR_FILE, COLOR_RESET
from .utils import write_line


def render_text(
    node: TreeNode, 
    file,
    config: TreeConfig,
    indent: str = "",
    is_last: bool = True,
    is_root: bool = True
):
    use_color = config.use_color
    display_name = node.name + ("/" if node.is_dir else "")
    
    if is_root:
        write_line(file, display_name)
    else:
        branch = '└── ' if is_last else '├── '
        if use_color:
            color = COLOR_DIR if node.is_dir else COLOR_FILE
            display_name = f"{color}{display_name}{COLOR_RESET}"
        write_line(file, indent + branch + display_name)

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

def render_json(node: TreeNode, file):
    def to_dict(n: TreeNode):
        d = {
            "name": n.name,
            "type": "directory" if n.is_dir else "file",
        }
        if n.is_dir:
            d.update({
                "content": {
                    "folders": n.stats.total_dirs,
                    "files": n.stats.total_files
                },
                "children": [to_dict(c) for c in n.children]
            })
        return d
    json.dump(to_dict(node), file, indent=4)

def render_markdown(node, file, depth=0):
    indent = "  " * depth
    icon = "📂" if node.is_dir else "📄"
    name_display = f"`{node.name}/`" if node.is_dir else f"`{node.name}`"
    write_line(file, f"{indent}- {icon} {name_display}")
    for child in node.children:
        render_markdown(child, file, depth + 1)

def render_markdown_as_block(node, file, config: TreeConfig):
    write_line(file, "```text")     # or use ```bash
    config.use_color = False
    render_text(node, file, config)
    write_line(file, "```")

def print_stats(node: TreeNode):
    s = node.stats
    print(f"\nSummary:")
    print(f"Visible: {s.visible_dirs:>3} dir(s), {s.visible_files:>3} file(s)")
    print(f"Total  : {s.total_dirs:>3} dir(s), {s.total_files:>3} file(s)")