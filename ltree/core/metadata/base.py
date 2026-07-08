# ltree/core/metadata/base.py
from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from ltree.core.config import TreeConfig

if TYPE_CHECKING:
    from ltree.core.models import TreeNode


class MetadataProvider(Protocol):
    def enrich(self, node: TreeNode, config: TreeConfig) -> None: ...
