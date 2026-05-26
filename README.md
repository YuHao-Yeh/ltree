# ltree

<div align="center">
  <!-- Metadata -->
  <p>
    <a href="https://github.com/YuHao-Yeh/ltree/actions">
      <img src="https://github.com/YuHao-Yeh/ltree/actions/workflows/tests.yml/badge.svg" alt="Python Tests">
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
    </a>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/python-%3E%3D3.10-blue" alt="Python Version">
    </a>
  </p>
</div>

**ltree** is a fast, customizable CLI tool to visualize directory structures in a tree diagram. It features beautiful *Rich UI* rendering, *Nerd Font/Emoji* icon support, detailed statistics, and multiple export formats.

```bash
>>> ltree .
📂 ltree/
├── ⚖️ LICENSE
├── 📂 ltree/
│   ├── 🐍 __init__.py
│   ├── 🐍 cli.py
│   ├── 🐍 constants.py
│   ├── 📂 core/
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 config.py
│   │   ├── 🐍 models.py
│   │   ├── 🐍 scanner.py
│   │   └── 🐍 utils.py
│   ├── 📂 renderers/
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 base.py
│   │   ├── 🐍 exporters.py
│   │   └── 🐍 rich_renderer.py
│   └── 📂 themes/
│       ├── 🐍 __init__.py
│       ├── 🐍 emoji.py
│       ├── 🐍 icons.py
│       └── 🐍 nerd.py
├── 📂 ltree-vscode/
│   ├── 📝 CHANGELOG.md
│   ├── 📄 eslint.config.mjs
│   ├── ⚙️ package-lock.json
│   ├── ⚙️ package.json
│   ├── 📖 README.md
│   ├── 📦 src/
│   │   └── 🟦 extension.ts
│   └── ⚙️ tsconfig.json
├── ⚙️ pyproject.toml
├── 📖 README.md
├── 🧪 tests/
│   ├── 🐍 __init__.py
│   ├── 🐍 test_cli.py
│   ├── 🐍 test_config.py
│   ├── 🐍 test_core.py
│   ├── 🐍 test_exporters.py
│   ├── 🐍 test_icons.py
│   ├── 🐍 test_rich_renderer.py
│   └── 🐍 test_utils.py
└── 🔒 uv.lock

Summary:
Visible:   7 directories,  35 files
Total  :   7 directories,  35 files
```

---

## Installation

For local development or usage:

```bash
# Clone the repository
git clone https://github.com/YuHao-Yeh/ltree.git
cd ltree

# Install in editable mode (using uv)
uv pip install -e .

# Or using standard pip
pip install -e .
```

---

## VS Code Extension

**ltree** now comes with an official VS Code companion!

- **Quick Action**: Right-click any file or folder in the Explorer to generate a tree.
- **Multiple Formats**: Copy as Text, JSON, or Markdown Blocks (perfect for AI prompts).
- **Customizable**: Pass any CLI arguments directly from VS Code.

To use it, check the [ltree-vscode](./ltree-vscode) directory for installation instructions.

---

## Usage

```bash
ltree [path] [options]
```

### Basic Commands
```bash
# Display current directory structure
ltree

# Output to console with color
ltree . -o - --color

# Save tree to a file
ltree /path/to/dir -o tree.txt

# For more help
ltree --help
```

### Quick Examples
<details>
<summary>Click to expand examples</summary>

- **Export to JSON:** `ltree -F json -o data.json`
- **Markdown List:** `ltree -F md -o report.md`
- **Markdown Block:** `ltree -F block -o report.md`
- **Limit Depth:** `ltree -L 2 --show-ellipsis`
- **Filter by Extension:** `ltree --ex-ext .log --ex-ext .tmp`
- **Filter by Regex**: `ltree --re-ex "test_.*\.py"`
- **Only Directories**: `ltree -d --dirs-first`
- **Show Sizes**: `ltree -s -H`
- **Nerd Fonts and Rich UI**: `ltree . -F rich --theme nerd`
</details>

