import os

from ltree.core.models import TreeNode
from ltree.themes.manager import ThemeManager
from ltree.themes.emoji import EmojiTheme
from ltree.themes.nerd import NerdTheme


# ======================================================================= #
# Helper for concise TreeNode creation in tests
# ======================================================================= #
def make_node(
    name: str,
    is_dir: bool = False,
    is_symlink: bool = False,
    is_executable: bool = False,
) -> TreeNode:
    node = TreeNode(name=name, is_dir=is_dir, path=name)
    node.is_symlink = is_symlink
    node.is_executable = is_executable
    if not is_dir:
        _, ext = os.path.splitext(name)
        node.extension = ext.lower()
    return node


# ======================================================================= #
# Test: init and none
# ======================================================================= #
def test_theme_manager_none_theme():
    provider = ThemeManager("none")

    assert provider.get_icon(make_node("src", is_dir=True)) == ""
    assert provider.get_icon(make_node("main.py", is_dir=False)) == ""
    assert provider.get_icon(make_node("Dockerfile", is_dir=False)) == ""


def test_no_theme_style():
    provider = ThemeManager("none")
    node = TreeNode(name="src", is_dir=True, path="src")
    assert provider.get_style(node) == ""


# ======================================================================= #
# Test: Emoji
# ======================================================================= #
def test_get_icon_directories_emoji():
    provider = ThemeManager("emoji")

    # 1. known directories
    assert (
        provider.get_icon(make_node(".git", is_dir=True))
        == f"{EmojiTheme.DIR_ICON['.git']} "
    )
    assert (
        provider.get_icon(make_node("node_modules", is_dir=True))
        == f"{EmojiTheme.DIR_ICON['node_modules']} "
    )

    # 2. unknown directories
    assert (
        provider.get_icon(make_node("my_custom_folder", is_dir=True))
        == f"{EmojiTheme.DEFAULT_FOLDER} "
    )


def test_get_icon_files_emoji():
    provider = ThemeManager("emoji")

    # 1. matched filename
    assert (
        provider.get_icon(make_node("Dockerfile", is_dir=False))
        == f"{EmojiTheme.FILE_ICON['Dockerfile']} "
    )
    assert (
        provider.get_icon(make_node("README.md", is_dir=False))
        == f"{EmojiTheme.FILE_ICON['README.md']} "
    )

    # 2. file extension
    assert (
        provider.get_icon(make_node("script.py", is_dir=False))
        == f"{EmojiTheme.EXT_ICON['.py']} "
    )
    assert (
        provider.get_icon(make_node("style.css", is_dir=False))
        == f"{EmojiTheme.EXT_ICON['.css']} "
    )

    # 3. uppercase file extensions
    assert (
        provider.get_icon(make_node("IMAGE.PNG", is_dir=False))
        == f"{EmojiTheme.EXT_ICON.get('.png', EmojiTheme.DEFAULT_FILE)} "
    )

    # 4. unknown extension file
    assert (
        provider.get_icon(make_node("data.unknown", is_dir=False))
        == f"{EmojiTheme.DEFAULT_FILE} "
    )
    assert (
        provider.get_icon(make_node("just_a_file", is_dir=False))
        == f"{EmojiTheme.DEFAULT_FILE} "
    )


def test_icons_symlink_and_executable_emoji():
    provider = ThemeManager("emoji")

    symlink_dir = TreeNode(name="my_link", is_dir=True, path="my_link", is_symlink=True)
    assert provider.get_icon(symlink_dir) == "🔗 "
    assert provider.get_style(symlink_dir) == "italic magenta"

    exec_file = TreeNode(name="run.sh", is_dir=False, path="run.sh", is_executable=True)
    assert provider.get_style(exec_file) == "bold green"

    fallback_file = TreeNode(name="style.css", is_dir=False, path="style.css")
    assert provider.get_icon(fallback_file) == "🎨 "


# ======================================================================= #
# Test: Nerd
# ======================================================================= #
def test_get_icon_nerd_font():
    provider = ThemeManager("nerd")

    assert (
        provider.get_icon(make_node("Dockerfile", is_dir=False))
        == f"{NerdTheme.FILE_ICON['Dockerfile']} "
    )
    assert (
        provider.get_icon(make_node(".git", is_dir=True))
        == f"{NerdTheme.DIR_ICON['.git']} "
    )
    assert (
        provider.get_icon(make_node("main.py", is_dir=False))
        == f"{NerdTheme.EXT_ICON['.py']} "
    )


def test_icons_symlink_and_executable_nerd():
    provider = ThemeManager("nerd")

    symlink_dir = TreeNode(
        name="my_link", is_dir=True, path="my_link", is_symlink=False
    )
    assert provider.get_icon(symlink_dir) == " "
    assert provider.get_style(symlink_dir) == "bold cyan"

    symlink_file = TreeNode(
        name="my_link", is_dir=False, path="my_link", is_symlink=True
    )
    assert provider.get_icon(symlink_file) == " "
    assert provider.get_style(symlink_file) == "italic magenta"

    exec_file = TreeNode(name="run.sh", is_dir=False, path="run.sh", is_executable=True)
    assert provider.get_style(exec_file) == "bold green"

    fallback_file = TreeNode(name="style.css", is_dir=False, path="style.css")
    assert provider.get_icon(fallback_file) == " "
    assert provider.get_style(fallback_file) == "white"
