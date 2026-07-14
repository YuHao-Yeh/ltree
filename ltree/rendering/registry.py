# ltree/rendering/registry.py
from __future__ import annotations

from typing import TYPE_CHECKING

from .formats.graphviz import GraphvizRenderer
from .formats.html import HtmlRenderer
from .formats.json import JsonRenderer
from .formats.markdown import MarkdownRenderer
from .formats.md_block import MarkdownBlockRenderer
from .formats.rich import RichRenderer
from .formats.text import TextRenderer
from .formats.yaml import YamlRenderer

if TYPE_CHECKING:
    from .base import BaseRenderer


class RendererRegistry:
    def __init__(self):
        self._renderers: dict[str, type[BaseRenderer]] = {}

    def register(self, renderer: type[BaseRenderer]) -> None:
        if not renderer.name:
            raise ValueError(f"{renderer.__name__} has no renderer name.")

        if renderer.name in self._renderers:
            raise ValueError(f"Renderer '{renderer.name}' already registered.")

        self._renderers[renderer.name] = renderer

        for alias in renderer.aliases:
            if alias in self._renderers:
                raise ValueError(f"Alias '{alias}' already registered.")

            self._renderers[alias] = renderer

    def unregister(self, name: str) -> None:
        renderer = self._renderers.get(name)

        if renderer is None:
            return

        keys = [key for key, value in self._renderers.items() if value is renderer]

        for key in keys:
            self._renderers.pop(key)

    def get(self, name: str) -> type[BaseRenderer] | None:
        return self._renderers.get(name)

    def names(self) -> list[str]:
        return sorted({renderer.name for renderer in self._renderers.values()})

    def keys(self) -> list[str]:
        return sorted(self._renderers.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._renderers

    def __iter__(self):
        seen = set()
        for renderer in self._renderers.values():
            if renderer not in seen:
                seen.add(renderer)
                yield renderer


BUILTIN_RENDERERS = (
    TextRenderer,
    RichRenderer,
    MarkdownRenderer,
    MarkdownBlockRenderer,
    JsonRenderer,
    YamlRenderer,
    HtmlRenderer,
    GraphvizRenderer,
)

registry = RendererRegistry()

for renderer in BUILTIN_RENDERERS:
    registry.register(renderer)
