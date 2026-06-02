# ltree/themes/manager.py
from typing import TYPE_CHECKING

from .emoji import EmojiTheme
from .nerd import NerdTheme
from .none import NoTheme

if TYPE_CHECKING:
    from ltree.serializers.types import SerializedNode


class ThemeManager:
    THEMES = {
        "emoji": EmojiTheme,
        "nerd": NerdTheme,
        "none": NoTheme,
    }

    def __init__(self, theme_name: str = "emoji"):
        theme_cls = self.THEMES.get(theme_name, NoTheme)
        self.theme = theme_cls()

    def get_icon(self, node: "SerializedNode") -> str:
        return self.theme.get_icon(node)

    def get_style(self, node: "SerializedNode") -> str:
        return self.theme.get_style(node)
