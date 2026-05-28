# ltree/core/metadata/git.py
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.core.config import TreeConfig
from ltree.core.metadata.base import MetadataProvider
from ltree.core.metadata.models import GitMetadata

if TYPE_CHECKING:
    from ltree.core.models import TreeNode


class GitMetadataProvider(MetadataProvider):
    def __init__(self):
        self._repo_root = None
        self._git_available = None
        self._status_cache = {}  # rel_path -> git status (ex. "src/main.py" -> "modified")

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
            self._repo_root = os.path.abspath(res.stdout.strip())
            self._git_available = True
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            self._git_available = False

    def _load_git_status_cache(self) -> None:
        if not self._repo_root:
            return

        try:
            # cmd: git status --porcelain
            res = subprocess.run(
                ["git", "status", "--porcelain", "--ignored"],
                cwd=self._repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

            for line in res.stdout.splitlines():
                if len(line) < 4:
                    continue
                code = line[:2]
                rel_path = line[3:].strip().strip('"')
                rel_path = rel_path.replace("\\", "/")

                status = "clean"
                if "M" in code:
                    status = "modified"
                elif "A" in code:
                    status = "staged_added"
                elif "D" in code:
                    status = "deleted"
                elif "R" in code:
                    status = "renamed"
                elif "C" in code:
                    status = "copied"
                elif "U" in code:
                    status = "unmerged"
                elif "??" in code:
                    status = "untracked"
                elif "!!" in code:
                    status = "ignored"

                self._status_cache[rel_path] = status
        except subprocess.SubprocessError:
            pass

    def enrich(self, node: "TreeNode", config: TreeConfig) -> None:
        # 1. Initialize detection and caching on first call
        if self._git_available is None:
            self._check_git_and_find_root(node.path)
            if self._git_available and self._repo_root:
                self._load_git_status_cache()

        if not self._git_available or not self._repo_root:
            node.metadata.git = GitMetadata()
            return

        # 2. Relative path to the root dir of the git repo
        abs_path = os.path.abspath(node.path)
        if not abs_path.startswith(self._repo_root):
            node.metadata.git = GitMetadata()
            return

        rel_to_repo = os.path.relpath(abs_path, self._repo_root).replace("\\", "/")
        if node.is_dir:
            has_changes = any(
                p.startswith(rel_to_repo + "/") for p in self._status_cache
            )
            node.metadata.git = GitMetadata(
                tracked=True,
                is_repo_root=bool(abs_path == self._repo_root),
                has_sub_changes=has_changes,
                status="modified" if has_changes else "clean",
            )
        else:
            status = self._status_cache.get(rel_to_repo, "clean")
            node.metadata.git = GitMetadata(
                tracked=bool(status != "ignored"), status=status
            )
