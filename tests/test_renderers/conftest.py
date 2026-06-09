# tests/test_renderers/conftest.py
import pytest
from ltree.core.models import TreeNode, NodeType, Stats
from ltree.core.config import TreeConfig
from ltree.core.metadata.models import (
    CodeMetadata,
    FilesystemMetadata,
    GitMetadata,
    GitStatus,
    ProjectMetadata,
    TimeMetadata,
)
from ltree.serializers.tree import TreeSerializer
from ltree.core.scanners.aggregation import aggregate_tree


# ======================================================================= #
# Fixture
# ======================================================================= #
# root/
# ├── src/              (dir)
# │   └── main.py       (file, 1536 bytes)
# ├── truncated_dir/    (dir)
# │   └── ... (0 dirs, 2 files, 0 bytes)
# └── README.md         (file, 500 bytes)
# ======================================================================= #
@pytest.fixture
def sample_tree() -> TreeNode:
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.metadata.fs.permissions = "drwxrwxrwx"
    root.metadata.git = GitMetadata(True, GitStatus.MODIFIED, True, True)

    src = TreeNode(path="root/src", ntype=NodeType.DIR)
    src.metadata.fs.permissions = "drwxrwxrwx"
    src.metadata.git = GitMetadata(True, GitStatus.ADDED, False, True)
    src.metadata.project = ProjectMetadata("Python", "ltree", "0.1.0")
    src.metadata.time = TimeMetadata(relative_modified="yesterday")
    src.metadata.code = CodeMetadata(None, True)
    main_py = TreeNode(path="root/src/main.py", ntype=NodeType.FILE)
    main_py.metadata.fs = FilesystemMetadata(
        permissions="-rw-r--r--",
        size=1536,  # 1.5 KB
    )
    main_py.metadata.git = GitMetadata(True, GitStatus.ADDED)
    main_py.metadata.code = CodeMetadata("Python", True)
    src.children.append(main_py)
    root.children.append(src)

    truncated_dir = TreeNode(
        path="root/truncated_dir", ntype=NodeType.DIR, is_truncated=True
    )
    truncated_dir.stats = Stats(hidden_files=2, hidden_size=0)
    truncated_dir.metadata.fs.permissions = "drwxrwxrwx"
    truncated_dir.metadata.git = GitMetadata(False, GitStatus.UNTRACKED)
    root.children.append(truncated_dir)

    readme = TreeNode(path="root/README.md", ntype=NodeType.FILE)
    readme.metadata.fs = FilesystemMetadata(permissions="-rw-rw-rw-", size=500)
    readme.metadata.git = GitMetadata(True, GitStatus.CLEAN)
    root.children.append(readme)

    aggregate_tree(root)

    return root


@pytest.fixture
def sample_serialized_node(sample_tree):
    config = TreeConfig()
    config.show_size = True
    config.show_permission = True
    config.show_project = True
    config.show_git = True
    config.show_time = True
    config.human_readable = True

    serializer = TreeSerializer(config)
    return serializer.serialize(sample_tree)
