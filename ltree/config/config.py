# ltree/config/config.py
from __future__ import annotations

import fnmatch
import json
import logging
import os
import pathspec
import sys
from dataclasses import dataclass, field

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


FORMATS: list[str] = [
    "text",
    "json",
    "md",
    "markdown",
    "block",
    "rich",
    "yaml",
    "html",
    "graphviz",
]
THEMES: list[str] = ["nerd", "emoji", "none"]

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MatchRules:
    literals: set[str] = field(default_factory=set)
    globs: set[str] = field(default_factory=set)

    def add_pattern(self, pattern: str) -> None:
        pat = pattern.replace("\\", "/").strip("/")
        if not pat:
            return

        if any(ch in pat for ch in "*?[]"):
            self.globs.add(pat)
        else:
            self.literals.add(pat)

    def matches(self, rel_path: str, name: str) -> bool:
        # 1. Literal check
        for lit in self.literals:
            if "/" in lit:
                if rel_path == lit:
                    return True
            else:
                if name == lit:
                    return True

        # 2. Glob check
        for glob in self.globs:
            if "/" in glob:
                if fnmatch.fnmatch(rel_path, glob):
                    return True
                if glob.startswith("**/"):
                    remainder = glob[3:]
                    if fnmatch.fnmatch(rel_path, remainder):
                        return True
                if glob.endswith("/**"):
                    parent_dir = glob[:-3]
                    if fnmatch.fnmatch(rel_path, parent_dir):
                        return True
            else:
                if fnmatch.fnmatch(name, glob):
                    return True

        return False


# @dataclass(slots=True)
class TreeConfig:
    def __init__(self):
        self.root_path: str = ""

        self.exclude: MatchRules = MatchRules()
        self.include: MatchRules = MatchRules()

        default_exclude_literals = {
            "__pycache__",
            ".git",
            ".venv",
            "env",
            "venv",
            ".idea",
            ".mypy_cache",
            "python",
            "media",
            ".DS_Store",
        }
        for lit in default_exclude_literals:
            self.exclude.add_pattern(lit)
        self.exclude.add_pattern("error*")

        self.use_gitignore: bool = True
        self.gitignore_spec: pathspec.PathSpec | None = None
        self.regex_exclude_patterns: list = []

        self._subtree_cache: dict = {}

        self.use_color: bool = False
        self.show_size: bool = False
        self.human_readable: bool = False
        self.show_all: bool = False
        self.folders_only: bool = False
        self.full_path: bool = False
        self.dirs_first: bool = False
        self.show_ellipsis: bool = False
        self.theme: str = "emoji"

        self.show_permission: bool = True
        self.show_git: bool = True
        self.show_time: bool = True
        self.show_code: bool = False
        self.show_project: bool = True

    def load_config_file(self, start_path: str) -> None:
        search_path = os.path.abspath(start_path)

        while True:
            ltreerc_path = os.path.join(search_path, ".ltreerc")
            pyproject_path = os.path.join(search_path, "pyproject.toml")

            # 1. .ltreerc (JSON)
            if os.path.exists(ltreerc_path):
                try:
                    with open(ltreerc_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._apply_dict_config(data)
                        return
                except Exception as e:
                    logger.warning("Failed to parse .ltreerc: %s", e)

            # 2. pyproject.toml [tool.ltree]
            if os.path.exists(pyproject_path):
                if tomllib is None:
                    logger.warning(
                        "pyproject.toml found but cannot be parsed because 'tomli' is not installed (required for Python < 3.11).",
                    )
                else:
                    try:
                        with open(pyproject_path, "rb") as f:
                            data = tomllib.load(f)
                            ltree_data = data.get("tool", {}).get("ltree", {})
                            if ltree_data:
                                self._apply_dict_config(ltree_data)
                                return
                    except Exception as e:
                        logger.warning("Failed to parse pyproject.toml: %s", e)

            parent = os.path.dirname(search_path)
            if parent == search_path:
                break
            search_path = parent

    def _apply_dict_config(self, config_dict: dict):
        # --- 1. Boolean Values and Strings ---
        if "theme" in config_dict:
            self.theme = config_dict["theme"]
        if "color" in config_dict:
            self.use_color = config_dict["color"]
        if "size" in config_dict:
            self.show_size = config_dict["size"]
        if "human" in config_dict:
            self.human_readable = config_dict["human"]
        if "all" in config_dict:
            self.show_all = config_dict["all"]
        if "dirs_only" in config_dict:
            self.folders_only = config_dict["dirs_only"]
        if "full_path" in config_dict:
            self.full_path = config_dict["full_path"]
        if "dirs_first" in config_dict:
            self.dirs_first = config_dict["dirs_first"]
        if "show_ellipsis" in config_dict:
            self.show_ellipsis = config_dict["show_ellipsis"]
        if "no_ignore" in config_dict:
            self.use_gitignore = not config_dict["no_ignore"]

        # --- 2. Exclusion and Inclusion Lists ---
        if "exclude" in config_dict and isinstance(config_dict["exclude"], list):
            for d in config_dict["exclude"]:
                self.exclude.add_pattern(d)
        if "include" in config_dict and isinstance(config_dict["include"], list):
            for d in config_dict["include"]:
                self.include.add_pattern(d)

    def load_gitignore(self, root_path: str):
        if not self.use_gitignore:
            return

        gitignore_path = os.path.join(root_path, ".gitignore")
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    self.gitignore_spec = pathspec.PathSpec.from_lines(
                        "gitignore", f.readlines()
                    )
            except Exception as e:
                logger.warning("Could not load .gitignore: %s", e)
