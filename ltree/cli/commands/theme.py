# ltree/cli/commands/theme.py
from ltree.themes.manager import ThemeManager


def run_theme(args) -> None:
    print("Available icon themes:")
    for theme_name in ThemeManager.THEMES.keys():
        desc = ""
        if theme_name == "emoji":
            desc = " - Beautiful colored emojis (Default)"
        elif theme_name == "nerd":
            desc = " - Nerd Fonts symbols (Requires patched terminal font)"
        elif theme_name == "none":
            desc = " - Pure text without any icons"
        else:
            desc = " - Unclear"
        print(f"  * {theme_name}{desc}")


def run_theme_preview(args) -> None:
    theme_name = args.theme_name
    manager = ThemeManager(theme_name)

    mock_dir = {
        "name": "src",
        "type": "directory",
        "metadata": {"fs": {"is_symlink": False}},
    }
    mock_py = {
        "name": "main.py",
        "type": "file",
        "metadata": {"fs": {"is_symlink": False, "extension": ".py"}},
    }
    mock_link = {
        "name": "shortcut",
        "type": "file",
        "metadata": {"fs": {"is_symlink": True, "extension": ""}},
    }

    print(f"--- Previewing theme '{theme_name}' ---")
    print(f"Directory: {manager.get_icon(mock_dir)}src/")
    print(f"Python:    {manager.get_icon(mock_py)}main.py")
    print(f"Symlink:   {manager.get_icon(mock_link)}shortcut")
