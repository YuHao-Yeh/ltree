# ltree/core/metadata/time.py
import os
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from ltree.core.metadata.base import MetadataProvider
from ltree.core.metadata.models import TimeMetadata

if TYPE_CHECKING:
    from ltree.core.config import TreeConfig
    from ltree.core.models import TreeNode


class TimeMetadataProvider(MetadataProvider):
    def _get_relative_time(self, mtime: float) -> str:
        diff = time.time() - mtime
        if diff < 60:
            return "just now"
        elif diff < 3600:
            return f"{int(diff // 60)}m ago"
        elif diff < 86400:
            return f"{int(diff // 3600)}h ago"
        elif diff < 2592000:  # 30 days = 60 * 60 * 24* 30
            days = int(diff // 86400)
            return "yesterday" if days == 1 else f"{days}d ago"
        else:
            dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
            return dt.strftime("%Y-%m-%d")

    def enrich(self, node: "TreeNode", config: "TreeConfig") -> None:
        try:
            st = os.lstat(node.path)
            mtime = st.st_mtime
            node.metadata.time = TimeMetadata(
                modified_timestamp=mtime,
                modified_iso=datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
                relative_modified=self._get_relative_time(mtime),
            )
        except OSError:
            node.metadata.time = TimeMetadata(
                modified_timestamp=0.0, modified_iso="", relative_modified="unknown"
            )
