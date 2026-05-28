# ltree/core/models.py
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from ltree.core.metadata.models import MetadataContainer


class NodeType(Enum):
    FILE = "file"
    DIR = "directory"


@dataclass(slots=True)
class Stats:
    visible_dirs: int = 0
    visible_files: int = 0
    hidden_dirs: int = 0
    hidden_files: int = 0

    @property
    def total_dirs(self) -> int:
        return self.visible_dirs + self.hidden_dirs

    @property
    def total_files(self) -> int:
        return self.visible_files + self.hidden_files


@dataclass(slots=True)
class TreeNode:
    path: Path
    ntype: NodeType
    children: list["TreeNode"] = field(default_factory=list)
    metadata: MetadataContainer = field(default_factory=MetadataContainer)

    stats: Stats = field(default_factory=Stats)
    is_truncated: bool = False

    def __init__(
        self,
        path: Path | str,
        ntype: NodeType | None = None,
        children: list["TreeNode"] | None = None,
        metadata: MetadataContainer | None = None,
        stats: Stats | None = None,
        is_truncated: bool = False,
        size: int = 0,
        # todo: remove name, is_dir, is_symlink, is_executable, permissions, git_status from params
        name: str | None = None,
        is_dir: bool | None = None,
        is_symlink: bool | None = None,
        is_executable: bool | None = None,
        permissions: str | None = None,
        git_status: None = None,
    ):
        if isinstance(path, str):
            self.path = Path(path)
        else:
            self.path = path

        if ntype is not None:
            self.ntype = ntype
        elif is_dir is not None:
            self.ntype = NodeType.DIR if is_dir else NodeType.FILE
        else:
            self.ntype = NodeType.DIR if self.path.is_dir() else NodeType.FILE

        self.children = children if children is not None else []
        self.metadata = metadata if metadata is not None else MetadataContainer()
        self.stats = stats if stats is not None else Stats()
        self.is_truncated = is_truncated

        from ltree.core.metadata.models import FilesystemMetadata

        if self.metadata.fs is None:
            self.metadata.fs = FilesystemMetadata()
        if size > 0:
            self.metadata.fs.size = size
        # todo: remove the following conditions, which have already done in FilesystemMetadataProvider
        if is_symlink is not None:
            self.metadata.fs.is_symlink = is_symlink
        if is_executable is not None:
            self.metadata.fs.is_executable = is_executable
        if permissions is not None:
            self.metadata.fs.permissions = permissions

    @property
    def name(self) -> str:
        name_str = self.path.name
        if not name_str:
            return str(self.path)
        return name_str

    @property
    def is_dir(self) -> bool:
        return self.ntype == NodeType.DIR

    @property
    def is_symlink(self) -> bool:
        return self.metadata.fs.is_symlink if self.metadata.fs else False

    @is_symlink.setter
    def is_symlink(self, value: bool) -> None:
        self.metadata.fs.is_symlink = value

    @property
    def is_executable(self) -> bool:
        return self.metadata.fs.is_executable if self.metadata.fs else False

    @is_executable.setter
    def is_executable(self, value: bool) -> None:
        self.metadata.fs.is_executable = value

    @property
    def permissions(self) -> str:
        return self.metadata.fs.permissions if self.metadata.fs else ""

    @permissions.setter
    def permissions(self, value: str) -> None:
        self.metadata.fs.permissions = value

    @property
    def extension(self) -> str:
        return self.metadata.fs.extension if self.metadata.fs else ""

    @extension.setter
    def extension(self, value: str) -> None:
        self.metadata.fs.extension = value

    @property
    def size(self) -> int:
        return self.metadata.fs.size if self.metadata.fs else 0

    @size.setter
    def size(self, value: int) -> None:
        self.metadata.fs.size = value
