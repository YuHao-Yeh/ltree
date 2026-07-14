# ltree/rendering/models.py
from dataclasses import dataclass, field

from ltree.metadata.models import GitStatus


@dataclass(slots=True)
class MetadataToken:
    text: str
    kind: str  # Token type（ex."perm", "git", "size", "time"）
    status: GitStatus | None = None


@dataclass(slots=True)
class RenderDetail:
    kind: str
    text: str


@dataclass(slots=True)
class RenderRow:
    name: str
    icon: str
    is_dir: bool

    permission: MetadataToken
    git: MetadataToken
    size: MetadataToken
    time: MetadataToken

    details: list[RenderDetail] = field(default_factory=list)


_BASE_MAP = {
    GitStatus.MODIFIED: "M",
    GitStatus.ADDED: "A",
    GitStatus.DELETED: "D",
    GitStatus.RENAMED: "R",
    GitStatus.UNTRACKED: "?",
    GitStatus.IGNORED: "I",
    GitStatus.UNMERGED: "U",
    GitStatus.TYPE_CHANGED: "T",
    GitStatus.COPIED: "C",
    GitStatus.DIRTY: "*",
    GitStatus.CLEAN: " ",
}

GIT_SYMBOL_MAP: dict[GitStatus | str, str] = {}
for status, symbol in _BASE_MAP.items():
    GIT_SYMBOL_MAP[status] = symbol
    GIT_SYMBOL_MAP[status.value] = symbol
