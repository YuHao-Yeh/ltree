# ltree/tree/scanner/context.py
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ltree.config.config import TreeConfig

if TYPE_CHECKING:
    from os import PathLike


def _relative_path(target_path: str | PathLike[str], base_path: str | PathLike[str]):
    abs_target = os.path.abspath(target_path)
    abs_base = os.path.abspath(base_path)

    if abs_target == abs_base:
        return "."

    rel = os.path.relpath(abs_target, abs_base)

    return rel.replace("\\", "/")


@dataclass(slots=True)
class FilterContext:
    path: Path
    is_dir: bool
    config: TreeConfig
    name: str = field(init=False)
    rel_path: str = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.path.name
        self.rel_path = _relative_path(self.path, self.config.root_path)
