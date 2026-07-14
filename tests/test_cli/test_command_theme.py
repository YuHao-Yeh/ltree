# tests/test_cli/test_command_theme.py
import argparse

from ltree.cli.commands.theme import run_theme, run_theme_preview
from ltree.themes.manager import ThemeManager


# ======================================================================= #
# Tests: run_theme
# ======================================================================= #
def test_run_theme_output(capsys):
    args = argparse.Namespace()
    run_theme(args)

    captured = capsys.readouterr()

    assert "Available icon themes:" in captured.out
    assert "emoji" in captured.out
    assert "nerd" in captured.out
    assert "none" in captured.out


def test_run_theme_with_unknown_fallback(monkeypatch, capsys):
    monkeypatch.setitem(ThemeManager.THEMES, "custom_unknown", None)

    args = argparse.Namespace()
    run_theme(args)

    captured = capsys.readouterr()

    assert "  * custom_unknown - Unclear" in captured.out
    assert "  * emoji - Beautiful colored emojis (Default)" in captured.out


# ======================================================================= #
# Tests: run_theme_preview
# ======================================================================= #
def test_run_theme_preview_outputs(capsys):
    # A. Emoji
    args_emoji = argparse.Namespace(theme_name="emoji")
    run_theme_preview(args_emoji)

    captured_emoji = capsys.readouterr()
    assert "--- Previewing theme 'emoji' ---" in captured_emoji.out
    assert "Directory: 📦 src/" in captured_emoji.out
    assert "Python:    🐍 main.py" in captured_emoji.out
    assert "Symlink:   🔗 shortcut" in captured_emoji.out

    # B. Nerd Font
    args_nerd = argparse.Namespace(theme_name="nerd")
    run_theme_preview(args_nerd)

    captured_nerd = capsys.readouterr()
    assert "--- Previewing theme 'nerd' ---" in captured_nerd.out
    assert "Directory:  src/" in captured_nerd.out
    assert "Python:     main.py" in captured_nerd.out
