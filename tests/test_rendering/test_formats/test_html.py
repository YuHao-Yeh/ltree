# tests/test_rendering/test_formats/test_html.py
from ltree.config.config import TreeConfig
from ltree.rendering import HtmlRenderer


# ======================================================================= #
# Tests: HtmlRenderer
# ======================================================================= #
def test_html_renderer_basic_structure(sample_serialized_node):
    config = TreeConfig()
    config.show_size = True
    config.show_git = True
    config.show_permission = True

    renderer = HtmlRenderer(config)
    html_content = renderer.render(sample_serialized_node)

    assert "<!DOCTYPE html>" in html_content
    assert "<html>" in html_content
    assert "<style>" in html_content
    assert "background-color: #0b0e14" in html_content

    assert '<table class="tree-table">' in html_content
    assert '<td class="col-perm">' in html_content
    assert '<td class="col-size">' in html_content

    assert "root" in html_content
    assert "main.py" in html_content
    assert "└── " in html_content


def test_html_renderer_style_isolation_detail(sample_serialized_node):
    config = TreeConfig()
    config.show_project = True

    sample_serialized_node["metadata"]["project"] = {
        "project_type": "Python",
        "name": "ltree",
        "version": "0.8.0",
    }

    renderer = HtmlRenderer(config)
    html_content = renderer.render(sample_serialized_node)

    assert '<span class="detail-text">' in html_content
    assert "ltree v0.8.0 (Python)" in html_content


def test_html_renderer_truncated_detail(sample_serialized_node):
    config = TreeConfig()
    config.show_ellipsis = True

    renderer = HtmlRenderer(config)
    html_content = renderer.render(sample_serialized_node)

    assert "(0 dirs, 2 files)" in html_content
