# ltree/renderers/row_builder.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ltree.core.models import NodeType
from ltree.core.metadata.models import GitStatus
from ltree.renderers.models import (
    RenderRow,
    RenderDetail,
    MetadataToken,
    GIT_SYMBOL_MAP,
)
from ltree.core.utils import format_size_classic

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode
    from ltree.themes.manager import ThemeManager


class RowBuilder:
    def __init__(self, config: TreeConfig, theme_manager: ThemeManager):
        self.config = config
        self.theme = theme_manager

    def build(self, node: TreeNode) -> RenderRow:
        meta = node.metadata
        fs = meta.fs if meta else None
        git = meta.git if meta else None
        time_meta = meta.time if meta else None

        # 1. Permission token
        perm_text = fs.permissions if (self.config.show_permission and fs) else ""
        permission_token = MetadataToken(text=perm_text, kind="perm")

        # 2. Git status token
        git_text = ""
        git_status = GitStatus.CLEAN
        if self.config.show_git and git:
            git_status = git.status
            git_text = GIT_SYMBOL_MAP.get(git.status, "")
        git_token = MetadataToken(text=git_text, kind="git", status=git_status)

        # 3. Size Token
        size_text = ""
        if self.config.show_size and fs:
            size_bytes = fs.size
            if node.ntype == NodeType.FILE or size_bytes > 0:
                size_text = format_size_classic(
                    size_bytes, self.config.human_readable
                ).strip()
        size_token = MetadataToken(text=size_text, kind="size")

        # 4. Modification time Token
        time_text = ""
        if self.config.show_time and time_meta:
            time_text = time_meta.relative_modified
        time_token = MetadataToken(text=time_text, kind="time")

        # 5. Transformation and compatibility with existing ThemeManager
        # Current ThemeManager expects dict input
        compat_dict = {
            "name": node.name,
            "type": "directory" if node.ntype == NodeType.DIR else "file",
            "metadata": {
                "fs": {
                    "is_symlink": fs.is_symlink if fs else False,
                    "extension": fs.extension if fs else "",
                }
            },
        }
        icon = self.theme.get_icon(compat_dict)

        # 6. Detail information
        details = self._build_details(node)

        return RenderRow(
            name=node.name,
            icon=icon,
            is_dir=(node.ntype == NodeType.DIR),
            permission=permission_token,
            git=git_token,
            size=size_token,
            time=time_token,
            details=details,
        )

    def _build_details(self, node: TreeNode) -> list[RenderDetail]:
        meta = node.metadata
        if not meta:
            return []

        details = []

        # A. Code
        if self.config.show_code and meta.code and meta.code.is_source_code:
            code = meta.code
            if code.language:
                details.append(
                    RenderDetail(
                        kind="code",
                        text=f"language={code.language}",
                    )
                )

        # B. Project
        if self.config.show_project and meta.project and meta.project.project_type:
            p = meta.project
            details.append(
                RenderDetail(
                    kind="project", text=f"{p.name} v{p.version} ({p.project_type})"
                )
            )

        # C. Truncated directory
        if node.is_truncated and self.config.show_ellipsis:
            s = node.stats
            if self.config.folders_only:
                details.append(
                    RenderDetail(kind="truncated", text=f"... ({s.hidden_dirs} dirs)")
                )
            else:
                details.append(
                    RenderDetail(
                        kind="truncated",
                        text=f"... ({s.hidden_dirs} dirs, {s.hidden_files} files)",
                    )
                )

        return details
