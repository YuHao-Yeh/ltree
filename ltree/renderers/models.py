# ltree/renderers/models.py
from dataclasses import dataclass, field

from ltree.core.metadata.models import GitStatus


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
