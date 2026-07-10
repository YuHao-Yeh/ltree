# ltree/core/scanners/models.py
from dataclasses import dataclass, field
from pathlib import Path

from ltree.core.config import TreeConfig
from ltree.core.utils import relative_path


@dataclass(slots=True)
class FilterContext:
    path: Path
    is_dir: bool
    config: TreeConfig
    name: str = field(init=False)
    rel_path: str = field(init=False)

    def __post_init__(self):
        self.name = self.path.name
        self.rel_path = relative_path(self.path, self.config.root_path)
