# tests/test_renderers/test_block.py
from ltree.core.config import TreeConfig
from ltree.renderers import MarkdownBlockRenderer


# ======================================================================= #
# Test: MarkdownBlockRenderer
# ======================================================================= #
def test_markdown_renderer_basic(sample_tree):
    config = TreeConfig()
    config.use_color = True
    renderer = MarkdownBlockRenderer(config)

    block_output = renderer.render(sample_tree)

    assert "```text" in block_output
    assert "\x1b[" not in block_output
