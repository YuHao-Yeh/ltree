# tests/test_renderers/test_rich.py
from ltree.core.config import TreeConfig
from ltree.renderers.rich import RichRenderer


# ======================================================================= #
# Test: RowBuilder
# ======================================================================= #
def test_rich_renderer_without_color(sample_tree):
    config = TreeConfig()
    config.use_color = False
    config.show_size = True

    renderer = RichRenderer(config)
    rich_content = renderer.render(sample_tree)

    assert "\x1b[" not in rich_content

    assert "root" in rich_content
    assert "main.py" in rich_content


def test_rich_renderer_with_color(sample_tree):
    config = TreeConfig()
    config.use_color = True
    config.show_permission = True
    config.show_git = True
    config.show_size = True

    renderer = RichRenderer(config)
    rich_content = renderer.render(sample_tree)

    assert "\x1b[" in rich_content
    assert "\x1b[1;36m" in rich_content or "\x1b[36m" in rich_content
    assert "\x1b[33m" in rich_content
    assert "\x1b[2;36m" in rich_content or "\x1b[36m" in rich_content


def test_rich_renderer_label(sample_tree):
    config = TreeConfig()
    config.show_size = True
    config.theme = "emoji"

    renderer = RichRenderer(config)
    rich_content = renderer.render(sample_tree)

    assert "├── 📦 src" in rich_content
    assert "│   └── ltree v0.1.0 (Python)" in rich_content


def test_rich_renderer_no_metadata(sample_tree):
    config = TreeConfig()
    config.show_permission = False
    config.show_git = False
    config.show_size = False
    config.show_time = False

    renderer = RichRenderer(config)
    rich_content = renderer.render(sample_tree)

    assert "?" not in rich_content
    assert "yesterday" not in rich_content
