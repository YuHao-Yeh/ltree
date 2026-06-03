# tests/test_metadata/test_time.py
import os
import time
import pytest
from unittest.mock import patch

from ltree.core.models import TreeNode, NodeType
from ltree.core.config import TreeConfig
from ltree.core.metadata.time import TimeMetadataProvider


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture
def config():
    return TreeConfig()


@pytest.fixture
def provider():
    return TimeMetadataProvider()


# ======================================================================= #
# Tests: TimeMetadataProvider
# ======================================================================= #
def test_time_metadata_provider_relative_times(provider: TimeMetadataProvider):
    now = time.time()

    # 1. < 60 s -> "just now"
    assert provider._get_relative_time(now - 30) == "just now"

    # 2. < 3600 s -> "Xm ago"
    assert provider._get_relative_time(now - 600) == "10m ago"

    # 3. < 86400 s -> "Xh ago"
    assert provider._get_relative_time(now - 18000) == "5h ago"

    # 4. yesterday (86400 <= diff < 172800) -> "yesterday"
    assert provider._get_relative_time(now - 90000) == "yesterday"

    # 5. days ago (e.g. 5 days) -> "Xd ago"
    assert provider._get_relative_time(now - 5 * 86400) == "5d ago"

    # 6. long time ago (e.g. 40 days ago) -> "YYYY-MM-DD"
    long_ago = now - 40 * 86400
    res = provider._get_relative_time(long_ago)
    assert len(res) == 10
    assert res[4] == "-"
    assert res[7] == "-"


def test_time_metadata_provider_enrich_success(config, provider):
    node = TreeNode(path="/dummy/file.txt", ntype=NodeType.FILE)

    mtime = 1779888000.0
    mock_stat = os.stat_result((0, 0, 0, 0, 0, 0, 0, 0, mtime, 0))

    with patch("os.lstat", return_value=mock_stat):
        provider.enrich(node, config)

    assert node.metadata.time is not None
    assert node.metadata.time.modified_timestamp == mtime
    assert "2026-" in node.metadata.time.modified_iso


def test_time_metadata_provider_enrich_os_error(config, provider):
    node = TreeNode(path="/dummy/missing.txt", ntype=NodeType.FILE)

    with patch("os.lstat", side_effect=OSError):
        provider.enrich(node, config)

    assert node.metadata.time is not None
    assert node.metadata.time.modified_timestamp == 0.0
    assert node.metadata.time.modified_iso == ""
    assert node.metadata.time.relative_modified == "unknown"
