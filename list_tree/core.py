import sys
import os

from .config import TreeConfig
from .schema import TreeNode
from .utils import is_excluded, count_subtree


def scan_tree(
    path: str,
    config: TreeConfig,
    max_depth: int = None,
    curr_depth: int = 0
) -> TreeNode:
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.", file=sys.stderr)
        return None
    
    is_dir = os.path.isdir(path)
    name = os.path.basename(os.path.abspath(path)) if curr_depth == 0 else os.path.basename(path)
    node = TreeNode(name=name, is_dir=is_dir, path=path)

    if not is_dir:
        try:
            node.size = os.path.getsize(path)
        except OSError:
            node.size = 0
        return node

    try:
        with os.scandir(path) as it:
            entries = list(it)
            entries.sort(key=lambda e: (not e.is_dir() if config.dirs_first else False, e.name.lower()))

            for entry in entries:
                if is_excluded(entry.name, entry.is_dir(), config):
                    continue

                # visible file
                if not entry.is_dir():
                    f_size = entry.stat().st_size
                    node.size += f_size

                    if config.folders_only:
                        node.stats.hidden_files += 1
                        continue

                    node.stats.visible_files += 1
                    node.children.append(TreeNode(name=entry.name, is_dir=False, path=entry.path, size=f_size))
                    continue

                # visible folder
                node.stats.visible_dirs += 1

                if max_depth is not None and curr_depth >= max_depth:
                    # hidden folders & files
                    h_dirs, h_files, h_size = count_subtree(entry.path, config)

                    child = TreeNode(name=entry.name, is_dir=True, path=entry.path, is_truncated=True)
                    child.stats.hidden_dirs = h_dirs
                    child.stats.hidden_files = h_files
                    child.size = h_size
                    node.children.append(child)
                    
                    node.size += h_size
                    node.stats.hidden_dirs += h_dirs
                    node.stats.hidden_files += h_files
                else:
                    child = scan_tree(entry.path, config, max_depth, curr_depth + 1)
                    if child:
                        node.children.append(child)

                        node.stats.visible_dirs += child.stats.visible_dirs
                        node.stats.visible_files += child.stats.visible_files
                        node.stats.hidden_dirs += child.stats.hidden_dirs
                        node.stats.hidden_files += child.stats.hidden_files

                        node.size += child.size
    except PermissionError:
        print(f"Error: No permission for the path '{path}'", file=sys.stderr)
        return

    return node
