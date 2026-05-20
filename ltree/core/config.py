import argparse
import os
import pathspec
import re


class TreeConfig:
    def __init__(self):
        self.root_path: str = ""
        self.exclude_dirs: set = {
            '__pycache__', '.git', '.venv', 'env', 'venv', '.idea', 
            '.mypy_cache', 'python', 'media'
        }
        self.exclude_files: set = {'.DS_Store', 'error*'}
        self.exclude_exts: set = set()
        self.exclude_prefixes: set = set()
        self.added_items: set = set()
        self._exact_files: set = set()
        self._pattern_files: list = []

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

        self._prepare_patterns()

    def _prepare_patterns(self) -> None:
        self._exact_files.clear()
        self._pattern_files.clear()

        for pattern in self.exclude_files:
            if '*' in pattern or '?' in pattern:
                self._pattern_files.append(pattern)
            else:
                self._exact_files.add(pattern)
        
    @property
    def subtree_cache(self) -> dict:
        return self._subtree_cache
    
    def apply_args(self, args: argparse.Namespace) -> None:
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
        
        if args.output != "-":
            self.use_color = False
        else:
            self.use_color = args.color
        self.show_size = args.show_size
        self.human_readable = args.human_readable
        self.show_all = args.show_all
        self.folders_only = args.folders_only
        self.full_path = args.full_path
        self.dirs_first = args.dirs_first
        self.show_ellipsis = args.show_ellipsis
        
        self._prepare_patterns()

    def load_gitignore(self, root_path: str):
        if not self.use_gitignore:
            return

        gitignore_path = os.path.join(root_path, '.gitignore')
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    self.gitignore_spec = pathspec.PathSpec.from_lines(
                        'gitignore', f.readlines()
                )
            except Exception as e:
                print(f"Warning: Could not load .gitignore: {e}")
