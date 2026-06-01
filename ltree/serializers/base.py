# ltree/serializers/base.py
from abc import ABC, abstractmethod

from ltree.core.models import TreeNode
from ltree.serializers.types import SerializedNode


class Serializer(ABC):
    @abstractmethod
    def serialize(
        self,
        node: TreeNode,
    ) -> SerializedNode:
        raise NotImplementedError
