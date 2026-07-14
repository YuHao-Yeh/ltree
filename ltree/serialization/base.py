# ltree/serialization/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ltree.config.config import TreeConfig
    from ltree.serialization.types import SerializedNode
    from ltree.tree.models import TreeNode


class Serializer(ABC):
    def __init__(self, config: TreeConfig | None = None):
        self.config = config

    @abstractmethod
    def serialize(self, node: "TreeNode") -> "SerializedNode":
        raise NotImplementedError
