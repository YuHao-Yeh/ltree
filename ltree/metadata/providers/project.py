# ltree/metadata/provider/project.py
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.metadata.base import MetadataProvider
from ltree.metadata.models import ProjectMetadata

if TYPE_CHECKING:
    from os import stat_result
    from ltree.tree.models import TreeNode


class ProjectMetadataProvider(MetadataProvider):
    def _parse_package_json(self, path: Path) -> ProjectMetadata:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ProjectMetadata(
                    project_type="NodeJS",
                    name=data.get("name", "unknown"),
                    version=data.get("version", "unknown"),
                )
        except Exception:
            return ProjectMetadata()

    def _parse_pyproject_toml(self, path: Path) -> ProjectMetadata:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                return ProjectMetadata(
                    project_type="Python (PEP 518)",
                    name=name_match.group(1) if name_match else "unknown",
                    version=version_match.group(1) if version_match else "unknown",
                )
        except Exception:
            return ProjectMetadata()

    def enrich(self, node: TreeNode, /, *, stat: stat_result | None = None) -> None:
        if node.is_dir:
            return

        filename = node.name
        info = {}

        if filename == "package.json":
            info = self._parse_package_json(node.path)
        elif filename == "pyproject.toml":
            info = self._parse_pyproject_toml(node.path)

        if info:
            node.metadata.project = info
