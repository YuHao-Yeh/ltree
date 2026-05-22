import io
import os
import pytest
from ltree.core.models import TreeNode, Stats
from ltree.core.config import TreeConfig
from ltree.renderers.rich_renderer import RichRenderer
from ltree.constants import RICH_COLOR_DIR, RICH_COLOR_FILE


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
    root = TreeNode(name="root", is_dir=True, path="root")
    
    src = TreeNode(name="src", is_dir=True, path="root/src")
    main_py = TreeNode(name="main.py", is_dir=False, path="root/src/main.py", size=1024)
    src.children.append(main_py)
    
    readme = TreeNode(name="README.md", is_dir=False, path="root/README.md", size=500)
    
    root.children.extend([src, readme])
    return root


# ======================================================================= #
# Test: _build_node_label
# ======================================================================= #
def test_build_node_label_basic(base_config):
    renderer = RichRenderer(base_config)
    
    dir_node = TreeNode(name="src", is_dir=True, path="src")
    dir_label = renderer._build_node_label(dir_node)
    assert RICH_COLOR_DIR in dir_label
    assert "src" in dir_label

    file_node = TreeNode(name="main.py", is_dir=False, path="main.py")
    file_label = renderer._build_node_label(file_node)
    assert RICH_COLOR_FILE in file_label
    assert "main.py" in file_label

def test_build_node_label_with_size(base_config):
    base_config.show_size = True
    renderer = RichRenderer(base_config)
    
    file_node = TreeNode(name="main.py", is_dir=False, path="main.py", size=2048)
    label = renderer._build_node_label(file_node)
    
    # 2048 -> 2.0 kBs
    assert "2.0 kB" in label
    assert "[dim]" in label

def test_build_node_label_full_path(base_config):
    base_config.full_path = True
    renderer = RichRenderer(base_config)
    
    file_node = TreeNode(name="main.py", is_dir=False, path="src/utils/main.py")
    
    # root node: only displays the name.
    root_label = renderer._build_node_label(file_node, is_root=True)
    assert f"{RICH_COLOR_FILE}main.py[/]" in root_label
    
    # other: display path
    expected_path = "src/utils/main.py".replace("/", os.sep)
    child_label = renderer._build_node_label(file_node, is_root=False)
    assert f"{RICH_COLOR_FILE}{expected_path}[/]" in child_label

def test_build_node_label_with_icon(base_config):
    base_config.theme = "emoji"
    renderer = RichRenderer(base_config)
    
    py_node = TreeNode(name="script.py", is_dir=False, path="script.py")
    label = renderer._build_node_label(py_node)
    
    assert "🐍" in label


# ======================================================================= #
# Test: _render_recursive (Truncation)
# ======================================================================= #
def test_render_truncated_node(base_config):
    truncated_node = TreeNode(name="hidden_dir", is_dir=True, path="hidden_dir", is_truncated=True)
    truncated_node.stats = Stats(hidden_dirs=2, hidden_files=5)
    
    from rich.tree import Tree
    
    base_config.show_ellipsis = True

    # Case 1: folders_only = True
    rich_tree_1 = Tree("Root")
    base_config.folders_only = True
    renderer = RichRenderer(base_config)   
    renderer._render_recursive(truncated_node, rich_tree_1)
    
    child_nodes_1 = list(rich_tree_1.children)
    assert len(child_nodes_1) == 1
    
    rendered_text_1 = str(child_nodes_1[0].label)
    assert "... (2 dirs)" in rendered_text_1
    assert "files" not in rendered_text_1 
    
    # Case 2: folders_only = False
    rich_tree_2 = Tree("Root")
    base_config.folders_only = False
    renderer = RichRenderer(base_config)   
    renderer._render_recursive(truncated_node, rich_tree_2)
    
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