# ltree/core/metadata/filesystem.py
import os
import stat
from typing import TYPE_CHECKING

from ltree.core.metadata.base import MetadataProvider
from ltree.core.metadata.models import FilesystemMetadata

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode


class FilesystemMetadataProvider(MetadataProvider):
    def enrich(self, node: "TreeNode", config: "TreeConfig") -> None:
        try:
            st = node.path.lstat()

            _, ext = os.path.splitext(node.name)

            node.metadata.fs = FilesystemMetadata(
                permissions=stat.filemode(st.st_mode),
                is_executable=bool(st.st_mode & stat.S_IXUSR),
                is_symlink=stat.S_ISLNK(st.st_mode),
                extension=ext.lower(),
                size=st.st_size if not node.is_dir else 0,
            )
        except OSError:
            node.metadata.fs = FilesystemMetadata(
                permissions="",
                is_executable=False,
                is_symlink=False,
                extension="",
                size=0,
            )
