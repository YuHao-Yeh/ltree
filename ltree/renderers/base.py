# ltree/renderers/base.py
from abc import ABC, abstractmethod
from typing import Literal, TYPE_CHECKING

from ltree.themes.manager import ThemeManager

if TYPE_CHECKING:
    from typing import TextIO
    from ltree.core.config import TreeConfig
    from ltree.serializers.types import SerializedNode


class BaseRenderer(ABC):
    input_type: Literal["row", "serialized"] = "serialized"

    def __init__(self, config: "TreeConfig", **kwargs):
        self.config = config
        self.theme_manager = ThemeManager(config.theme)

    @abstractmethod
    def render(self, node: "SerializedNode", output_file: "TextIO") -> None:
        pass


class Renderer(ABC):
    @abstractmethod
    def render(self, node: "SerializedNode") -> str:
        pass
