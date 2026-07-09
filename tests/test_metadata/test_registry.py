# tests/test_metadata/test_registry.py
from unittest.mock import MagicMock

from ltree.core.models import TreeNode
from ltree.core.config import TreeConfig
from ltree.core.metadata import (
    MetadataProvider,
    MetadataPipeline,
    FilesystemMetadataProvider,
    CodeMetadataProvider,
    ProjectMetadataProvider,
    TimeMetadataProvider,
    GitMetadataProvider,
    get_default_pipeline,
)


# ======================================================================= #
# Tests: MetadataPipeline
# ======================================================================= #
def test_metadata_pipeline_registration():
    pipeline = MetadataPipeline()
    provider = MagicMock(spec=MetadataProvider)

    res = pipeline.register(provider)
    assert res is pipeline
    assert provider in pipeline._providers


def test_metadata_pipeline_execute_success():
    pipeline = MetadataPipeline()
    provider1 = MagicMock(spec=MetadataProvider)
    provider2 = MagicMock(spec=MetadataProvider)

    pipeline.register(provider1).register(provider2)

    node = TreeNode(path="/dummy/path")
    config = TreeConfig()

    pipeline.execute(node, config)

    provider1.enrich.assert_called_once_with(node, config)
    provider2.enrich.assert_called_once_with(node, config)


def test_metadata_pipeline_execute_with_os_error():
    pipeline = MetadataPipeline()

    provider1 = MagicMock(spec=MetadataProvider)
    provider1.enrich.side_effect = OSError("Read permissions error")

    provider2 = MagicMock(spec=MetadataProvider)

    pipeline.register(provider1).register(provider2)

    node = TreeNode(path="/dummy/path")
    config = TreeConfig()

    pipeline.execute(node, config)

    provider1.enrich.assert_called_once_with(node, config)
    provider2.enrich.assert_called_once_with(node, config)


# ======================================================================= #
# Tests: get_default_pipeline()
# ======================================================================= #
def test_get_default_pipeline_with_gitignore():
    config = TreeConfig()
    config.use_gitignore = True

    pipeline = get_default_pipeline(config)
    provider_types = [type(p) for p in pipeline._providers]

    assert FilesystemMetadataProvider in provider_types
    assert CodeMetadataProvider in provider_types
    assert ProjectMetadataProvider in provider_types
    assert TimeMetadataProvider in provider_types
    assert GitMetadataProvider in provider_types


def test_get_default_pipeline_without_gitignore():
    config = TreeConfig()
    config.use_gitignore = False

    pipeline = get_default_pipeline(config)
    provider_types = [type(p) for p in pipeline._providers]

    assert FilesystemMetadataProvider in provider_types
    assert CodeMetadataProvider in provider_types
    assert ProjectMetadataProvider in provider_types
    assert TimeMetadataProvider in provider_types
    assert GitMetadataProvider not in provider_types
