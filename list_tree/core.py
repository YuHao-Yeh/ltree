import sys
import os
from io import TextIOWrapper
from typing import TextIO

from .constants import COLOR_DIR, COLOR_FILE, COLOR_RESET
from .config import TreeConfig
from .schema import Stats, TreeNode
from .utils import is_excluded, count_subtree, write_line


def list_dir(
        start_path: str = '.',
        indent: str = '',
        file: TextIO | TextIOWrapper | None = None,
        is_console: bool = False,
        stats: Stats | None = None, 
        use_color: bool = True,
        folders_only: bool = False,
        dirs_first: bool = False, 
        show_ellipsis: bool = False,
        curr_depth: int = 0,
        max_depth: int | None = None,
        config: TreeConfig | None = None,
        is_root: bool = False
    ):
    try:        
        items = os.listdir(start_path)
        items_with_type = [(item, os.path.isdir(os.path.join(start_path, item))) for item in items]

        if dirs_first:
            items_with_type.sort(key=lambda x: (not x[1], x[0].lower()))
        else:
            items_with_type.sort(key=lambda x: x[0].lower())
    except FileNotFoundError:
        print(f"Error: Path '{start_path}' does not exist.", file=sys.stderr)
        return
    except PermissionError:
        return
    
    if is_root:
        root_name = os.path.basename(os.path.abspath(start_path))
        write_line(file, root_name + "/")

    visible_items = []

    if config is None:
        config = TreeConfig()

    for item, is_dir in items_with_type:
        path = os.path.join(start_path, item)

        if is_excluded(item, is_dir, config):
            continue

        if folders_only and not is_dir:
            continue

        visible_items.append((item, is_dir))

    use_color = is_console and use_color
    for index, (item, is_dir) in enumerate(visible_items):
        path = os.path.join(start_path, item)
        is_last = index == len(visible_items) - 1
        branch = '└── ' if is_last else '├── '
        prefix = indent + branch

        if is_dir:
            if stats is not None:
                stats.visible_dirs += 1

            if use_color:   # console mode
                display = f"{COLOR_DIR}{item}/{COLOR_RESET}"
            else:
                display = f"{item}/"

            write_line(file, prefix + display)

            if max_depth is not None and curr_depth >= max_depth:
                if show_ellipsis:
                    ellipsis_prefix = indent + ('    ' if is_last else '│   ') + '└── '
                    if path not in config.subtree_cache:
                        sub_dirs, sub_files = count_subtree(path, config)
                    else:
                        sub_dirs, sub_files = config.subtree_cache[path]
                    
                    if stats is not None:
                        stats.hidden_dirs += sub_dirs
                        stats.hidden_files += sub_files

                    text = ellipsis_prefix
                    text += f"... ({sub_dirs} dirs)" if folders_only else f"... ({sub_dirs} dirs, {sub_files} files)"
                    write_line(file, text)
                continue
              
            list_dir(
                start_path=path, 
                indent=indent + ('    ' if is_last else '│   '), 
                file=file, 
                is_console=is_console, 
                stats=stats, 
                use_color=use_color, 
                folders_only=folders_only,
                dirs_first=dirs_first, 
                show_ellipsis=show_ellipsis,
                curr_depth=curr_depth + 1,
                max_depth=max_depth,
                config=config,
                is_root=False,
            )
        else:
            if stats is not None:
                stats.visible_files += 1
            if use_color:   # console mode
                display = f"{COLOR_FILE}{item}{COLOR_RESET}"
            else:
                display = item
            write_line(file, prefix + display)

def scan_tree(
    path: str,
    config: TreeConfig,
    max_depth: int = None,
    curr_depth: int = 0,
    folders_only: bool = False
) -> TreeNode:
    is_dir = os.path.isdir(path)
    name = os.path.basename(os.path.abspath(path)) if curr_depth == 0 else os.path.basename(path)
    node = TreeNode(name=name, is_dir=is_dir, path=path)

    if not is_dir:
        return node

    try:
        with os.scandir(path) as it:
            entries = list(it)
            entries.sort(key=lambda e: (not e.is_dir() if config.dirs_first else False, e.name.lower()))

            for entry in entries:
                if is_excluded(entry.name, entry.is_dir(), config):
                    continue

                if folders_only and not entry.is_dir():
                    continue

                # visible file
                if not entry.is_dir():
                    node.stats.visible_files += 1
                    node.children.append(TreeNode(name=entry.name, is_dir=False, path=entry.path))
                    continue

                # visible folder
                node.stats.visible_dirs += 1

                if max_depth is not None and curr_depth >= max_depth:
                    # hidden folders & files
                    h_dirs, h_files = count_subtree(entry.path, config)

                    child = TreeNode(name=entry.name, is_dir=True, path=entry.path, is_truncated=True)
                    child.stats.hidden_dirs = h_dirs
                    child.stats.hidden_files = h_files
                    node.children.append(child)
                    
                    node.stats.hidden_dirs += h_dirs
                    node.stats.hidden_files += h_files
                else:
                    child = scan_tree(entry.path, config, max_depth, curr_depth + 1, folders_only)
                    node.children.append(child)
                    
                    node.stats.visible_dirs += child.stats.visible_dirs
                    node.stats.visible_files += child.stats.visible_files
                    node.stats.hidden_dirs += child.stats.hidden_dirs
                    node.stats.hidden_files += child.stats.hidden_files
    except FileNotFoundError:
        print(f"Error: Path '{path}' does not exist.", file=sys.stderr)
        return
    except PermissionError:
        return

    return node
