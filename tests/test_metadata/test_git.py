# tests/test_metadata/test_git.py
import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from ltree.core.models import TreeNode, NodeType
from ltree.core.config import TreeConfig
from ltree.core.metadata.git import GitMetadataProvider
from ltree.core.metadata.models import GitStatus


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture
def config():
    return TreeConfig()


@pytest.fixture
def provider():
    return GitMetadataProvider()


# ======================================================================= #
# Tests: GitMetadataProvider
# ======================================================================= #
# --- Tests: Initialization & Root Detection ---
def test_git_metadata_provider_git_not_available(config, provider):
    node = TreeNode(path="/dummy/file.txt", ntype=NodeType.FILE)

    with patch("subprocess.run", side_effect=FileNotFoundError):
        provider.enrich(node, config)

    assert provider._git_available is False
    assert node.metadata.git is not None
    assert node.metadata.git.tracked is False


def test_git_metadata_provider_check_git_and_find_root_os_error(config, provider):
    node = TreeNode(path="/dummy/file.txt", ntype=NodeType.FILE)

    with patch("subprocess.run", side_effect=OSError):
        provider.enrich(node, config)

    assert provider._git_available is False
    assert node.metadata.git is not None


def test_git_metadata_provider_check_git_and_find_root_already_unavailable(provider):
    provider._git_available = False
    with patch("subprocess.run") as mock_run:
        provider._check_git_and_find_root(Path("/dummy/repo"))
        mock_run.assert_not_called()


def test_git_metadata_provider_path_not_in_root(config, provider):
    provider._repo_root = Path("/dummy/repo").resolve()
    provider._git_available = True

    node = TreeNode(path="/other_path/file.txt", ntype=NodeType.FILE)

    provider.enrich(node, config)
    assert node.metadata.git is not None
    assert node.metadata.git.tracked is False


def test_git_metadata_provider_is_inside_repo_no_repo_root(provider):
    provider._repo_root = None
    assert provider._is_inside_repo(Path("/dummy/repo")) is False


# --- Tests: Porcelain Status Parsing & Cache Loading ---
def test_git_metadata_provider_subprocess_error(config, provider):
    node = TreeNode(path="/dummy/file.txt", ntype=NodeType.FILE)

    def mock_subprocess_run(cmd, **kwargs):
        if "rev-parse" in cmd:
            mock = MagicMock()
            mock.stdout = "/dummy/repo"
            return mock
        raise subprocess.SubprocessError("Git error")

    with patch("subprocess.run", side_effect=mock_subprocess_run):
        provider.enrich(node, config)

    assert provider._git_available is True
    assert node.metadata.git is not None


def test_git_metadata_provider_load_git_status_cache_subprocess_error(config, provider):
    provider._repo_root = Path("/dummy/repo")

    with patch("subprocess.run", side_effect=subprocess.SubprocessError):
        provider._load_git_status_cache()

    assert provider._status_cache == {}


def test_git_metadata_provider_load_git_status_cache_no_repo_root(provider):
    provider._repo_root = None
    with patch("subprocess.run") as mock_run:
        provider._load_git_status_cache()
        mock_run.assert_not_called()


def test_git_metadata_provider_load_git_status_cache_short_lines(provider):
    provider._repo_root = Path("/dummy/repo").resolve()
    status_output = "M \n?? src/untracked.py\n"

    def mock_run(cmd, **kwargs):
        mock = MagicMock()
        mock.stdout = status_output
        return mock

    with patch("subprocess.run", side_effect=mock_run):
        provider._load_git_status_cache()

    assert "src/untracked.py" in provider._status_cache
    assert "" not in provider._status_cache


def test_git_metadata_provider_parse_all_git_statuses(config, provider):
    status_output = (
        " M src/main.py\n"
        "A  src/helper.py\n"
        " D src/old.py\n"
        "R  src/old.py -> src/new.py\n"
        " C src/copy.py\n"
        "UU src/conflict.py\n"
        "?? src/untracked.py\n"
        "!! src/ignored.py\n"
        " T src/typechanged.py\n"
    )

    def mock_run(cmd, **kwargs):
        mock = MagicMock()
        if "rev-parse" in cmd:
            mock.stdout = "/dummy/repo\n"
        elif "status" in cmd:
            mock.stdout = status_output
        return mock

    with patch("subprocess.run", side_effect=mock_run):
        node = TreeNode(path="/dummy/repo/src/main.py", ntype=NodeType.FILE)
        provider.enrich(node, config)
        assert node.metadata.git.tracked is True
        assert node.metadata.git.status == GitStatus.MODIFIED

    assert provider._status_cache["src/main.py"] == GitStatus.MODIFIED
    assert provider._status_cache["src/helper.py"] == GitStatus.ADDED
    assert provider._status_cache["src/old.py"] == GitStatus.DELETED
    assert provider._status_cache["src/new.py"] == GitStatus.RENAMED
    assert provider._status_cache["src/copy.py"] == GitStatus.COPIED
    assert provider._status_cache["src/conflict.py"] == GitStatus.UNMERGED
    assert provider._status_cache["src/untracked.py"] == GitStatus.UNTRACKED
    assert provider._status_cache["src/ignored.py"] == GitStatus.IGNORED

    # fallback
    assert provider._parse_status("XX") == GitStatus.CLEAN


