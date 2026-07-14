# ltree/themes/manager.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ltree.themes.emoji import EmojiTheme
from ltree.themes.nerd import NerdTheme
from ltree.themes.none import NoTheme

if TYPE_CHECKING:
    from ltree.serialization.types import SerializedNode


class ThemeManager:
    THEMES = {
        "emoji": EmojiTheme,
        "nerd": NerdTheme,
        "none": NoTheme,
    }

    def __init__(self, theme_name: str = "emoji"):
        theme_cls = self.THEMES.get(theme_name, NoTheme)
        self.theme = theme_cls()

    def get_icon(self, node: SerializedNode) -> str:
        return self.theme.get_icon(node)

    def get_style(self, node: SerializedNode) -> str:
        return self.theme.get_style(node)
