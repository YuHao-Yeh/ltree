import os
import stat
import pytest
from unittest.mock import patch

from ltree.core.models import TreeNode, NodeType
from ltree.core.config import TreeConfig
from ltree.core.metadata.filesystem import FilesystemMetadataProvider


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture
def config():
    return TreeConfig()


@pytest.fixture
def provider():
    return FilesystemMetadataProvider()


# ======================================================================= #
# Tests: FilesystemMetadataProvider
# ======================================================================= #
def test_filesystem_metadata_provider_regular_file(config, provider):
    node = TreeNode(path="/dummy/test_document.TXT", ntype=NodeType.FILE)

    # Normal file permissions (stat.S_IFREG) and read/write permissions 0o644.
    mock_mode = stat.S_IFREG | 0o644
    mock_stat = os.stat_result((mock_mode, 0, 0, 0, 0, 0, 1234, 0, 0, 0))

    with patch("pathlib.Path.lstat", return_value=mock_stat):
        provider.enrich(node, config)

    assert node.is_symlink is False
    assert node.is_executable is False
    assert node.extension == ".txt"
    assert node.permissions.startswith("-rw-")
    assert node.size == 1234


def test_filesystem_metadata_provider_symlink(config, provider):
    node = TreeNode(path="/dummy/my_symlink", ntype=NodeType.FILE)

    mock_mode = stat.S_IFLNK | 0o777
    mock_stat = os.stat_result((mock_mode, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    with patch("pathlib.Path.lstat", return_value=mock_stat):
        provider.enrich(node, config)

    assert node.is_symlink is True
    assert node.permissions.startswith("l")


def test_filesystem_metadata_provider_executable(config, provider):
    node = TreeNode(path="/dummy/runner.sh", ntype=NodeType.FILE)

    mock_mode = stat.S_IFREG | stat.S_IXUSR | 0o755
    mock_stat = os.stat_result((mock_mode, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    with patch("pathlib.Path.lstat", return_value=mock_stat):
        provider.enrich(node, config)

    assert node.is_executable is True


def test_filesystem_metadata_provider_os_error(config, provider):
    node = TreeNode(path="/dummy/missing_file.txt", ntype=NodeType.FILE)

    with patch("pathlib.Path.lstat", side_effect=OSError("File target not found")):
        provider.enrich(node, config)

    assert node.is_symlink is False
    assert node.is_executable is False
    assert node.permissions == ""
    assert node.extension == ""
    assert node.size == 0
