# ltree/sserializers/tree.py
from dataclasses import asdict

from ltree.core.models import TreeNode, Stats
from ltree.core.metadata.models import MetadataContainer
from ltree.serializers.base import Serializer
from ltree.serializers.types import SerializedNode


def _serialize_metadata(metadata: MetadataContainer) -> dict:
    result = {}

    if metadata.fs:
        result["fs"] = asdict(metadata.fs)

    if metadata.git:
        git_data = asdict(metadata.git)

        if metadata.git.status:
            git_data["status"] = metadata.git.status.value

        result["git"] = git_data

    if metadata.code:
        result["code"] = asdict(metadata.code)

    if metadata.project:
        result["project"] = asdict(metadata.project)

    if metadata.time:
        result["time"] = asdict(metadata.time)

    return result


def _serialize_stats(stats: Stats) -> dict[str, int]:
    return {
        "visible_dirs": stats.visible_dirs,
        "visible_files": stats.visible_files,
        "hidden_dirs": stats.hidden_dirs,
        "hidden_files": stats.hidden_files,
        "hidden_size": stats.hidden_size,
        "total_dirs": stats.total_dirs,
        "total_files": stats.total_files,
    }


class TreeSerializer(Serializer):
    def serialize(self, node: TreeNode) -> SerializedNode:
        return {
            "name": node.name,
            "path": str(node.path),
            "type": node.ntype.value,
            "metadata": _serialize_metadata(node.metadata),
            "stats": _serialize_stats(node.stats),
            "is_truncated": node.is_truncated,
            "children": [self.serialize(child) for child in node.children],
        }
