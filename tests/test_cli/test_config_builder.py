# tests/test_cli/test_config_builder.py
import argparse
import re
from ltree.cli.config_builder import build_config
from ltree.core.config import TreeConfig


def test_build_config_standard_args():
    args = argparse.Namespace(
        start_path=".",
        output="-",
        format="text",
        theme="nerd",
        color=True,
        show_permission=False,
        show_git=False,
        show_size=True,
        human_readable=True,
        show_mtime=False,
        show_code=True,
        show_project=True,
        show_all=True,
        folders_only=True,
        dirs_first=True,
        full_path=True,
        show_ellipsis=True,
        gitignore=True,
        regex_exclude=["temp_\\d+"],
        add_dirs=["__pycache__"],
        add_files=["extra.txt"],
        ex_dirs=["build"],
        ex_files=["*.log"],
        ex_ext=[".tmp"],
        ex_prefix=["test_"],
    )

    config = build_config(args)

    assert isinstance(config, TreeConfig)
    assert config.theme == "nerd"
    assert config.use_color is True
    assert config.show_permission is False
    assert config.show_git is False
    assert config.show_size is True
    assert config.human_readable is True
    assert config.show_time is False
    assert config.show_code is True
    assert config.show_project is True
    assert config.show_all is True
    assert config.folders_only is True
    assert config.dirs_first is True
    assert config.full_path is True
    assert config.show_ellipsis is True
    assert config.use_gitignore is True

    # regex
    assert len(config.regex_exclude_patterns) == 1
    assert isinstance(config.regex_exclude_patterns[0], re.Pattern)

    # inclusion and exclusion
    assert "__pycache__" in config.added_items
    assert "build" in config.exclude_dirs
    assert "*.log" in config.exclude_files
    assert ".tmp" in config.exclude_exts
    assert "test_" in config.exclude_prefixes

    args.output = "out.txt"
    config = build_config(args)
    assert not config.use_color


def test_build_config_with_invalid_regex(capsys):
    args = argparse.Namespace(
        start_path="-",
        output="-",
        format="text",
        theme=None,
        color=False,
        show_permission=True,
        show_git=True,
        show_size=False,
        human_readable=False,
        show_mtime=True,
        show_code=False,
        show_project=False,
        show_all=False,
        folders_only=False,
        dirs_first=False,
        full_path=False,
        show_ellipsis=False,
        gitignore=True,
        regex_exclude=["[invalid-regex+"],
        add_dirs=[],
        add_files=[],
        ex_dirs=[],
        ex_files=[],
        ex_ext=[],
        ex_prefix=[],
    )

    config = build_config(args)
    captured = capsys.readouterr()

    assert "Warning: Invalid regex" in captured.err
    assert len(config.regex_exclude_patterns) == 0
