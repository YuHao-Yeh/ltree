# ltree/renderers/__init__.py
from ltree.renderers.base import BaseRenderer
from ltree.renderers.graphviz import GraphvizRenderer
from ltree.renderers.html import HtmlRenderer
from ltree.renderers.json import JsonRenderer
from ltree.renderers.markdown import MarkdownRenderer
from ltree.renderers.md_block import MarkdownBlockRenderer
from ltree.renderers.rich import RichRenderer
from ltree.renderers.row_builder import RowBuilder
from ltree.renderers.text import TextRenderer
from ltree.renderers.yaml import YamlRenderer


__all__ = [
    "BaseRenderer",
    "GraphvizRenderer",
    "HtmlRenderer",
    "JsonRenderer",
    "MarkdownRenderer",
    "MarkdownBlockRenderer",
    "RichRenderer",
    "RowBuilder",
    "TextRenderer",
    "YamlRenderer",
]


def get_renderer_class(fmt: str) -> BaseRenderer:
    renderers = {
        "block": MarkdownBlockRenderer,
        "graphviz": GraphvizRenderer,
        "html": HtmlRenderer,
        "json": JsonRenderer,
        "markdown": MarkdownRenderer,
        "md": MarkdownRenderer,
        "rich": RichRenderer,
        "text": TextRenderer,
        "yaml": YamlRenderer,
    }
    return renderers.get(fmt, TextRenderer)
