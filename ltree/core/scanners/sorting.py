# ltree/core/scanner/sorting.py
from typing import TYPE_CHECKING

from ltree.core.config import TreeConfig

if TYPE_CHECKING:
    import os


def sort_entries(
    entries: list["os.DirEntry"], config: TreeConfig
) -> list["os.DirEntry"]:
    return sorted(
        entries,
        key=lambda e: (
            not e.is_dir() if config.dirs_first else False,
            e.name.lower(),
        ),
    )
