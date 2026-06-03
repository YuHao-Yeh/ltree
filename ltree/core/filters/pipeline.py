# ltree/core/filters/pipeline.py
from typing import TYPE_CHECKING

from ltree.core.filters.depth import MaxDepthFilter
from ltree.core.filters.folders import FoldersOnlyFilter
from ltree.core.filters.sorting import SortFilter

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.filters.base import TreeFilter
    from ltree.core.models import TreeNode


class FilterPipeline:
    def __init__(self, filters: list["TreeFilter"] | None = None):
        self._filters = filters or []

    def register(self, filter: "TreeFilter") -> "FilterPipeline":
        self._filters.append(filter)
        return self

    def apply(self, root: "TreeNode") -> "TreeNode":
        """Filters mutate the tree in-place and return root."""
        current = root

        for filter in self._filters:
            current = filter.apply(current)

        return current


def get_default_filter_pipeline(config: "TreeConfig", max_depth: int | None):
    pipeline = FilterPipeline()

    # 1. Depth filter
    if max_depth is not None:
        pipeline.register(MaxDepthFilter(max_depth))

    # 2. Floders filter
    if config.folders_only:
        pipeline.register(FoldersOnlyFilter())

    # 3. Tree sort
    pipeline.register(SortFilter(config.dirs_first))

    return pipeline
