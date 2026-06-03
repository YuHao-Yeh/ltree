# ltree/serializers/base.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ltree.core.models import TreeNode
    from ltree.serializers.types import SerializedNode


class Serializer(ABC):
    @abstractmethod
    def serialize(self, node: "TreeNode") -> "SerializedNode":
        raise NotImplementedError
