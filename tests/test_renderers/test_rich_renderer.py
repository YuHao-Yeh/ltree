# tests/test_renderers/test_rich_renderer.py
import io
import os
import pytest
from ltree.core.models import TreeNode, Stats, NodeType
from ltree.core.config import TreeConfig
from ltree.renderers.rich_renderer import RichRenderer
from ltree.serializers import TreeSerializer


# ======================================================================= #
# Fixtures
# ======================================================================= #
@pytest.fixture
def base_config():
    config = TreeConfig()
    config.theme = "none"
    config.use_color = False
    return config


@pytest.fixture
def sample_tree():
    # root/
    # ├── src/
    # │   └── main.py (1024 bytes)
    # └── README.md (500 bytes)
    root = TreeNode(path="root", ntype=NodeType.DIR)

    src = TreeNode(path="root/src", ntype=NodeType.DIR)
    main_py = TreeNode(path="root/src/main.py", ntype=NodeType.FILE)
    main_py.size = 1024
    src.children.append(main_py)

    readme = TreeNode(path="root/README.md", ntype=NodeType.FILE)
    readme.size = 500

    root.children.extend([src, readme])
    return TreeSerializer().serialize(root)


# ======================================================================= #
# Test: _build_node_label
# ======================================================================= #
def test_build_node_label_basic(base_config):
    base_config.theme = "emoji"
    renderer = RichRenderer(base_config)

    dir_node = TreeNode(path="src", ntype=NodeType.DIR)
    snode = TreeSerializer().serialize(dir_node)
    dir_label = renderer._build_node_label(snode)
    assert dir_label.plain == "📦 src"
    assert any(span.style == "bold cyan" for span in dir_label.spans)

    file_node = TreeNode(path="main.py", ntype=NodeType.FILE)
    snode = TreeSerializer().serialize(file_node)
    file_label = renderer._build_node_label(snode)
    assert file_label.plain == "🐍 main.py"
    assert any(span.style == "white" for span in file_label.spans)


def test_build_node_label_with_size(base_config):
    base_config.theme = "emoji"
    base_config.show_size = True
    renderer = RichRenderer(base_config)

    file_node = TreeNode(path="main.py", ntype=NodeType.FILE)
    file_node.size = 2048
    snode = TreeSerializer().serialize(file_node)
    label = renderer._build_node_label(snode)

    # 2048 -> 2.0 kBs
    assert "2.0 kB" in label.plain
    assert any(span.style == "dim" for span in label.spans)


def test_build_node_label_full_path(base_config):
    base_config.theme = "emoji"
    base_config.full_path = True
    renderer = RichRenderer(base_config)

    file_node = TreeNode(path="src/utils/main.py", ntype=NodeType.FILE)

    # root node: only displays the name.
    snode = TreeSerializer().serialize(file_node)
    root_label = renderer._build_node_label(snode, is_root=True)
    assert root_label.plain == "🐍 main.py"

    # other: display path
    expected_path = "src/utils/main.py".replace("/", os.sep)
    snode = TreeSerializer().serialize(file_node)
    child_label = renderer._build_node_label(snode, is_root=False)
    assert expected_path in child_label.plain


def test_build_node_label_with_icon(base_config):
    base_config.theme = "emoji"
    renderer = RichRenderer(base_config)

    py_node = TreeNode(path="script.py", ntype=NodeType.FILE)
    py_node.extension = ".py"
    snode = TreeSerializer().serialize(py_node)
    label = renderer._build_node_label(snode)

    assert "🐍" in label


# ======================================================================= #
# Test: _render_recursive (Truncation)
# ======================================================================= #
def test_render_truncated_node(base_config):
    truncated_node = TreeNode(path="hidden_dir", ntype=NodeType.DIR, is_truncated=True)
    truncated_node.stats = Stats(hidden_dirs=2, hidden_files=5)

    from rich.tree import Tree

    base_config.show_ellipsis = True

    # Case 1: folders_only = True
    rich_tree_1 = Tree("Root")
    base_config.folders_only = True
    renderer = RichRenderer(base_config)
    snode = TreeSerializer().serialize(truncated_node)
    renderer._render_recursive(snode, rich_tree_1)

    child_nodes_1 = list(rich_tree_1.children)
    assert len(child_nodes_1) == 1

    rendered_text_1 = str(child_nodes_1[0].label)
    assert "... (2 dirs)" in rendered_text_1
    assert "files" not in rendered_text_1

    # Case 2: folders_only = False
    rich_tree_2 = Tree("Root")
    base_config.folders_only = False
    renderer = RichRenderer(base_config)
    snode = TreeSerializer().serialize(truncated_node)
    renderer._render_recursive(snode, rich_tree_2)

    child_nodes_2 = list(rich_tree_2.children)
    assert len(child_nodes_2) == 1

    rendered_text_2 = str(child_nodes_2[0].label)
    assert "... (2 dirs, 5 files)" in rendered_text_2


# ======================================================================= #
# Test: render (Integration)
# ======================================================================= #
def test_render_full_tree(base_config, sample_tree):
    renderer = RichRenderer(base_config)
    output = io.StringIO()

    renderer.render(sample_tree, output)
    result = output.getvalue()
    assert "root" in result
    assert "├── src" in result or "└── src" in result
    assert "main.py" in result
    assert "README.md" in result
