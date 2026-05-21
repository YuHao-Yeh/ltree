ICONS = {
    "dir": "📁",
    "file": "📄",
    ".py": "🐍",
    ".md": "📝",
    ".js": "javascript",
    ".json": "⚙️",
    ".git": "🌳",
    "LICENSE": "⚖️",
    "__pycache__": "🗑️",
}

def get_icon(name, is_dir=False):
    if is_dir:
        return ICONS.get(name, ICONS["dir"])
    
    if name in ICONS:
        return ICONS[name]
    
    import os
    ext = os.path.splitext(name)[1]
    return ICONS.get(ext, ICONS["file"])