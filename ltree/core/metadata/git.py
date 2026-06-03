# ltree/core/metadata/git.py
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.core.metadata.base import MetadataProvider
from ltree.core.metadata.models import GitMetadata, GitStatus

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode


class GitMetadataProvider(MetadataProvider):
    def __init__(self):
        self._repo_root: Path | None = None
        self._git_available: bool | None = None
        # rel_path -> status
        self._status_cache: dict[str, GitStatus] = {}
        # tracked paths
        self._tracked_paths: set[str] = set()

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
            # cmd: git status --porcelain=v1 --ignored
            # -uall -> --untracked-files=all
            res = subprocess.run(
                ["git", "status", "--porcelain=v1", "--ignored"],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                check=True,
            )

            for line in res.stdout.splitlines():
                if len(line) < 4:
                    continue

                code = line[:2]
                rel_path = line[3:].strip().strip('"').replace("\\", "/")

                # rename handling:
                # R old.py -> new.py
                if "->" in rel_path:
                    rel_path = rel_path.split("->", 1)[1].strip()

                rel_path = rel_path.replace("\\", "/")

                status = self._parse_status(code)
                self._status_cache[rel_path] = status

                if status != GitStatus.IGNORED:
                    self._tracked_paths.add(rel_path)

        except subprocess.SubprocessError:
            pass

    def _parse_status(self, code: str) -> GitStatus:
        if "??" in code:
            return GitStatus.UNTRACKED

        if "!!" in code:
            return GitStatus.IGNORED

        if "U" in code:
            return GitStatus.UNMERGED

        if "R" in code:
            return GitStatus.RENAMED

        if "A" in code:
            return GitStatus.ADDED

        if "D" in code:
            return GitStatus.DELETED

        if "C" in code:
            return GitStatus.COPIED

        if "M" in code:
            return GitStatus.MODIFIED

        return GitStatus.CLEAN

    def _is_inside_repo(self, path: Path) -> bool:
        if not self._repo_root:
            return False

        try:
            path.resolve().relative_to(self._repo_root)
            return True
        except ValueError:
            return False

    def enrich(self, node: "TreeNode", config: "TreeConfig") -> None:
        # 1. Initialize detection and caching on first call
        if self._git_available is None:
            self._check_git_and_find_root(node.path)

            if self._git_available and self._repo_root:
                self._load_git_status_cache()

        if not self._git_available or not self._repo_root:
            node.metadata.git = GitMetadata()
            return

        # 2. Relative path to the root dir of the git repo
        if not self._is_inside_repo(node.path):
            node.metadata.git = GitMetadata()
            return

        abs_path = node.path.resolve()
        rel_to_repo = abs_path.relative_to(self._repo_root).as_posix()
        if rel_to_repo == ".":
            rel_to_repo = ""

        if node.is_dir:
            if rel_to_repo == "":
                has_changes = bool(self._status_cache)
            else:
                # prefix = rel_to_repo + "/"
                has_changes = any(
                    p.startswith(rel_to_repo + "/") for p in self._status_cache
                )

            node.metadata.git = GitMetadata(
                tracked=True,
                is_repo_root=bool(abs_path == self._repo_root),
                has_sub_changes=has_changes,
                status=GitStatus.DIRTY if has_changes else GitStatus.CLEAN,
            )
        else:
            tracked = bool(rel_to_repo in self._tracked_paths)
            status = self._status_cache.get(
                rel_to_repo, GitStatus.CLEAN if tracked else GitStatus.UNTRACKED
            )
            node.metadata.git = GitMetadata(tracked=tracked, status=status)
