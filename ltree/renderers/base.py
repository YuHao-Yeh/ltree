from abc import ABC, abstractmethod
from typing import TextIO

from ..core.models import TreeNode
from ..core.config import TreeConfig
from ..themes.icons import IconProvider

class BaseRenderer(ABC):
    def __init__(self, config: TreeConfig):
        self.config = config
        self.icon_provider = IconProvider(config.theme)

    @abstractmethod
    def render(self, node: TreeNode, output_file: TextIO) -> None:
        pass