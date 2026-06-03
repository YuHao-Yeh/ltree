# ltree/serializers/types.py
from __future__ import annotations

from typing import Any, TypedDict


class SerializedNode(TypedDict):
    name: str
    path: str
    type: str

    metadata: dict[str, Any]  # TODO: dict[str, Any] -> MetadataDict(TypedDict)

    stats: dict[str, Any]  # TODO: dict[str, Any] -> StatsDict(TypedDict)

    is_truncated: bool

    children: list["SerializedNode"]
