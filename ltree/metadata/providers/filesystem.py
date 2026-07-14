# ltree/metadata/provider/filesystem.py
from __future__ import annotations

import os
import stat as stat_module
from typing import TYPE_CHECKING

from ltree.metadata.base import MetadataProvider
from ltree.metadata.models import FilesystemMetadata

if TYPE_CHECKING:
    from os import stat_result
    from ltree.tree.models import TreeNode


class FilesystemMetadataProvider(MetadataProvider):
    def enrich(self, node: TreeNode, /, *, stat: stat_result | None = None) -> None:
        try:
            st = stat or node.path.lstat()

            _, ext = os.path.splitext(node.name)

            node.metadata.fs = FilesystemMetadata(
                permissions=stat_module.filemode(st.st_mode),
                is_executable=bool(st.st_mode & stat_module.S_IXUSR),
                is_symlink=stat_module.S_ISLNK(st.st_mode),
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
