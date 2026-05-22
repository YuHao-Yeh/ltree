import pytest
from ltree.themes.icons import IconProvider
from ltree.themes import emoji, nerd


# ======================================================================= #
# Test: init and none
# ======================================================================= #
def test_icon_provider_init():
    assert IconProvider("emoji").map == emoji
    assert IconProvider("nerd").map == nerd
    
    assert IconProvider("none").map is None
    assert IconProvider("invalid_theme").map is None

def test_icon_provider_none_theme():
    provider = IconProvider("none")
    
    assert provider.get_icon("src", is_dir=True) == ""
    assert provider.get_icon("main.py", is_dir=False) == ""
    assert provider.get_icon("Dockerfile", is_dir=False) == ""

# ======================================================================= #
# Test: Emoji
# ======================================================================= #
def test_get_icon_directories_emoji():
    provider = IconProvider("emoji")
    
    # 1. known directories
    assert provider.get_icon(".git", is_dir=True) == f"{emoji.FOLDERS['.git']} "
    assert provider.get_icon("node_modules", is_dir=True) == f"{emoji.FOLDERS['node_modules']} "
    
    # 2. unknown directories
    assert provider.get_icon("my_custom_folder", is_dir=True) == f"{emoji.DEFAULT_FOLDER} "

def test_get_icon_files_emoji():
    provider = IconProvider("emoji")
    
    # 1. matched filename
    assert provider.get_icon("Dockerfile", is_dir=False) == f"{emoji.FILENAMES['Dockerfile']} "
    assert provider.get_icon("README.md", is_dir=False) == f"{emoji.FILENAMES['README.md']} "
    
    # 2. file extension
    assert provider.get_icon("script.py", is_dir=False) == f"{emoji.EXTENSIONS['.py']} "
    assert provider.get_icon("style.css", is_dir=False) == f"{emoji.EXTENSIONS['.css']} "
    
    # 3. uppercase file extensions
    assert provider.get_icon("IMAGE.PNG", is_dir=False) == f"{emoji.EXTENSIONS.get('.png', emoji.DEFAULT_FILE)} "
    
    # 4. unknown extension file
    assert provider.get_icon("data.unknown", is_dir=False) == f"{emoji.DEFAULT_FILE} "
    assert provider.get_icon("just_a_file", is_dir=False) == f"{emoji.DEFAULT_FILE} "

# ======================================================================= #
# Test: Nerd
# ======================================================================= #
def test_get_icon_nerd_font():
    provider = IconProvider("nerd")

    assert provider.get_icon("Dockerfile", is_dir=False) == f"{nerd.FILENAMES['Dockerfile']} "
    assert provider.get_icon(".git", is_dir=True) == f"{nerd.FOLDERS['.git']} "
    assert provider.get_icon("main.py", is_dir=False) == f"{nerd.EXTENSIONS['.py']} "