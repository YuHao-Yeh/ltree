from abc import ABC, abstractmethod
from ..core.models import TreeNode


class BaseTheme(ABC):
    @abstractmethod
    def get_icon(self, node: TreeNode) -> str:
        pass

    @abstractmethod
    def get_style(self, node: TreeNode) -> str:
        pass
