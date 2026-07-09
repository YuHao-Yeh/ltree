# tests/test_cli/test_app_tree.py
from ltree.core.config import TreeConfig
from ltree.app.tree import TreeApplication, RenderResult


def test_tree_application_generate_success(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")

    config = TreeConfig()
    app = TreeApplication(config)

    # A. default text format
    result = app.generate(str(tmp_path), fmt="text")
    assert isinstance(result, RenderResult)
    assert "file1.txt" in result.content
    assert result.rtype == "row"

    # B. serialized format
    json_result = app.generate(str(tmp_path), fmt="json")
    assert isinstance(json_result, RenderResult)
    assert "file1.txt" in json_result.content
    assert json_result.rtype == "serialized"


def test_tree_application_generate_non_existent_path(capsys):
    config = TreeConfig()
    app = TreeApplication(config)

    result = app.generate("non_existent_path_999")

    captured = capsys.readouterr()
    assert "Path 'non_existent_path_999' does not exist." in captured.err
    assert isinstance(result, RenderResult)
    assert result.content == ""
    assert result.rtype == "row"
