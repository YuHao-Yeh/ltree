# ltree/tree/scanners/sorting.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import DirEntry
    from ltree.config.config import TreeConfig


def sort_entries(entries: list[DirEntry], config: TreeConfig) -> list[DirEntry]:
    return sorted(
        entries,
        key=lambda e: (
            not e.is_dir() if config.dirs_first else False,
            e.name.lower(),
        ),
    )
