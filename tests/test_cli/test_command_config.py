# tests/test_cli/test_command_config.py
import argparse
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from ltree.cli.commands.config import (
    run_config_show,
    run_config_locate,
    run_config_validate,
)

config_path = "ltree.config.config"


# ======================================================================= #
# Tests: run_config_show()
# ======================================================================= #
def test_run_config_show_output(tmp_path, capsys):
    rc_file = tmp_path / ".ltreerc"
    rc_data = {
        "theme": "nerd",
        "color": True,
        "size": True,
    }
    rc_file.write_text(json.dumps(rc_data), encoding="utf-8")

    args = argparse.Namespace(start_path=str(tmp_path))
    run_config_show(args)

    captured = capsys.readouterr()

    assert "Active Configuration" in captured.out
    assert (
        "============================================================" in captured.out
    )

    assert "theme" in captured.out
    assert "nerd" in captured.out
    assert "use_color" in captured.out


# ======================================================================= #
# Tests: run_config_locate()
# ======================================================================= #
@pytest.mark.parametrize(
    "filename",
    [
        ".ltreerc",
        "pyproject.toml",
    ],
)
def test_run_config_locate_found_rc(tmp_path, filename, capsys):
    rc_file = tmp_path / filename
    rc_file.write_text("{}", encoding="utf-8")

    real_exists = Path.exists

    def mock_exists(self):
        if tmp_path in self.parents or self == tmp_path or self == rc_file:
            return real_exists(self)
        return False

    args = argparse.Namespace(start_path=str(tmp_path))

    with patch.object(Path, "exists", autospec=True, side_effect=mock_exists):
        run_config_locate(args)

    captured = capsys.readouterr()
    assert "Configuration files:" in captured.out
    assert str(rc_file) in captured.out


def test_run_config_locate_not_found(tmp_path, capsys):
    with patch.object(Path, "exists", return_value=False):
        args = argparse.Namespace(start_path=str(tmp_path))
        run_config_locate(args)

    captured = capsys.readouterr()
    assert "No configuration files found." in captured.out


# ======================================================================= #
# Tests: run_config_validate()
# ======================================================================= #
def test_run_config_validate_success(tmp_path, capsys):
    rc_file = tmp_path / ".ltreerc"
    rc_file.write_text('{"theme": "emoji", "color": false}', encoding="utf-8")

    real_exists = Path.exists

    def mock_exists(self):
        if tmp_path in self.parents or self == tmp_path or self == rc_file:
            return real_exists(self)
        return False

    args = argparse.Namespace(start_path=str(tmp_path))

    with patch.object(Path, "exists", autospec=True, side_effect=mock_exists):
        run_config_validate(args)

    captured = capsys.readouterr()
    assert f"✓ {rc_file}" in captured.out


def test_run_config_validate_failure(tmp_path, capsys):
    rc_file = tmp_path / ".ltreerc"
    rc_file.write_text('{"theme": "emoji", malformed_json}', encoding="utf-8")

    real_exists = Path.exists

    def mock_exists(self):
        if tmp_path in self.parents or self == tmp_path or self == rc_file:
            return real_exists(self)
        return False

    args = argparse.Namespace(start_path=str(tmp_path))

    with patch.object(Path, "exists", autospec=True, side_effect=mock_exists):
        with patch(
            f"{config_path}.TreeConfig.load_config_file",
            side_effect=ValueError("Invalid parsing configurations"),
        ):
            run_config_validate(args)

    captured = capsys.readouterr()
    assert f"✗ {rc_file}" in captured.out
    assert "Invalid parsing configurations" in captured.out


def test_run_config_validate_not_found(tmp_path, capsys):
    with patch.object(Path, "exists", return_value=False):
        args = argparse.Namespace(start_path=str(tmp_path))
        run_config_validate(args)

    captured = capsys.readouterr()
    assert "No configuration files found." in captured.out
