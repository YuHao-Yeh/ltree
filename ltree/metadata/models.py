# ltree/metadata/models.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(slots=True)
class MetadataContainer:
    fs: FilesystemMetadata | None = None
    git: GitMetadata | None = None
    # media: MediaMetadata | None = None
    code: CodeMetadata | None = None
    project: ProjectMetadata | None = None
    time: TimeMetadata | None = None


# ----------------------------------------------------------------------
class GitStatus(Enum):
    CLEAN = "clean"
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    UNTRACKED = "untracked"
    IGNORED = "ignored"
    UNMERGED = "unmerged"
    COPIED = "copied"
    TYPE_CHANGED = "type_changed"
    DIRTY = "dirty"


# ----------------------------------------------------------------------
@dataclass(slots=True)
class FilesystemMetadata:
    permissions: str = ""
    is_executable: bool = False
    is_symlink: bool = False
    extension: str = ""
    size: int = 0


@dataclass(slots=True)
class GitMetadata:
    tracked: bool = False
    status: GitStatus | None = None
    is_repo_root: bool = False
    has_sub_changes: bool = False


@dataclass(slots=True)
class CodeMetadata:
    language: str | None = None
    is_source_code: bool = False


@dataclass(slots=True)
class ProjectMetadata:
    project_type: str = ""
    name: str = ""
    version: str = ""


@dataclass(slots=True)
class TimeMetadata:
    modified_timestamp: float = 0.0
    modified_iso: str = ""
    relative_modified: str = ""
