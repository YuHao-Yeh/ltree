# ltree/core/scanner.py
import os
import stat
import sys

from .config import TreeConfig
from .models import TreeNode, NodeType
from .utils import is_excluded, count_subtree
from .metadata import MetadataPipeline, get_default_pipeline


def build_metadata(path: str, node: TreeNode) -> None:
    try:
        st = os.lstat(path)

        node.is_symlink = stat.S_ISLNK(st.st_mode)
        node.is_executable = bool(st.st_mode & stat.S_IXUSR)
        node.permissions = stat.filemode(st.st_mode)

        _, ext = os.path.splitext(node.name)
        node.extension = ext.lower()
    except OSError:
        return


def scan_tree(
    path: str,
    config: TreeConfig,
    max_depth: int | None = None,
    curr_depth: int = 0,
    rel_path: str = ".",
    pipeline: MetadataPipeline | None = None,
) -> TreeNode | None:
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.", file=sys.stderr)
        return None

    if curr_depth == 0:
        config.root_path = os.path.abspath(path)
        config.load_gitignore(config.root_path)
        rel_path = "."
        pipeline = get_default_pipeline(config)

    is_dir = os.path.isdir(path)
    abs_path = os.path.abspath(path)
    name = os.path.basename(abs_path) if curr_depth == 0 else os.path.basename(path)
    if curr_depth == 0 and not name:
        name = abs_path

    node = TreeNode(path=path, ntype=NodeType.DIR if is_dir else NodeType.FILE)
    pipeline.execute(abs_path, node, config)

    if not is_dir:
        try:
            node.size = os.path.getsize(path)
        except OSError:
            node.size = 0
        return node

    try:
        with os.scandir(path) as it:
            entries = list(it)
            entries.sort(
                key=lambda e: (
                    not e.is_dir() if config.dirs_first else False,
                    e.name.lower(),
                )
            )

            for entry in entries:
                entry_rel_path = (
                    entry.name
                    if rel_path == "."
                    else os.path.join(rel_path, entry.name)
                )
                if is_excluded(entry.name, entry.is_dir(), config, entry_rel_path):
                    continue

                # visible file
                if not entry.is_dir():
                    f_size = entry.stat().st_size
                    node.size += f_size

                    if config.folders_only:
                        node.stats.hidden_files += 1
                        continue

                    node.stats.visible_files += 1
                    child = TreeNode(
                        name=entry.name, is_dir=False, path=entry.path, size=f_size
                    )
                    pipeline.execute(entry.path, child, config)
                    node.children.append(child)
                    continue

                # visible folder
                node.stats.visible_dirs += 1

                if max_depth is not None and curr_depth >= max_depth:
                    # hidden folders & files
                    h_dirs, h_files, h_size = count_subtree(entry.path, config)

                    child = TreeNode(
                        name=entry.name, is_dir=True, path=entry.path, is_truncated=True
                    )
                    pipeline.execute(entry.path, child, config)
                    child.stats.hidden_dirs = h_dirs
                    child.stats.hidden_files = h_files
                    child.size = h_size
                    node.children.append(child)

                    node.size += h_size
                    node.stats.hidden_dirs += h_dirs
                    node.stats.hidden_files += h_files
                else:
                    child = scan_tree(
                        entry.path,
                        config,
                        max_depth,
                        curr_depth + 1,
                        entry_rel_path,
                        pipeline,
                    )
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
    except OSError as e:
        print(f"Error: Failed to scan '{path}': {e}", file=sys.stderr)
        return

    return node
