import os
from . import emoji, nerd


class IconProvider:
    def __init__(self, theme: str = "emoji"):
        self.theme = theme
        if theme == "emoji":
            self.map = emoji
        elif theme == "nerd":
            self.map = nerd
        else:
            self.map = None  # theme == "none"

    def get_icon(self, name: str, is_dir: bool) -> str:
        if not self.map:
            return ""

        if is_dir:
            icon = self.map.FOLDERS.get(name, self.map.DEFAULT_FOLDER)
        else:
            if name in self.map.FILENAMES:
                icon = self.map.FILENAMES[name]
            else:
                ext = os.path.splitext(name)[1].lower()
                icon = self.map.EXTENSIONS.get(ext, self.map.DEFAULT_FILE)

        return f"{icon} "
