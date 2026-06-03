# ltree/core/metadata/code.py
import os
from typing import TYPE_CHECKING

from ltree.core.metadata.base import MetadataProvider
from ltree.core.metadata.models import CodeMetadata

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode


class CodeMetadataProvider(MetadataProvider):
    LANG_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript-react",
        ".jsx": "javascript-react",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c/cpp",
        ".java": "java",
        ".html": "html",
        ".css": "css",
        ".sh": "bash",
        ".md": "markdown",
        ".json": "json",
        ".toml": "toml",
        ".yaml": "yaml",
        ".yml": "yaml",
    }

    def enrich(self, node: "TreeNode", config: "TreeConfig") -> None:
        if node.is_dir:
            return

        _, ext = os.path.splitext(node.name)
        ext_lower = ext.lower()
        language = self.LANG_MAP.get(ext_lower, None)

        node.metadata.code = CodeMetadata(
            language=language, is_source_code=bool(language is not None)
        )
