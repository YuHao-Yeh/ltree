import os
import fnmatch

from .config import TreeConfig


def is_excluded(item: str, is_dir: bool, config: TreeConfig):
    # Priority 1
    if item in config.added_items:
        return False

    # Priority 2
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

    # Prioirty 3:
    if not config.show_all:
        if item.startswith(".") and item not in [".", "./"]:
            return True
        # if is_dir and item in config.exclude_dirs:
        #     return True
        # if not is_dir and item in config._exact_files:
        #     return True
        # if any(fnmatch.fnmatch(item, pattern) for pattern in config._pattern_files):
        #     return True

    return False

def count_subtree(path: str, config: TreeConfig):
    if path in config.subtree_cache:
        return config.subtree_cache[path]
    
    total_dirs = 0
    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not is_excluded(d, True, config)]

        for f in files:
            if not is_excluded(f, False, config):
                total_files += 1
                try:
                    f_path = os.path.join(root, f)
                    total_size += os.path.getsize(f_path)
                except OSError:
                    pass

        total_dirs += len(dirs)

    res = (total_dirs, total_files, total_size)
    config._subtree_cache[path] = res

    return res

def write_line(file, text):
    if file is None:
        return
    file.write(text + '\n')
