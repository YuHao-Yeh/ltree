# tests/test_serialization/test_tree.py
from pathlib import Path

from ltree.tree.models import TreeNode, NodeType, Stats
from ltree.metadata.models import (
    MetadataContainer,
    FilesystemMetadata,
    GitMetadata,
    GitStatus,
    CodeMetadata,
    ProjectMetadata,
    TimeMetadata,
)
from ltree.serialization.tree import TreeSerializer


# ======================================================================= #
# Tests: TreeSerializer
# ======================================================================= #
def test_tree_serializer_full_metadata_serialization():
    metadata = MetadataContainer(
        fs=FilesystemMetadata(
            permissions="-rwxr-xr-x",
            is_executable=True,
            is_symlink=False,
            extension=".py",
            size=1024,
        ),
        git=GitMetadata(
            tracked=True,
            status=GitStatus.MODIFIED,
            is_repo_root=False,
            has_sub_changes=False,
        ),
        code=CodeMetadata(language="python", is_source_code=True),
        project=ProjectMetadata(
            project_type="Python (PEP 518)", name="ltree-cli", version="0.2.0"
        ),
        time=TimeMetadata(
            modified_timestamp=1779888000.0,
            modified_iso="2026-05-26T12:00:00Z",
            relative_modified="3 days ago",
        ),
    )

    node = TreeNode(
        path=Path("src/main.py"),
        ntype=NodeType.FILE,
        metadata=metadata,
        stats=Stats(visible_dirs=0, visible_files=1),
    )

    serializer = TreeSerializer()
    res = serializer.serialize(node)

    # 1. Verify basic attribute
    assert res["name"] == "main.py"
    assert res["path"] == str(Path("src/main.py"))
    assert res["type"] == "file"
    assert res["is_truncated"] is False

    # 2. Verify metadata serialization
    meta = res["metadata"]
    assert meta["fs"]["size"] == 1024
    assert meta["fs"]["is_executable"] is True

    assert meta["git"]["status"] == "modified"
    assert meta["git"]["tracked"] is True

    assert meta["code"]["language"] == "python"
    assert meta["project"]["version"] == "0.2.0"
    assert meta["time"]["modified_timestamp"] == 1779888000.0


def test_tree_serializer_nested_tree_recursion():
    root = TreeNode(path="root", ntype=NodeType.DIR)
    child = TreeNode(path="root/child.txt", ntype=NodeType.FILE)
    root.stats.visible_files += 1
    root.children.append(child)

    serializer = TreeSerializer()
    res = serializer.serialize(root)

    assert res["name"] == "root"
    assert res["type"] == "directory"
    assert res["stats"]["visible_files"] == 1
    assert res["stats"]["total_files"] == 1
    assert len(res["children"]) == 1
    assert res["children"][0]["name"] == "child.txt"
    assert res["children"][0]["type"] == "file"


def test_tree_serializer_partial_metadata():
    node = TreeNode(path="temp.txt", ntype=NodeType.FILE)
    node.metadata = MetadataContainer()

    serializer = TreeSerializer()
    res = serializer.serialize(node)

    assert res["metadata"] == {}

    node.metadata = MetadataContainer(git=GitMetadata(tracked=False))
    res = serializer.serialize(node)

    assert res["metadata"]["git"]["status"] is None
