import io
import json
from ltree.schema import TreeNode, Stats
from ltree.config import TreeConfig
from ltree.exporters import (
    format_size, render_text, render_json, render_markdown,
    render_markdown_as_block, print_stats
)


#=======================================================================#
# Test: format_size
#=======================================================================#
def test_format_size():
    # Raw Bytes
    assert format_size(100, human=False) == "     100 B"
    assert format_size(1024, human=False) == "    1024 B"
    
    # Human Readable
    assert format_size(500, human=True) == "500.0 B"
    assert format_size(1024, human=True) == "  1.0 K"
    assert format_size(1024**2 * 1.5, human=True) == "  1.5 M"
    assert format_size(1024**5 * 1.5, human=True) == "  1.5 P"

#=======================================================================#
# Test: render_text
#=======================================================================#
def test_render_text_path_normalization():
    # root/
    # └── child.txt
    root = TreeNode(name="root", is_dir=True, path="root")
    child = TreeNode(name="child.txt", is_dir=False, path="root\\child.txt", size=100)
    root.children.append(child)
    
    config = TreeConfig()
    config.full_path = True
    config.use_color = False
    
    output = io.StringIO()
    render_text(root, output, config)
    result = output.getvalue()
    
    assert "root/" in result
    assert "└── root/child.txt" in result
    assert "\033[97m" not in result

def test_render_text_with_size_and_path():
    root = TreeNode(name="root", is_dir=True, path="root")
    child = TreeNode(name="child.txt", is_dir=False, path="root/child.txt", size=100)
    root.children.append(child)
    root.size += child.size
    root.stats.visible_files = 1
    
    config = TreeConfig()
    config.use_color = True
    config.show_size = True
    config.full_path = True
    
    output = io.StringIO()
    render_text(root, output, config)
    result = output.getvalue()
    
    assert "[     100 B]" in result
    assert "root/child.txt" in result
    assert "\033[97m" in result

def test_render_text_truncated_indentation():
    # root/
    # ├── sub/ (truncated)
    # └── other.txt
    root = TreeNode(name="root", is_dir=True, path="root")
    sub = TreeNode(name="sub", is_dir=True, path="root/sub", is_truncated=True)
    sub.stats = Stats(hidden_dirs=1, hidden_files=1)
    other = TreeNode(name="other.txt", is_dir=False, path="root/other.txt")
    
    root.children.append(sub)
    root.children.append(other)
    
    config = TreeConfig()
    config.show_ellipsis = True
    config.use_color = False
    
    # normal
    output = io.StringIO()
    render_text(root, output, config)
    result = output.getvalue()
    
    assert "│   └── ... (1 dirs, 1 files)" in result

    # only folders
    config.folders_only = True
    root.children.remove(other)
    output = io.StringIO()
    render_text(root, output, config)
    result = output.getvalue()
    assert "    └── ... (1 dirs)" in result

#=======================================================================#
# Test: render_json
#=======================================================================#
def test_render_json():
    root = TreeNode(name="root", is_dir=True, path="root", size=0)
    child = TreeNode(name="file1.txt", is_dir=False,path="root/file1.txt", size=1536)
    root.children.append(child)
    root.size += child.size
    root.stats.visible_files = 1
    
    config = TreeConfig()

    # Raw bytes
    output = io.StringIO()
    render_json(root, output, config)
    
    data = json.loads(output.getvalue())
    assert data["name"] == "root"
    assert data["size_bytes"] == 1536
    assert "content_summary" in data
    assert len(data["children"]) == 1

    # Human readable
    config.human_readable = True
    output = io.StringIO()

    render_json(root, output, config)
    data = json.loads(output.getvalue())
    assert data["size_bytes"] == 1536
    assert data["size_human"] == "1.5 K"

#=======================================================================#
# Test: render_markdown
#=======================================================================#
def test_render_markdown():
    root = TreeNode(name="root", is_dir=True, path="root")
    child = TreeNode(name="file.py", is_dir=False, path="root/file.py", size=3*1024)
    root.children.append(child)
    root.size += child.size
    root.stats.visible_files = 1
    
    config = TreeConfig()

    # normal
    output = io.StringIO()
    render_markdown(root, output, config)
    result = output.getvalue()
    
    assert "📂 **root/**" in result
    assert "📄 `file.py`" in result

    # show size
    config.show_size = True
    output.flush()
    render_markdown(root, output, config)
    result = output.getvalue()

    assert "📂 `3072 B` **root/**" in result
    assert "📄 `3072 B` `file.py`" in result

    # show size - human readable
    config.human_readable = True
    output.flush()
    render_markdown(root, output, config)
    result = output.getvalue()

    assert "📂 `3.0 K` **root/**" in result
    assert "📄 `3.0 K` `file.py`" in result

#=======================================================================#
# Test: render_markdown
#=======================================================================#
def test_render_markdown_as_block():
    root = TreeNode(name="root", is_dir=True, path="root")
    child = TreeNode(name="file.py", is_dir=False, path="root/file.py")
    root.children.append(child)
    
    config = TreeConfig()
    output = io.StringIO()
    render_markdown_as_block(root, output, config)
    result = output.getvalue()
    
    assert "root/" in result
    assert "file.py" in result

#=======================================================================#
# Test: print stats
#=======================================================================#
def test_print_stats(capsys):
    root = TreeNode(name="root", is_dir=True, path="root")
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
