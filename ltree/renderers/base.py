from abc import ABC, abstractmethod
from typing import TextIO

from ltree.core.models import TreeNode
from ltree.core.config import TreeConfig
from ltree.themes.manager import ThemeManager


class BaseRenderer(ABC):
    def __init__(self, config: TreeConfig):
        self.config = config
        self.theme_manager = ThemeManager(config.theme)

    @abstractmethod
    def render(self, node: TreeNode, output_file: TextIO) -> None:
        pass