---

## Options

*Run `ltree --help` to see the full list of available options.*

<details>
<summary><b>View Full Parameter List</b></summary>

### Basic Options
| Argument | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `start_path` | | `.` | Starting directory path. |
| `--output` | `-o` | `-` | Output file name. Use `-` for stdout. |

### Output Formatting & Display
| Argument | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--format` | `-F` | `text` | Choices: `text`, `json`, `md`, `markdown`, `block`, `rich`. |
| `--theme` | | emoji |	Icon theme to use. Choices: emoji, nerd, none. |
| `--color` | `-c` | | Enable colored output. |
| `--size` | `-s` | | Show file/directory sizes. |
| `--human` | `-H` | | Show size in human-readable format (e.g., 1K, 2M). |

### Filtering Rules
| Argument | Short | Description |
| :--- | :--- | :--- |
| `--all` | `-a` | Show hidden files and directories (starting with `.`). |
| `--dirs-only` | `-d` | Only display directories. |
| `--ex-dirs` | | Exclude specific directories. |
| `--ex-files` | `-I` | Exclude files (supports wildcards like `*.log`). |
| `--ex-ext` | | Exclude by file extension (e.g., `.log`). |
| `--ex-prefix` | | Exclude items by prefix. |
| `--re-ex` | | Exclude paths matching a regular expression. |
| `--no-ignore` | | Disable automatic exclusion based on .gitignore (enabled by default). |
| `--add-dirs` | | Re-include specific directories previously excluded. |
| `--add-files` | | Re-include specific files previously excluded. |

### Display Options
| Argument | Short | Description |
| :--- | :--- | :--- |
| `--max-depth` | `-L` | Limit directory recursion depth. |
| `--full-path` | `-f` | Print the full path prefix for every entry. |
| `--dirs-first` | | List directories before files. |
| `--show-ellipsis`| | Show "..." when depth is truncated. |

</details>

---

## Configuration

You can save your favorite settings in a config file so you don't have to type them every time. `ltree` will automatically search for these files in your project directory (or climb up to find them):

- `.ltreerc` (JSON)
- `pyproject.toml` (under `[tool.ltree]`)

### Configuration Priority
Settings are merged and overridden in the following order (from highest to lowest priority):
1. **Command Line Arguments**
2. **Local Configuration File** (`.ltreerc` or `pyproject.toml`)
3. **Default Settings**

### Examples

#### `.ltreerc` (JSON)
Create a `.ltreerc` file in your project root:
```json
{
  "theme": "nerd",
  "size": true,
  "human": true,
  "dirs_first": true,
  "ex_dirs": ["dist", "build", "target"],
  "ex_ext": [".log", ".tmp"]
}
```

#### `pyproject.toml` (TOML)
Create a `pyproject.toml` file in your project root:
```toml
[tool.ltree]
theme = "emoji"
full_path = true
color = true
size = true
add_dirs = ["output", "temp"]
```

### Supported Configuration Keys
All command-line flags can be configured in your settings file:
- Booleans & Strings:
  - theme: "emoji", "nerd", or "none"
  - color, size, human, all (show hidden files), dirs_only, full_path, dirs_first, show_ellipsis, no_ignore
- Filter Rules:
  - ex_dirs, ex_files, ex_ext, ex_prefix, add_dirs, add_files

---

## Output Examples

### Standard Text
```text
ltree/
├── ltree/
│   ├── core.py
│   └── exporters.py
├── tests/
└── README.md

Summary:
Visible:   2 directories,   3 files
Total  :   2 directories,   3 files
```

### Rich UI & Nerd Fonts (`-F rich --theme nerd`)
```Text
 ltree/
├──  ltree/
│   ├──  core.py
│   └──  exporters.py
├──  tests/
└──  README.md
```

### Markdown Mode (`-F md`)

- 📂 **ltree/**
  - 🐍 `core.py`
  - 🐍 `exporters.py`
- 📂 **tests/**
- 📖 `README.md`
---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.
