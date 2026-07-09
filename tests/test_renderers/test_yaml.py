# tests/test_renderers/test_yaml.py
import pytest
from ltree.core.config import TreeConfig
from ltree.renderers.yaml import YamlRenderer


# ======================================================================= #
# Test: YamlRenderer
# ======================================================================= #
def test_yaml_renderer_syntax_and_structure(sample_serialized_node):
    config = TreeConfig()
    renderer = YamlRenderer(config)

    yaml_content = renderer.render(sample_serialized_node)

    assert "name: root" in yaml_content
    assert "type: directory" in yaml_content
    assert "children:" in yaml_content

    try:
        import yaml

        parsed_data = yaml.safe_load(yaml_content)

        assert parsed_data["name"] == "root"
        assert parsed_data["type"] == "directory"
        assert len(parsed_data["children"]) == 3

        # 驗證 children 的順序 (應與 Serializer 序列化順序一致)
        child_names = [child["name"] for child in parsed_data["children"]]
        assert child_names == ["src", "truncated_dir", "README.md"]

    except ImportError:
        pytest.skip("pyyaml is not installed, skipping strict YAML validation")


def test_yaml_renderer_without_pyyaml(sample_serialized_node, monkeypatch):
    config = TreeConfig()
    renderer = YamlRenderer(config)

    import builtins

    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("mocked import error")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    yaml_output = renderer.render(sample_serialized_node)

    assert "Error: No available 'pyyaml' library for YAML export." in yaml_output
