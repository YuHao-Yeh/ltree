# ltree/core/filters/base.py
from abc import ABC, abstractmethod

from ltree.core.models import TreeNode


class TreeFilter(ABC):
    @abstractmethod
    def apply(self, root: TreeNode) -> TreeNode: ...
