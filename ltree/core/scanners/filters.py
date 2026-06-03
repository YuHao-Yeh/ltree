# ltree/core/scanners/filters.py
import fnmatch
from pathlib import Path
from typing import Protocol

from ltree.core.config import TreeConfig
from ltree.core.utils import get_rel_path


class NodeFilter(Protocol):
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool: ...


class ForceIncludeFilter:
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        return False


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
        if is_dir:
            if name in config.exclude_dirs:
                return True
        else:
            if name in config.exclude_files:
                return True
            if any(name.endswith(ext) for ext in config.exclude_exts):
                return True

        if any(name.startswith(p) for p in config.exclude_prefixes):
            return True

        if not is_dir:
            if any(fnmatch.fnmatch(name, pattern) for pattern in config._pattern_files):
                return True
        return False


class HiddenFilter:
    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        if config.show_all:
            return False

        return path.name.startswith(".")


class CompositeFilter:
    def __init__(self, filters: list[NodeFilter] | None = None):
        self.filters: list[NodeFilter] = filters or [
            GitignoreFilter(),
            RegexFilter(),
            DefaultExcludeFilter(),
            HiddenFilter(),
        ]

    def should_exclude(self, path: Path, is_dir: bool, config: TreeConfig) -> bool:
        if path.name in config.added_items:
            return False

        return any(f.should_exclude(path, is_dir, config) for f in self.filters)
