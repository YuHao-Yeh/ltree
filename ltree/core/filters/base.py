# ltree/core/filters/base.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ltree.core.models import TreeNode


class TreeFilter(ABC):
    @abstractmethod
    def apply(self, root: "TreeNode") -> "TreeNode": ...
