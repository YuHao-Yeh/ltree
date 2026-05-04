import argparse

class TreeConfig:
    def __init__(self):
        self.exclude_dirs: set = {'__pycache__', '.git', '.venv', 'env', 'venv', '.idea', '.mypy_cache', 'python', 'media'}
        self.exclude_files: set = {'.DS_Store', 'error*', 'tree.txt'}
        self.exclude_exts: set = set()
        self.exclude_prefixes: set = set()
        self._exact_files = set()
        self._pattern_files = []

        self._subtree_cache: dict = {}
        self.folders_only: bool = False
        self.dirs_first: bool = False
        self.use_color: bool = False
        self.show_ellipsis: bool = False

        self._prepare_patterns()

    def _prepare_patterns(self):
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
    
    def apply_args(self, args: argparse) -> None:
        for dir in args.ex_dirs:
            self.exclude_dirs.add(dir)
        for file in args.ex_files:
            self.exclude_files.add(file)
        
        for dir in args.add_dirs:
            self.exclude_dirs.discard(dir)
        for file in args.add_files:
            self.exclude_files.discard(file)
        
        for dir in args.ex_ext:
            self.exclude_exts.add(dir)
        for dir in args.ex_prefix:
            self.exclude_prefixes.add(dir)
        
        self.folders_only = args.folders_only
        self.dirs_first = args.dirs_first
        self.use_color = not args.no_color
        self.show_ellipsis = args.show_ellipsis
        
        self._prepare_patterns()
