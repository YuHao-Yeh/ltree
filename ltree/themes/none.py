from .base import BaseTheme
from ..core.models import TreeNode


class NoTheme(BaseTheme):
    def get_icon(self, node: TreeNode) -> str:
        return ""

    def get_style(self, node: TreeNode) -> str:
        return ""
