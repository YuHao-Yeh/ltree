# ltree/core/metadata/__init__.py
from ltree.core.metadata.base import MetadataProvider
from ltree.core.metadata.registry import MetadataPipeline, get_default_pipeline
from ltree.core.metadata.filesystem import FilesystemMetadataProvider
from ltree.core.metadata.code import CodeMetadataProvider
from ltree.core.metadata.git import GitMetadataProvider
from ltree.core.metadata.time import TimeMetadataProvider
from ltree.core.metadata.project import ProjectMetadataProvider

__all__ = [
    "MetadataProvider",
    "MetadataPipeline",
    "get_default_pipeline",
    "FilesystemMetadataProvider",
    "GitMetadataProvider",
    "CodeMetadataProvider",
    "TimeMetadataProvider",
    "ProjectMetadataProvider",
]
