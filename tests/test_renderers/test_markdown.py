# tests/test_renderers/test_markdown.py
from ltree.core.config import TreeConfig
from ltree.renderers.markdown import MarkdownRenderer
from ltree.serializers.tree import TreeSerializer


# ======================================================================= #
# Test: MarkdownRenderer
# ======================================================================= #
def test_markdown_renderer_basic_structure(sample_serialized_node):
    config = TreeConfig()
    config.show_size = False

    renderer = MarkdownRenderer(config)
    markdown_content = renderer.render(sample_serialized_node)

    assert "- 📂 **root/**" in markdown_content
    assert "  - 📦 **src/**" in markdown_content
    assert "  - 📖 `README.md`" in markdown_content
    assert "    - 🐍 `main.py`" in markdown_content


def test_markdown_renderer_with_project(sample_tree):
    config = TreeConfig()

    # Case 1: show_project = False
    config.show_project = False

    serializer = TreeSerializer(config)
    node = serializer.serialize(sample_tree)
    renderer = MarkdownRenderer(config)
    markdown_content = renderer.render(node)

    assert "(v0.1.0)" not in markdown_content

    # Case 2: show_project = True
    serializer.config.show_project = True
    renderer.config.show_project = True
    node = serializer.serialize(sample_tree)
    markdown_content = renderer.render(node)

    assert "(v0.1.0)" in markdown_content


def test_markdown_renderer_with_size(sample_serialized_node):
    config = TreeConfig()

    # Case 1: human_readable = False
    config.show_size = True
    config.human_readable = False

    renderer = MarkdownRenderer(config)
    markdown_content = renderer.render(sample_serialized_node)

    assert "    - 🐍 `1536 B` `main.py`" in markdown_content
    assert "  - 📖 `500 B` `README.md`" in markdown_content

    # Case 2: human_readable = True
    renderer.config.human_readable = True
    markdown_content = renderer.render(sample_serialized_node)

    assert "    - 🐍 `1.5 K` `main.py`" in markdown_content
    assert "  - 📖 `500.0 B` `README.md`" in markdown_content

    # Case 3: size_val = None
    sample_serialized_node["metadata"]["fs"]["size"] = None
    renderer.config.human_readable = False
    markdown_content = renderer.render(sample_serialized_node)

    assert "    - 🐍 `1536 B` `main.py`" in markdown_content
    assert "  - 📖 `500 B` `README.md`" in markdown_content


def test_markdown_renderer_truncated_ellipsis(sample_serialized_node):
    config = TreeConfig()

    # Case 1: folders_only = False
    config.show_ellipsis = True

    renderer = MarkdownRenderer(config)
    markdown_content = renderer.render(sample_serialized_node)

    assert "  - ... (0 dirs, 2 files)" in markdown_content

    # Case 2: folders_only = True
    renderer.config.folders_only = True
    renderer.config.show_ellipsis = True
    markdown_content = renderer.render(sample_serialized_node)

    assert "  - ... (0 dirs)" in markdown_content
