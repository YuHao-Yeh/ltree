# ltree/metadata/provider/git.py
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.metadata.base import MetadataProvider
from ltree.metadata.models import GitMetadata, GitStatus

if TYPE_CHECKING:
    from os import stat_result
    from ltree.tree.models import TreeNode


_ROOT_SENTINEL = Path(".")


class GitMetadataProvider(MetadataProvider):
    def __init__(self):
        self._repo_root: Path | None = None
        self._git_available: bool | None = None
        self._status_cache: dict[str, GitStatus] = {}  # rel_path -> status
        self._tracked_paths: set[str] = set()  # tracked paths
        self._dirty_dirs: set[str] = set()

    def _check_git_and_find_root(self, path: Path) -> None:
        if self._git_available is False:
            return

        try:
            target_dir = path if path.is_dir() else path.parent
            # cmd: git rev-parse --show-toplevel
            res = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(target_dir),
                capture_output=True,
                text=True,
                check=True,
            )
            self._repo_root = Path(res.stdout.strip()).resolve()
            self._git_available = True
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            self._git_available = False

    def _load_git_status_cache(self) -> None:
        if not self._repo_root:
            return

        try:
            # 1. Load tracked files
            # cmd: git ls-files
            res_tracked = subprocess.run(
                ["git", "ls-files"],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                check=True,
            )
            for line in res_tracked.stdout.splitlines():
                path_str = line.strip().strip('"').replace("\\", "/")
                if path_str:
                    self._tracked_paths.add(path_str)

            # 2. Load git status
            # cmd: git status --porcelain=v1 --ignored -uall
            res = subprocess.run(
                ["git", "status", "--porcelain=v1", "--ignored", "-uall"],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                check=True,
            )

            for line in res.stdout.splitlines():
                if len(line) < 4:
                    continue

                code = line[:2]
                raw_path_part = line[3:]

                # rename handling:
                # R "old.py" -> "new.py"
                if "->" in raw_path_part:
                    _, new_path_raw = raw_path_part.split("->", 1)
                    rel_path = new_path_raw.strip().strip('"')
                else:
                    rel_path = raw_path_part.strip().strip('"')

                rel_path = rel_path.replace("\\", "/")

                status = self._parse_status(code)
                self._status_cache[rel_path] = status

                if status != GitStatus.IGNORED:
                    self._tracked_paths.add(rel_path)
        except subprocess.SubprocessError:
            return
        else:
            self._build_dirty_dir_cache()

    def _build_dirty_dir_cache(self) -> None:
        self._dirty_dirs.clear()

        for rel_path, status in self._status_cache.items():
            if status == GitStatus.IGNORED:
                continue

            parent = Path(rel_path).parent

            while True:
                self._dirty_dirs.add(
                    "" if parent == _ROOT_SENTINEL else parent.as_posix()
                )

                if parent == _ROOT_SENTINEL:
                    break

                parent = parent.parent

    def _parse_status(self, code: str) -> GitStatus:
        if code in {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}:
            return GitStatus.UNMERGED

        if "??" in code:
            return GitStatus.UNTRACKED
        if "!!" in code:
            return GitStatus.IGNORED

        if "R" in code:
            return GitStatus.RENAMED
        if "C" in code:
            return GitStatus.COPIED
        if "A" in code:
            return GitStatus.ADDED
        if "D" in code:
            return GitStatus.DELETED
        if "T" in code:
            return GitStatus.TYPE_CHANGED
        if "M" in code:
            return GitStatus.MODIFIED

        return GitStatus.CLEAN

    def enrich(self, node: TreeNode, /, *, stat: stat_result | None = None) -> None:
        # 1. Initialize detection and caching on first call
        if self._git_available is None:
            self._check_git_and_find_root(node.path)

            if self._git_available and self._repo_root:
                self._load_git_status_cache()

        if not self._git_available or not self._repo_root:
            node.metadata.git = GitMetadata()
            return

        # 2. Relative path to the root dir of the git repo
        try:
            abs_path = node.path.resolve()
            rel_to_repo = abs_path.relative_to(self._repo_root).as_posix()
        except ValueError:
            node.metadata.git = GitMetadata()
            return

        if rel_to_repo == ".":
            rel_to_repo = ""

        if node.is_dir:
            if rel_to_repo == "":
                has_changes = bool(self._dirty_dirs)
            else:
                has_changes = rel_to_repo in self._dirty_dirs

            node.metadata.git = GitMetadata(
                tracked=True,
                is_repo_root=bool(abs_path == self._repo_root),
                has_sub_changes=has_changes,
                status=GitStatus.DIRTY if has_changes else GitStatus.CLEAN,
            )
        else:
            tracked = rel_to_repo in self._tracked_paths
            status = self._status_cache.get(
                rel_to_repo, GitStatus.CLEAN if tracked else GitStatus.UNTRACKED
            )
            node.metadata.git = GitMetadata(tracked=tracked, status=status)
