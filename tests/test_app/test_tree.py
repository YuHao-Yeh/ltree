# tests/test_app/test_tree.py
import logging
import pytest

from ltree.config.config import TreeConfig
from ltree.app.tree import TreeApplication, RenderResult


# ======================================================================= #
# Tests: TreeApplication
# ======================================================================= #
def test_tree_application_generate_success(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")

    config = TreeConfig()
    app = TreeApplication(config)

    # A. default text format
    result = app.generate(str(tmp_path), fmt="text")
    assert isinstance(result, RenderResult)
    assert "file1.txt" in result.content
    assert result.show_stats is True

    # B. serialized format
    json_result = app.generate(str(tmp_path), fmt="json")
    assert isinstance(json_result, RenderResult)
    assert "file1.txt" in json_result.content
    assert json_result.show_stats is False


def test_tree_application_generate_non_existent_path(caplog):
    config = TreeConfig()
    app = TreeApplication(config)

    with caplog.at_level(logging.ERROR):
        result = app.generate("non_existent_path_999")

    assert "Path 'non_existent_path_999' does not exist." in caplog.text
    assert isinstance(result, RenderResult)
    assert result.content == ""
    assert result.show_stats is False


def test_tree_application_generate_renderclass_error():
    config = TreeConfig()
    app = TreeApplication(config)

    with pytest.raises(ValueError):
        app.generate(".", fmt="abc")
