# ltree/serializers/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode
    from ltree.serializers.types import SerializedNode


class Serializer(ABC):
    def __init__(self, config: TreeConfig | None = None):
        self.config = config

    @abstractmethod
    def serialize(self, node: "TreeNode") -> "SerializedNode":
        raise NotImplementedError
