import os

from .base import BaseTheme
from ..core.models import TreeNode


class EmojiTheme(BaseTheme):
    DEFAULT_FILE = "📄"
    DEFAULT_FOLDER = "📂"

    FILE_ICON = {
        "Dockerfile": "🐳",
        "Makefile": "🛠️",
        "LICENSE": "⚖️",
        "README.md": "📖",
        "pyproject.toml": "⚙️",
        "uv.lock": "🔒",
        ".gitignore": "🚫",
        ".env": "🔑",
    }

    EXT_ICON = {
        ".py": "🐍",
        ".js": "🟨",
        ".ts": "🟦",
        ".html": "🌐",
        ".css": "🎨",
        ".json": "⚙️",
        ".md": "📝",
        ".rs": "🦀",
        ".go": "🐹",
        ".sql": "🗄️",
        ".zip": "📦",
    }

    DIR_ICON = {
        ".git": "🌳",
        "node_modules": "📦",
        ".venv": "🐍",
        "venv": "🐍",
        "tests": "🧪",
        "src": "📦",
        "docs": "📚",
        "__pycache__": "🗑️",
        ".vscode": "💻",
    }

    def get_icon(self, node: TreeNode) -> str:
        if node.is_symlink:
            return "🔗 "

        if node.is_dir:
            icon = self.DIR_ICON.get(node.name, self.DEFAULT_FOLDER)
        else:
            if node.name in self.FILE_ICON:
                icon = self.FILE_ICON[node.name]
            else:
                ext = node.extension
                if not ext:
                    _, file_ext = os.path.splitext(node.name)
                    ext = file_ext.lower()
                icon = self.EXT_ICON.get(ext, self.DEFAULT_FILE)
        return f"{icon} "

    def get_style(self, node: TreeNode) -> str:
        if node.is_symlink:
            return "italic magenta"
        if node.is_dir:
            return "bold cyan"
        if node.is_executable:
            return "bold green"
        return "white"
