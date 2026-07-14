# ltree/themes/nerd.py
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .base import BaseTheme
from ltree.tree.models import NodeType

if TYPE_CHECKING:
    from ltree.serialization.types import SerializedNode


class NerdTheme(BaseTheme):
    DEFAULT_FILE = "󰈔"
    DEFAULT_FOLDER = ""

    FILE_ICON = {
        "Dockerfile": "",
        "Makefile": "",
        "LICENSE": "󰿃",
        "README.md": "",
        "pyproject.toml": "",
        ".gitignore": "",
        ".env": "",
    }

    EXT_ICON = {
        ".py": "",
        ".js": "",
        ".ts": "",
        ".html": "",
        ".css": "",
        ".json": "",
        ".md": "",
        ".rs": "",
        ".go": "",
        ".sql": "",
        ".zip": "",
    }

    DIR_ICON = {
        ".git": "",
        "node_modules": "",
        ".venv": "",
        "venv": "",
        "tests": "",
        "src": "",
        "docs": "󰈙",
        ".vscode": "",
    }

    def get_icon(self, node: SerializedNode) -> str:
        if node["metadata"].get("fs")["is_symlink"]:
            return " "

        if node["type"] == "directory":
            icon = self.DIR_ICON.get(node["name"], self.DEFAULT_FOLDER)
        else:
            name = node["name"]
            if name in self.FILE_ICON:
                icon = self.FILE_ICON[name]
            else:
                ext = node["metadata"].get("fs")["extension"]
                if not ext:
                    _, file_ext = os.path.splitext(name)
                    ext = file_ext.lower()
                icon = self.EXT_ICON.get(ext, self.DEFAULT_FILE)
        return f"{icon} "

    def get_style(self, node: SerializedNode) -> str:
        fs = node["metadata"].get("fs")
        if fs["is_symlink"]:
            return "italic magenta"
        if node["type"] == NodeType.DIR.value:
            return "bold cyan"
        if fs["is_executable"]:
            return "bold green"
        return "white"
