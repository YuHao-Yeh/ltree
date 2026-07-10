# ltree/core/scanners/filters.py
from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from ltree.core.utils import get_rel_path

if TYPE_CHECKING:
    from pathlib import Path
    from ltree.core.config import TreeConfig


class NodeFilter(Protocol):
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool: ...


# ----------------------------------------------------------------------
class ForceIncludeFilter:
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        return False


# ----------------------------------------------------------------------
class GitignoreFilter:
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        if not config.gitignore_spec:
            return False

        rel_path = get_rel_path(str(path), config.root_path)
        normalized_rel_path = rel_path.replace("\\", "/")

        path_for_git = f"{normalized_rel_path}/" if is_dir else normalized_rel_path

        return config.gitignore_spec.match_file(path_for_git)


class RegexFilter:
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        if not config.regex_exclude_patterns:
            return False

        rel_path = get_rel_path(str(path), config.root_path)
        normalized_rel_path = rel_path.replace("\\", "/")

        return any(
            regex.search(normalized_rel_path) for regex in config.regex_exclude_patterns
        )


class DefaultExcludeFilter:
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        name = path.name
        rel_path = get_rel_path(str(path), config.root_path)
        if config.exclude.matches(rel_path, name):
            return True

        return False


class HiddenFilter:
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        if config.show_all:
            return False

        return path.name.startswith(".")


# ----------------------------------------------------------------------
class CompositeFilter:
    def __init__(self, filters: list[NodeFilter] | None = None):
        self.filters: list[NodeFilter] = filters or [
            GitignoreFilter(),
            RegexFilter(),
            DefaultExcludeFilter(),
            HiddenFilter(),
        ]

    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        rel_path = get_rel_path(str(path), config.root_path)
        name = path.name
        if config.include.matches(rel_path, name):
            return False

        return any(f.should_exclude(path, is_dir, config) for f in self.filters)
