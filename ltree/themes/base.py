# ltree/themes/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ltree.serialization.types import SerializedNode


class BaseTheme(ABC):
    @abstractmethod
    def get_icon(self, node: SerializedNode) -> str:
        pass

    @abstractmethod
    def get_style(self, node: SerializedNode) -> str:
        pass
