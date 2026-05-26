from .emoji import EmojiTheme
from .nerd import NerdTheme
from .none import NoTheme
from ..core.models import TreeNode


class ThemeManager:
    THEMES = {
        "emoji": EmojiTheme,
        "nerd": NerdTheme,
        "none": NoTheme,
    }

    def __init__(self, theme_name: str = "emoji"):
        theme_cls = self.THEMES.get(theme_name, NoTheme)
        self.theme = theme_cls()

    def get_icon(self, node: TreeNode) -> str:
        return self.theme.get_icon(node)

    def get_style(self, node: TreeNode) -> str:
        return self.theme.get_style(node)
