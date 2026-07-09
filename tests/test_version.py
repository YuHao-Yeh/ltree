# tests/test_version.py
import importlib.metadata
from pathlib import Path
from unittest.mock import patch, mock_open

from ltree import _get_version

meta_version = "importlib.metadata.version"


def test_get_version_from_installed_metadata():
    with patch(meta_version, return_value="9.9.9"):
        assert _get_version() == "9.9.9"


def test_get_version_fallback_to_pyproject_toml():
    mock_toml_content = """
    [project]
    name = "ltree-cli"
    version_info = "malformed-no-quotes-or-mismatched-key"
    version = "1.2.3"
    """

    with patch(meta_version, side_effect=importlib.metadata.PackageNotFoundError):
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_toml_content)):
                assert _get_version() == "1.2.3"


def test_get_version_fallback_to_pyproject_toml_malformed_version():
    mock_toml_content = """
    [project]
    name = "ltree-cli"
    description = "A directory tree viewer."
    """

    with patch(meta_version, side_effect=Exception("Metadata Error")):
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_toml_content)):
                assert _get_version() == "0.3.0"


def test_get_version_fallback_to_static_default():
    with patch(meta_version, side_effect=Exception("Generic Error")):
        with patch.object(Path, "exists", return_value=False):
            assert _get_version() == "0.3.0"


def test_get_version_fallback_climbing_exception_handling():
    with patch(meta_version, side_effect=importlib.metadata.PackageNotFoundError):
        with patch.object(
            Path, "resolve", side_effect=OSError("Disk resolution error")
        ):
            assert _get_version() == "0.3.0"
