# tests/test_rendering/test_formats/test_graphviz.py
from ltree.config.config import TreeConfig
from ltree.rendering import GraphvizRenderer


# ======================================================================= #
# Tests: Graphviz Renderer
# ======================================================================= #
def test_graphviz_renderer_output(sample_serialized_node):
    config = TreeConfig()

    # Case 1: show_size = True
    config.show_size = True

    renderer = GraphvizRenderer(config)
    dot_content = renderer.render(sample_serialized_node)

    assert "digraph G {" in dot_content
    assert "rankdir=LR;" in dot_content
    assert 'bgcolor="#0b0e14"' in dot_content

    assert "node0 [label=" in dot_content
    assert "node1 [label=" in dot_content
    assert "root" in dot_content
    assert "main.py" in dot_content

    assert "node0 -> node1;" in dot_content
    assert "node1 -> node2;" in dot_content

    assert "(1536 B)" in dot_content

    # Case 2: show_size = False
    renderer.config.show_size = False
    dot_content = renderer.render(sample_serialized_node)

    assert "(1536 B)" not in dot_content
