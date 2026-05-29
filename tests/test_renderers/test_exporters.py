import io
import json
import os
from ltree.core.models import TreeNode, Stats, NodeType
from ltree.core.config import TreeConfig
from ltree.renderers.exporters import (
    TextRenderer,
    JsonRenderer,
    MarkdownRenderer,
    MarkdownBlockRenderer,
    print_stats,
)


# =======================================================================#
# Test: render_text
# =======================================================================#
def test_render_text_path_normalization():
    # root/
    # └── child.txt
    root = TreeNode(path="root", ntype=NodeType.DIR)
    path = os.path.join("root", "child.txt")
    child = TreeNode(path=path, ntype=NodeType.FILE)
    child.size = 100
    root.children.append(child)

    config = TreeConfig()
    config.full_path = True
    config.use_color = False
    config.theme = "none"

    output = io.StringIO()
    TextRenderer(config).render(root, output)
    result = output.getvalue()

    assert f"root{os.sep}" in result
    assert f"└── root{os.sep}child.txt" in result
    assert "\033[97m" not in result


def test_render_text_with_size_and_path():
    root = TreeNode(path="root", ntype=NodeType.DIR)
    path = os.path.join("root", "child.txt")
    child = TreeNode(path=path, ntype=NodeType.FILE)
    child.size = 100
    root.children.append(child)
    root.size += child.size
    root.stats.visible_files = 1

    config = TreeConfig()
    config.use_color = True
    config.show_size = True
    config.full_path = True

    output = io.StringIO()
    TextRenderer(config).render(root, output)
    result = output.getvalue()

    assert "[     100 B]" in result
    assert f"root{os.sep}child.txt" in result
    assert "\033[97m" in result


def test_render_text_truncated_indentation():
    # root/
    # ├── sub/ (truncated)
    # └── other.txt
    root = TreeNode(path="root", ntype=NodeType.DIR)
    sub_path = os.path.join("root", "sub")
    sub = TreeNode(path=sub_path, ntype=NodeType.DIR, is_truncated=True)
    sub.stats = Stats(hidden_dirs=1, hidden_files=1)
    other_path = os.path.join("root", "other.txt")
    other = TreeNode(path=other_path, ntype=NodeType.FILE)

    root.children.append(sub)
    root.children.append(other)

    config = TreeConfig()
    config.show_ellipsis = True
    config.use_color = False

    # normal
    output = io.StringIO()
    TextRenderer(config).render(root, output)
    result = output.getvalue()

    assert "│   └── ... (1 dirs, 1 files)" in result

    # only folders
    config.folders_only = True
    root.children.remove(other)
    output = io.StringIO()
    TextRenderer(config).render(root, output)
    result = output.getvalue()
    assert "    └── ... (1 dirs)" in result


# =======================================================================#
# Test: render_json
# =======================================================================#
def test_render_json():
    root = TreeNode(path="root", ntype=NodeType.DIR)
    path = os.path.join("root", "file1.txt")
    child = TreeNode(path=path, ntype=NodeType.FILE)
    child.size = 1536
    root.children.append(child)
    root.size += child.size
    root.stats.visible_files = 1

    config = TreeConfig()

    # Raw bytes
    output = io.StringIO()
    JsonRenderer(config).render(root, output)

    data = json.loads(output.getvalue())
    assert data["name"] == "root"
    assert data["size_bytes"] == 1536
    assert "content_summary" in data
    assert len(data["children"]) == 1

    # Human readable
    config.human_readable = True
    output = io.StringIO()

    JsonRenderer(config).render(root, output)
    data = json.loads(output.getvalue())
    assert data["size_bytes"] == 1536
    assert data["size_human"] == "1.5 K"


def test_render_json_truncated():
    path = os.path.join("project", "root")
    root = TreeNode(path=path, ntype=NodeType.DIR)
    root.is_truncated = True
    root.size = 5000
    root.stats.hidden_dirs = 5
    root.stats.hidden_files = 12

    config = TreeConfig()
    output = io.StringIO()
    JsonRenderer(config).render(root, output)

    data = json.loads(output.getvalue())

    assert data["is_truncated"] is True
    assert "hidden_summary" in data
    assert data["hidden_summary"]["hidden_folders"] == 5
    assert data["hidden_summary"]["hidden_files"] == 12

    assert "children" not in data


