# ltree/metadata/base.py
from __future__ import annotations

from typing import Protocol, TYPE_CHECKING


if TYPE_CHECKING:
    from os import stat_result
    from ltree.tree.models import TreeNode


class MetadataProvider(Protocol):
    def enrich(self, node: TreeNode, /, *, stat: stat_result | None = None) -> None: ...
