# tests/test_renderers/test_json.py
import json

from ltree.core.config import TreeConfig
from ltree.renderers import JsonRenderer


# ======================================================================= #
# Test: JsonRenderer
# ======================================================================= #
def test_render_json(sample_serialized_node):
    config = TreeConfig()

    json_output = JsonRenderer(config).render(sample_serialized_node)
    json_content = json.loads(json_output)

    assert json_content["name"] == "root"
    assert json_content["metadata"]["fs"]["size"] == 2036
    assert json_content["stats"]["hidden_files"] == 2

    assert len(json_content["children"]) == 3
