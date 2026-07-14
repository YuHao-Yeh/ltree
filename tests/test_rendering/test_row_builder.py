# tests/test_rendering/test_row_builder.py
from ltree.config.config import TreeConfig
from ltree.metadata.models import GitStatus
from ltree.rendering.builders.row_builder import RowBuilder
from ltree.themes.manager import ThemeManager
from ltree.tree.models import TreeNode, NodeType


# ======================================================================= #
# Tests: RowBuilder
# ======================================================================= #
def test_row_builder_folder_node(sample_tree):
    config = TreeConfig()
    config.show_permission = True
    config.show_project = True
    config.show_git = True
    config.show_size = True
    config.show_time = True
    config.show_code = True

    theme_manager = ThemeManager("emoji")
    builder = RowBuilder(config, theme_manager)

    src_node = sample_tree.children[0]

    row = builder.build(src_node)

    assert row.name == "src"
    assert row.is_dir is True
    assert "📦" in row.icon

    assert row.permission.text == "drwxrwxrwx"
    assert row.permission.kind == "perm"

    assert row.git.text == "A"
    assert row.git.status == GitStatus.ADDED
    assert row.git.kind == "git"

    assert row.size.text == "1536 B"
    assert row.size.kind == "size"

    assert any(d.text == "ltree v0.1.0 (Python)" for d in row.details)
    assert not any(d.kind == "code" for d in row.details)


def test_row_builder_file_node(sample_tree):
    config = TreeConfig()
    config.show_permission = True
    config.show_git = True
    config.show_size = True
    config.show_time = True

    theme_manager = ThemeManager("emoji")
    builder = RowBuilder(config, theme_manager)

    src_node = sample_tree.children[0]
    main_py_node = src_node.children[0]

    row = builder.build(main_py_node)

    assert row.name == "main.py"
    assert row.is_dir is False
    assert "🐍" in row.icon

    assert row.permission.text == "-rw-r--r--"
    assert row.permission.kind == "perm"

    assert row.git.text == "A"
    assert row.git.status == GitStatus.ADDED
    assert row.git.kind == "git"

    assert row.size.text == "1536 B"
    assert row.size.kind == "size"


def test_row_builder_human_readable_size(sample_tree):
    config = TreeConfig()
    config.show_size = True
    config.human_readable = True
    config.show_code = True

    theme_manager = ThemeManager("none")
    builder = RowBuilder(config, theme_manager)

    src_node = sample_tree.children[0]
    main_py_node = src_node.children[0]

    row = builder.build(main_py_node)

    assert row.size.text == "1.5 K"


def test_row_builder_truncated_directory(sample_tree):
    config = TreeConfig()
    config.show_size = True
    config.show_ellipsis = True
    theme_manager = ThemeManager("emoji")

    # Case 1: folders_only = False
    config.folders_only = False
    builder = RowBuilder(config, theme_manager)

    truncated_node = sample_tree.children[1]
    row = builder.build(truncated_node)

    assert row.size.text == ""
    assert row.is_dir is True
    assert len(row.details) == 1

    detail = row.details[0]
    assert detail.kind == "truncated"
    assert ".. (0 dirs, 2 files)" in detail.text

    # Case 2: folders_only = True
    builder.config.folders_only = True
    row = builder.build(truncated_node)

    detail = row.details[0]
    assert detail.kind == "truncated"
    assert ".. (0 dirs)" in detail.text


def test_row_builder_bare_node_safety():
    config = TreeConfig()
    config.show_permission = True
    config.show_git = True
    config.show_size = True

    theme_manager = ThemeManager("none")
    builder = RowBuilder(config, theme_manager)

    bare_node = TreeNode(path="bare_file.txt", ntype=NodeType.FILE)
    bare_node.metadata = None

    row = builder.build(bare_node)

    assert row.name == "bare_file.txt"
    assert row.permission.text == ""
    assert row.git.text == ""
    assert row.size.text == ""
    assert len(row.details) == 0
