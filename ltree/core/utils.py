import os
import fnmatch
from io import TextIOWrapper
from typing import TextIO

from .config import TreeConfig


def is_excluded(item: str, is_dir: bool, config: TreeConfig, rel_path: str) -> bool:
    normalized_rel_path = rel_path.replace('\\', '/')

    # Priority 1
    if item in config.added_items:
        return False
    
    # Priority 2 - gitignore
    if config.gitignore_spec:
        path_for_git = normalized_rel_path + '/' if is_dir else normalized_rel_path
        if config.gitignore_spec.match_file(path_for_git):
            return True
    
    # Priority 3 - regex
    if config.regex_exclude_patterns:
        for regex in config.regex_exclude_patterns:
            if regex.search(normalized_rel_path):
                return True

    # Priority 4
    if is_dir:
        if item in config.exclude_dirs:
            return True
    else:
        if item in config.exclude_files:
            return True
        if any(item.endswith(ext) for ext in config.exclude_exts):
            return True    

    if any(item.startswith(p) for p in config.exclude_prefixes):
        return True
    
    if not is_dir:
        if any(fnmatch.fnmatch(item, pattern) for pattern in config._pattern_files):
            return True

    # Prioirty 5 - hidden files
    if not config.show_all:
        if item.startswith(".") and item not in [".", "./"]:
            return True

    return False

def count_subtree(path: str, config: TreeConfig) -> tuple[int, int, int]:
    if path in config._subtree_cache:
        return config._subtree_cache[path]
    
    total_dirs = 0
    total_files = 0
    total_size = 0

    base_path = config.root_path

    for root, dirs, files in os.walk(path):
        rel_root = get_rel_path(root, base_path)
        # --- directories ---
        keep_dirs = []
        for d in dirs:
            rel_dir_path = d if rel_root == "." else f"{rel_root}/{d}"

            if not is_excluded(d, True, config, rel_dir_path):
                total_dirs += 1
                keep_dirs.append(d)
        dirs[:] = keep_dirs

        # --- files ---
        for f in files:
            rel_file_path = f if rel_root == "." else f"{rel_root}/{f}"

            if not is_excluded(f, False, config, rel_file_path):
                total_files += 1
                try:
                    f_path = os.path.join(root, f)
                    total_size += os.path.getsize(f_path)
                except OSError:
                    pass

    res = (total_dirs, total_files, total_size)
    config._subtree_cache[path] = res

    return res

def get_rel_path(target_path: str, base_path: str):
    abs_target = os.path.abspath(target_path)
    abs_base = os.path.abspath(base_path)
    
    if abs_target == abs_base:
        return "."
    
    rel = os.path.relpath(abs_target, abs_base)

    return rel.replace("\\", "/")

def write_line(file: TextIO | TextIOWrapper | None = None, text: str = "") -> None:
    if file is None:
        return
    file.write(text + '\n')
