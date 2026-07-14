# ltree/metadata/__init__.py
from ltree.metadata.base import MetadataProvider
from ltree.metadata.providers.code import CodeMetadataProvider
from ltree.metadata.providers.filesystem import FilesystemMetadataProvider
from ltree.metadata.providers.git import GitMetadataProvider
from ltree.metadata.providers.project import ProjectMetadataProvider
from ltree.metadata.providers.time import TimeMetadataProvider
from ltree.metadata.registry import MetadataPipeline, get_default_pipeline


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
