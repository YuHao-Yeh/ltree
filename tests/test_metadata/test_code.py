# tests/test_metadata/test_code.py
import pytest

from ltree.core.models import TreeNode, NodeType
from ltree.core.metadata.code import CodeMetadataProvider


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture
def provider():
    return CodeMetadataProvider()


# ======================================================================= #
# Tests: CodeMetadataProvider
# ======================================================================= #
def test_code_metadata_provider_directory(provider):
    node = TreeNode(path="/dummy/src", ntype=NodeType.DIR)

    provider.enrich(node)
    assert node.metadata.code is None


def test_code_metadata_provider_known_code(provider):
    node = TreeNode(path="/dummy/main.py", ntype=NodeType.FILE)

    provider.enrich(node)
    assert node.metadata.code is not None
    assert node.metadata.code.language == "python"
    assert node.metadata.code.is_source_code is True


def test_code_metadata_provider_unknown_code(provider):
    node = TreeNode(path="/dummy/data.unknown", ntype=NodeType.FILE)

    provider.enrich(node)
    assert node.metadata.code is not None
    assert node.metadata.code.language is None
    assert node.metadata.code.is_source_code is False
