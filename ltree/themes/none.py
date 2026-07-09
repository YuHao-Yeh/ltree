# ltree/themes/none.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ltree.themes.base import BaseTheme

if TYPE_CHECKING:
    from ltree.serializers.types import SerializedNode


class NoTheme(BaseTheme):
    def get_icon(self, node: SerializedNode) -> str:
        return ""

    def get_style(self, node: SerializedNode) -> str:
        return ""
