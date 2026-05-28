# ltree/core/metadata/registry.py
from typing import TYPE_CHECKING

from ltree.core.metadata.base import MetadataProvider
from ltree.core.metadata.filesystem import FilesystemMetadataProvider
from ltree.core.metadata.code import CodeMetadataProvider
from ltree.core.metadata.git import GitMetadataProvider
from ltree.core.metadata.time import TimeMetadataProvider
from ltree.core.metadata.project import ProjectMetadataProvider

from ltree.core.config import TreeConfig

if TYPE_CHECKING:
    from ltree.core.models import TreeNode


class MetadataPipeline:
    def __init__(self):
        self._providers: list[MetadataProvider] = []

    def register(self, provider: MetadataProvider) -> "MetadataPipeline":
        self._providers.append(provider)
        return self

    def execute(self, path: str, node: "TreeNode", config: TreeConfig) -> None:
        # todo: remove path from param
        for provider in self._providers:
            provider.enrich(node, config)


def get_default_pipeline(config: TreeConfig) -> MetadataPipeline:
    pipeline = MetadataPipeline()

    # 1. Basic file system attributes (required)
    pipeline.register(FilesystemMetadataProvider())

    # 2. Code language type identification (lightweight, pre-loaded)
    pipeline.register(CodeMetadataProvider())

    # 3. Project version configuration file parsing (lightweight, pre-loaded)
    pipeline.register(ProjectMetadataProvider())

    # 4. Time-modified information (lightweight, pre-loaded)
    pipeline.register(TimeMetadataProvider())

    # 5. Git status information (loaded if gitignore enabled and not explicitly disabled)
    if config.use_gitignore:
        pipeline.register(GitMetadataProvider())

    return pipeline
