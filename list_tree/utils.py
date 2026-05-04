import os
import fnmatch

from .config import TreeConfig


def is_excluded(item: str, is_dir: bool, config: TreeConfig):
    if any(item.startswith(p) for p in config.exclude_prefixes):
        return True
    
    if is_dir:
        return item in config.exclude_dirs
    else:
        if item in config._exact_files:
            return True
        if any(fnmatch.fnmatch(item, pattern) for pattern in config._pattern_files):
            return True
        if any(item.endswith(ext) for ext in config.exclude_exts):
            return True

    return False

def count_subtree(path: str, config: TreeConfig):
    if path in config._subtree_cache:
        return config._subtree_cache[path]
    
    total_dirs = 0
    total_files = 0

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not is_excluded(d, True, config)]
        files = [f for f in files if not is_excluded(f, False, config)]

        total_dirs += len(dirs)
        total_files += len(files)

    config._subtree_cache[path] = (total_dirs, total_files)

    return total_dirs, total_files

def write_line(file, text):
    if file is None:
        return
    file.write(text + '\n')
