import pytest
from unittest.mock import patch, mock_open

from ltree.core.models import TreeNode, NodeType
from ltree.core.config import TreeConfig
from ltree.core.metadata.project import ProjectMetadataProvider


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture
def config():
    return TreeConfig()


@pytest.fixture
def provider():
    return ProjectMetadataProvider()


# ======================================================================= #
# Tests: ProjectMetadataProvider
# ======================================================================= #
def test_project_metadata_provider_directory(config, provider):
    node = TreeNode(path="/dummy/src", ntype=NodeType.DIR)

    provider.enrich(node, config)
    assert node.metadata.project is None


def test_project_metadata_provider_package_json(config, provider):
    node = TreeNode(path="/dummy/package.json", ntype=NodeType.FILE)

    mock_json = '{"name": "ltree", "version": "1.0.0"}'
    with patch("builtins.open", mock_open(read_data=mock_json)):
        provider.enrich(node, config)

    assert node.metadata.project is not None
    assert node.metadata.project.project_type == "NodeJS"
    assert node.metadata.project.name == "ltree"
    assert node.metadata.project.version == "1.0.0"


def test_project_metadata_provider_package_json_corrupted(config, provider):
    node = TreeNode(path="/dummy/package.json", ntype=NodeType.FILE)

    mock_json = "{invalid json"
    with patch("builtins.open", mock_open(read_data=mock_json)):
        provider.enrich(node, config)

    assert node.metadata.project is not None
    assert node.metadata.project.project_type == ""
    assert node.metadata.project.name == ""
    assert node.metadata.project.version == ""


def test_project_metadata_provider_pyproject_toml(config, provider):
    node = TreeNode(path="/dummy/pyproject.toml", ntype=NodeType.FILE)

    mock_toml = """
    [project]
    name = "ltree-cli"
    version = "0.2.1"
    """
    with patch("builtins.open", mock_open(read_data=mock_toml)):
        provider.enrich(node, config)

    assert node.metadata.project is not None
    assert node.metadata.project.project_type == "Python (PEP 518)"
    assert node.metadata.project.name == "ltree-cli"
    assert node.metadata.project.version == "0.2.1"


def test_project_metadata_provider_pyproject_toml_corrupted(config, provider):
    node = TreeNode(path="/dummy/pyproject.toml", ntype=NodeType.FILE)

    with patch("builtins.open", side_effect=Exception("Read Error")):
        provider.enrich(node, config)

    assert node.metadata.project is not None
    assert node.metadata.project.project_type == ""
    assert node.metadata.project.name == ""
    assert node.metadata.project.version == ""


def test_project_metadata_provider_unmatched_file(config, provider):
    node = TreeNode(path="/dummy/readme.txt", ntype=NodeType.FILE)

    provider.enrich(node, config)
    assert node.metadata.project is None
