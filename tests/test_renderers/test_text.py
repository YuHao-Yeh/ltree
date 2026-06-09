# tests/test_renderers/test_text.py
from ltree.core.config import TreeConfig
from ltree.renderers.text import TextRenderer


# ======================================================================= #
# Test: TextBuilder
# ======================================================================= #
def test_text_renderer_standard_output(sample_tree):
    config = TreeConfig()
    config.show_permission = True
    config.show_git = True
    config.show_size = True
    config.show_time = True
    config.human_readable = True
    config.show_ellipsis = True

    renderer = TextRenderer(config)
    output = renderer.render(sample_tree)

    assert "drwxrwxrwx" in output  # root
    assert "-rw-r--r--" in output  # main.py
    assert "M" in output  # Git
    assert "1.5 K" in output  # main.py (1.5 K)
    assert "500.0 B" in output  # README.md (500 B)

    assert "├── 📦 src" in output
    assert "│   └── 🐍 main.py" in output
    assert "├── 📂 truncated_dir" in output
    assert "│   └── ... (0 dirs, 2 files)" in output
    assert "└── 📖 README.md" in output


def test_text_renderer_no_metadata(sample_tree):
    config = TreeConfig()
    config.show_permission = False
    config.show_git = False
    config.show_size = False
    config.show_time = False

    renderer = TextRenderer(config)
    output = renderer.render(sample_tree)

    assert "drwxrwxrwx" not in output  # root
    assert "-rw-r--r--" not in output  # main.py
    assert "1.5 K" not in output  # main.py (1.5 K)
    assert "500.0 B" not in output  # README.md (500 B)

    assert "├── 📦 src" in output
    assert "│   └── 🐍 main.py" in output
    assert "└── 📖 README.md" in output