# =======================================================================#
# Test: render_markdown
# =======================================================================#
def test_render_markdown():
    root = TreeNode(path="root", ntype=NodeType.DIR)
    path = os.path.join("root", "file.py")
    child = TreeNode(path=path, ntype=NodeType.FILE)
    child.size = 3 * 1024
    root.children.append(child)
    root.size += child.size
    root.stats.visible_files = 1

    config = TreeConfig()

    # normal
    output = io.StringIO()
    MarkdownRenderer(config).render(root, output)
    result = output.getvalue()

    assert "📂 **root/**" in result
    assert "🐍 `file.py`" in result

    # show size
    config.show_size = True
    output.flush()
    MarkdownRenderer(config).render(root, output)
    result = output.getvalue()

    assert "📂 `3072 B` **root/**" in result
    assert "🐍 `3072 B` `file.py`" in result

    # show size - human readable
    config.human_readable = True
    output.flush()
    MarkdownRenderer(config).render(root, output)
    result = output.getvalue()

    assert "📂 `3.0 K` **root/**" in result
    assert "🐍 `3.0 K` `file.py`" in result


def test_markdown_renderer_truncation():
    path = os.path.join("project", "root")
    root = TreeNode(path=path, ntype=NodeType.DIR)
    root.is_truncated = True
    root.size = 5000
    root.stats.hidden_dirs = 5
    root.stats.hidden_files = 12

    # 1. dirs + files
    config = TreeConfig()
    config.show_ellipsis = True
    output = io.StringIO()
    MarkdownRenderer(config).render(root, output)

    content = output.getvalue()
    assert "  - ... (5 dirs, 12 files)" in content

    # 2. folders_only
    config.folders_only = True
    output = io.StringIO()

    MarkdownRenderer(config).render(root, output)

    content = output.getvalue()
    assert "  - ... (5 dirs)" in content
    assert "files" not in content

    # 3. show_ellipsis = False
    config.show_ellipsis = False
    output = io.StringIO()

    MarkdownRenderer(config).render(root, output)

    content = output.getvalue()
    assert "..." not in content


# =======================================================================#
# Test: render_markdown
# =======================================================================#
def test_render_markdown_as_block():
    root = TreeNode(path="root", ntype=NodeType.DIR)
    path = os.path.join("root", "file.py")
    child = TreeNode(path=path, ntype=NodeType.FILE)
    root.children.append(child)

    config = TreeConfig()
    output = io.StringIO()
    MarkdownBlockRenderer(config).render(root, output)
    result = output.getvalue()

    assert f"root{os.sep}" in result
    assert "file.py" in result


# =======================================================================#
# Test: print stats
# =======================================================================#
def test_print_stats(capsys):
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.stats = Stats(visible_dirs=1, visible_files=2, hidden_dirs=0, hidden_files=0)

    # normal
    config = TreeConfig()
    print_stats(root, config)

    captured = capsys.readouterr()
    assert "Summary" in captured.out
    assert "1 directories" in captured.out
    assert "2 files" in captured.out

    # show size
    config.show_size = True
    print_stats(root, config)

    captured = capsys.readouterr()
    assert "0 B" in captured.out


def test_print_stats_rich(capsys):
    root = TreeNode(path="root", ntype=NodeType.DIR)
    root.stats = Stats(visible_dirs=1, visible_files=2, hidden_dirs=0, hidden_files=0)

    # normal
    config = TreeConfig()
    print_stats(root, config, fmt="rich")

    captured = capsys.readouterr()
    assert "Summary" in captured.out
    assert "1 directories" in captured.out
    assert "2 files" in captured.out

    # show size
    config.show_size = True
    print_stats(root, config, fmt="rich")

    captured = capsys.readouterr()
    assert "0 bytes" in captured.out
