import os

from ltree.core.models import TreeNode, NodeType
from ltree.themes.manager import ThemeManager
from ltree.themes.emoji import EmojiTheme
from ltree.themes.nerd import NerdTheme


# ======================================================================= #
# Helper for concise TreeNode creation in tests
# ======================================================================= #
def make_node(
    path: str,
    ntype: NodeType,
    is_symlink: bool = False,
    is_executable: bool = False,
) -> TreeNode:
    node = TreeNode(path=path, ntype=ntype)
    node.is_symlink = is_symlink
    node.is_executable = is_executable
    if ntype == NodeType.FILE:
        _, ext = os.path.splitext(path)
        node.extension = ext.lower()
    return node


# ======================================================================= #
# Test: init and none
# ======================================================================= #
def test_theme_manager_none_theme():
    provider = ThemeManager("none")

    assert provider.get_icon(make_node("src", ntype=NodeType.DIR)) == ""
    assert provider.get_icon(make_node("main.py", ntype=NodeType.FILE)) == ""
    assert provider.get_icon(make_node("Dockerfile", ntype=NodeType.FILE)) == ""


def test_no_theme_style():
    provider = ThemeManager("none")
    node = TreeNode(path="src", ntype=NodeType.DIR)
    assert provider.get_style(node) == ""


# ======================================================================= #
# Test: Emoji
# ======================================================================= #
def test_get_icon_directories_emoji():
    provider = ThemeManager("emoji")

    # 1. known directories
    assert (
        provider.get_icon(make_node(".git", ntype=NodeType.DIR))
        == f"{EmojiTheme.DIR_ICON['.git']} "
    )
    assert (
        provider.get_icon(make_node("node_modules", ntype=NodeType.DIR))
        == f"{EmojiTheme.DIR_ICON['node_modules']} "
    )

    # 2. unknown directories
    assert (
        provider.get_icon(make_node("my_custom_folder", ntype=NodeType.DIR))
        == f"{EmojiTheme.DEFAULT_FOLDER} "
    )


def test_get_icon_files_emoji():
    provider = ThemeManager("emoji")

    # 1. matched filename
    assert (
        provider.get_icon(make_node("Dockerfile", ntype=NodeType.FILE))
        == f"{EmojiTheme.FILE_ICON['Dockerfile']} "
    )
    assert (
        provider.get_icon(make_node("README.md", ntype=NodeType.FILE))
        == f"{EmojiTheme.FILE_ICON['README.md']} "
    )

    # 2. file extension
    assert (
        provider.get_icon(make_node("script.py", ntype=NodeType.FILE))
        == f"{EmojiTheme.EXT_ICON['.py']} "
    )
    assert (
        provider.get_icon(make_node("style.css", ntype=NodeType.FILE))
        == f"{EmojiTheme.EXT_ICON['.css']} "
    )

    # 3. uppercase file extensions
    assert (
        provider.get_icon(make_node("IMAGE.PNG", ntype=NodeType.FILE))
        == f"{EmojiTheme.EXT_ICON.get('.png', EmojiTheme.DEFAULT_FILE)} "
    )

    # 4. unknown extension file
    assert (
        provider.get_icon(make_node("data.unknown", ntype=NodeType.FILE))
        == f"{EmojiTheme.DEFAULT_FILE} "
    )
    assert (
        provider.get_icon(make_node("just_a_file", ntype=NodeType.FILE))
        == f"{EmojiTheme.DEFAULT_FILE} "
    )


def test_icons_symlink_and_executable_emoji():
    provider = ThemeManager("emoji")

    symlink_dir = make_node(path="my_link", ntype=NodeType.DIR, is_symlink=True)
    assert provider.get_icon(symlink_dir) == "🔗 "
    assert provider.get_style(symlink_dir) == "italic magenta"

    exec_file = make_node(path="run.sh", ntype=NodeType.FILE, is_executable=True)
    assert provider.get_style(exec_file) == "bold green"

    fallback_file = make_node(path="style.css", ntype=NodeType.FILE)
    assert provider.get_icon(fallback_file) == "🎨 "


# ======================================================================= #
# Test: Nerd
# ======================================================================= #
def test_get_icon_nerd_font():
    provider = ThemeManager("nerd")

    assert (
        provider.get_icon(make_node("Dockerfile", ntype=NodeType.FILE))
        == f"{NerdTheme.FILE_ICON['Dockerfile']} "
    )
    assert (
        provider.get_icon(make_node(".git", ntype=NodeType.DIR))
        == f"{NerdTheme.DIR_ICON['.git']} "
    )
    assert (
        provider.get_icon(make_node("main.py", ntype=NodeType.FILE))
        == f"{NerdTheme.EXT_ICON['.py']} "
    )


def test_icons_symlink_and_executable_nerd():
    provider = ThemeManager("nerd")

    symlink_dir = make_node(path="my_link", ntype=NodeType.DIR, is_symlink=False)
    assert provider.get_icon(symlink_dir) == " "
    assert provider.get_style(symlink_dir) == "bold cyan"

    symlink_file = make_node(path="my_link", ntype=NodeType.FILE, is_symlink=True)
    assert provider.get_icon(symlink_file) == " "
    assert provider.get_style(symlink_file) == "italic magenta"

    exec_file = make_node(path="run.sh", ntype=NodeType.FILE, is_executable=True)
    assert provider.get_style(exec_file) == "bold green"

    fallback_file = make_node(path="style.css", ntype=NodeType.FILE)
    assert provider.get_icon(fallback_file) == " "
    assert provider.get_style(fallback_file) == "white"