def test_git_metadata_provider_load_git_status_cache_empty_lines_in_tracked(
    config, provider
):
    provider._repo_root = Path("/dummy/repo").resolve()

    def mock_run(cmd, **kwargs):
        mock = MagicMock()
        if "ls-files" in cmd:
            mock.stdout = 'src/main.py\n\n   \n""\nsrc/helper.py\n'
        elif "status" in cmd:
            mock.stdout = ""
        return mock

    with patch("subprocess.run", side_effect=mock_run):
        provider._load_git_status_cache()

    assert "src/main.py" in provider._tracked_paths
    assert "src/helper.py" in provider._tracked_paths

    assert "" not in provider._tracked_paths
    assert "   " not in provider._tracked_paths
    assert len(provider._tracked_paths) == 2


# --- Tests: File Metadata Enrichment ---
def test_git_metadata_provider_file_metadata_modified(config, provider):
    provider._git_available = True
    provider._repo_root = Path("/dummy/repo").resolve()
    provider._status_cache = {"src/main.py": GitStatus.MODIFIED}
    provider._tracked_paths = {"src/main.py"}

    node = TreeNode(path="/dummy/repo/src/main.py", ntype=NodeType.FILE)

    provider.enrich(node, config)

    assert node.metadata.git.tracked is True
    assert node.metadata.git.status == GitStatus.MODIFIED


def test_git_metadata_provider_file_metadata_clean(config, provider):
    provider._git_available = True
    provider._repo_root = Path("/dummy/repo").resolve()
    provider._tracked_paths = {"src/clean.py"}

    node = TreeNode(path="/dummy/repo/src/clean.py", ntype=NodeType.FILE)

    provider.enrich(node, config)

    assert node.metadata.git.tracked is True
    assert node.metadata.git.status == GitStatus.CLEAN


def test_git_metadata_provider_file_metadata_untracked(config, provider):
    provider._git_available = True
    provider._repo_root = Path("/dummy/repo").resolve()

    node = TreeNode(path="/dummy/repo/src/new.py", ntype=NodeType.FILE)

    provider.enrich(node, config)

    assert node.metadata.git.tracked is False
    assert node.metadata.git.status == GitStatus.UNTRACKED


def test_git_metadata_provider_file_metadata_ignored(config, provider):
    provider._git_available = True
    provider._repo_root = Path("/dummy/repo").resolve()
    provider._status_cache = {"src/cache.pyc": GitStatus.IGNORED}

    node = TreeNode(path="/dummy/repo/src/cache.pyc", ntype=NodeType.FILE)

    provider.enrich(node, config)

    assert node.metadata.git.tracked is False
    assert node.metadata.git.status == GitStatus.IGNORED


# --- Tests: Directory Metadata Enrichment ---
def test_git_metadata_provider_directory_has_changes(config, provider):
    provider._git_available = True
    provider._repo_root = Path("/dummy/repo").resolve()
    provider._status_cache = {"src/main.py": GitStatus.MODIFIED}

    node = TreeNode(path="/dummy/repo/src", ntype=NodeType.DIR)

    provider.enrich(node, config)

    assert node.metadata.git.has_sub_changes is True
    assert node.metadata.git.status == GitStatus.DIRTY


def test_git_metadata_provider_directory_clean(config, provider):
    provider._git_available = True
    provider._repo_root = Path("/dummy/repo").resolve()

    node = TreeNode(path="/dummy/repo/docs", ntype=NodeType.DIR)

    provider.enrich(node, config)

    assert node.metadata.git.has_sub_changes is False
    assert node.metadata.git.status == GitStatus.CLEAN


def test_git_metadata_provider_repo_root_detection(config, provider):
    provider._git_available = True
    provider._repo_root = Path("/dummy/repo").resolve()
    provider._status_cache = {"src/main.py": GitStatus.MODIFIED}

    node = TreeNode(path="/dummy/repo", ntype=NodeType.DIR)

    provider.enrich(node, config)

    assert node.metadata.git.is_repo_root is True
    assert node.metadata.git.has_sub_changes is True
