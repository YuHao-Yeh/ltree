import os
import stat

from ..models import TreeNode


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
