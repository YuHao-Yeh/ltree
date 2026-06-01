# ltree/renderers/base.py
from abc import ABC, abstractmethod
from typing import TextIO

from ltree.core.config import TreeConfig
from ltree.serializers.types import SerializedNode
from ltree.themes.manager import ThemeManager


class BaseRenderer(ABC):
    def __init__(self, config: TreeConfig):
        self.config = config
        self.theme_manager = ThemeManager(config.theme)

    @abstractmethod
    def render(self, node: SerializedNode, output_file: TextIO) -> None:
        pass
