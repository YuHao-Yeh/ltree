# ltree/core/models.py
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from ltree.core.metadata.models import MetadataContainer, FilesystemMetadata


class NodeType(Enum):
    FILE = "file"
    DIR = "directory"


@dataclass(slots=True)
class Stats:
    visible_dirs: int = 0
    visible_files: int = 0
    hidden_dirs: int = 0
    hidden_files: int = 0
    hidden_size: int = 0

    @property
    def total_dirs(self) -> int:
        return self.visible_dirs + self.hidden_dirs

    @property
    def total_files(self) -> int:
        return self.visible_files + self.hidden_files


@dataclass(slots=True)
class TreeNode:
    path: Path
    ntype: NodeType | None = None
    children: list["TreeNode"] = field(default_factory=list)
    metadata: MetadataContainer = field(
        default_factory=lambda: MetadataContainer(fs=FilesystemMetadata())
    )

    stats: Stats = field(default_factory=Stats)
    is_truncated: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.path, str):
            self.path = Path(self.path)

        if self.ntype is None:
            self.ntype = NodeType.DIR if self.path.is_dir() else NodeType.FILE

    @property
    def name(self) -> str:
        return self.path.name or str(self.path)

    @property
    def is_dir(self) -> bool:
        return self.ntype == NodeType.DIR

    @property
    def is_symlink(self) -> bool:
        return self.metadata.fs.is_symlink

    @is_symlink.setter
    def is_symlink(self, value: bool) -> None:
        self.metadata.fs.is_symlink = value

    @property
    def is_executable(self) -> bool:
        return self.metadata.fs.is_executable

    @is_executable.setter
    def is_executable(self, value: bool) -> None:
        self.metadata.fs.is_executable = value

    @property
    def permissions(self) -> str:
        return self.metadata.fs.permissions

    @permissions.setter
    def permissions(self, value: str) -> None:
        self.metadata.fs.permissions = value

    @property
    def extension(self) -> str:
        return self.metadata.fs.extension

    @extension.setter
    def extension(self, value: str) -> None:
        self.metadata.fs.extension = value

    @property
    def size(self) -> int:
        return self.metadata.fs.size

    @size.setter
    def size(self, value: int) -> None:
        self.metadata.fs.size = value
