# ltree/core/config.py
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import pathspec
import re
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
                    parent_dir = glob[:-3]  # 取出 'src'
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
        # ------------------------------------------------------------- #
        # legacy vars:
        self.exclude_dirs: set = {
            "__pycache__",
            ".git",
            ".venv",
            "env",
            "venv",
            ".idea",
            ".mypy_cache",
            "python",
            "media",
        }
        self.exclude_files: set = {".DS_Store", "error*"}
        self.exclude_exts: set = set()
        self.exclude_prefixes: set = set()
        self.added_items: set = set()
        self._exact_files: set = set()
        self._pattern_files: list = []
        # ------------------------------------------------------------- #

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

        self._prepare_patterns()  # legacy: ready to remove

    def _prepare_patterns(self) -> None:
        self._exact_files.clear()
        self._pattern_files.clear()

        for pattern in self.exclude_files:
            if "*" in pattern or "?" in pattern:
                self._pattern_files.append(pattern)
            else:
                self._exact_files.add(pattern)

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
                    print(f"Warning: Failed to parse .ltreerc: {e}", file=sys.stderr)

            # 2. pyproject.toml [tool.ltree]
            if os.path.exists(pyproject_path):
                if tomllib is None:
                    print(
                        "Warning: pyproject.toml found but cannot be parsed because 'tomli' is not installed (required for Python < 3.11).",
                        file=sys.stderr,
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
                        print(
                            f"Warning: Failed to parse pyproject.toml: {e}",
                            file=sys.stderr,
                        )

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
        # legacy part:
        if "ex_dirs" in config_dict and isinstance(config_dict["ex_dirs"], list):
            self.exclude_dirs.update(config_dict["ex_dirs"])

        if "ex_files" in config_dict and isinstance(config_dict["ex_files"], list):
            self.exclude_files.update(config_dict["ex_files"])

        if "ex_ext" in config_dict and isinstance(config_dict["ex_ext"], list):
            self.exclude_exts.update(config_dict["ex_ext"])

        if "ex_prefix" in config_dict and isinstance(config_dict["ex_prefix"], list):
            self.exclude_prefixes.update(config_dict["ex_prefix"])

        if "add_dirs" in config_dict and isinstance(config_dict["add_dirs"], list):
            for d in config_dict["add_dirs"]:
                self.exclude_dirs.discard(d)
                self.added_items.add(d)

        if "add_files" in config_dict and isinstance(config_dict["add_files"], list):
            for f in config_dict["add_files"]:
                self.exclude_files.discard(f)
                self.added_items.add(f)
        # ------------------------------------------------------------- #
        # new:
        if "ex_dirs" in config_dict and isinstance(config_dict["ex_dirs"], list):
            for d in config_dict["ex_dirs"]:
                self.exclude.add_pattern(d + "/")
        if "ex_files" in config_dict and isinstance(config_dict["ex_files"], list):
            for f in config_dict["ex_files"]:
                self.exclude.add_pattern(f)

        if "add_dirs" in config_dict and isinstance(config_dict["add_dirs"], list):
            for d in config_dict["add_dirs"]:
                self.include.add_pattern(d + "/")
        if "add_files" in config_dict and isinstance(config_dict["add_files"], list):
            for f in config_dict["add_files"]:
                self.include.add_pattern(f)

    # legacy func
    def apply_args(self, args: argparse.Namespace) -> None:
        # preset profile
        start_path = getattr(args, "start_path", ".")
        self.load_config_file(start_path)

        # gitignore
        self.use_gitignore = not args.no_ignore

        # regex
        for pattern in args.regex_exclude:
            try:
                self.regex_exclude_patterns.append(re.compile(pattern))
            except re.error as e:
                print(f"Warning: Invalid regex '{pattern}': {e}")

        # include
        for dir in args.add_dirs:
            self.exclude_dirs.discard(dir)
            self.added_items.add(dir)
        for file in args.add_files:
            self.exclude_files.discard(file)
            self.added_items.add(file)

        # exclude
        for dir in args.ex_dirs:
            self.exclude_dirs.add(dir)
        for file in args.ex_files:
            self.exclude_files.add(file)

        # prefix, ext
        for ext in args.ex_ext:
            self.exclude_exts.add(ext)
        for pre in args.ex_prefix:
            self.exclude_prefixes.add(pre)

        # merge CLI parameters
        if args.color:
            self.use_color = True
        if args.show_size:
            self.show_size = True
        if args.human_readable:
            self.human_readable = True
        if args.show_all:
            self.show_all = True
        if args.folders_only:
            self.folders_only = True
        if args.full_path:
            self.full_path = True
        if args.dirs_first:
            self.dirs_first = True
        if args.show_ellipsis:
            self.show_ellipsis = True

        if any(arg in sys.argv for arg in ["--theme"]):
            self.theme = args.theme

        if args.output != "-":
            self.use_color = False

        self._prepare_patterns()

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
                print(f"Warning: Could not load .gitignore: {e}")
