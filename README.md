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

**ltree** is a fast, customizable CLI tool to visualize directory structures in tree diagram. It supports multiple output formats and provides detailed statistics.

```bash
>>> ltree .
ltree/
├── ltree/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── constants.py
│   ├── core.py
│   ├── exporters.py
│   ├── schema.py
│   └── utils.py
├── output/
│   ├── tree.json
│   ├── tree.md
│   └── tree.txt
├── pyproject.toml
├── README.md
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_core.py
│   ├── test_exporters.py
│   └── test_utils.py
└── uv.lock

Summary:
Visible:   3 directories,  20 files
Total  :   3 directories,  20 files
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

### Output Formatting
| Argument | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--format` | `-F` | `text` | Choices: `text`, `json`, `md`, `markdown`, `block`. |
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
| `--re-ex` | | Exclude paths matching a regular expression.
| `--no-ignore` | | Disable automatic exclusion based on .gitignore (enabled by default).
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

### Markdown Mode (`-F md`)

- 📂 **ltree/**
  - 📄 `core.py`
  - 📄 `exporters.py`
- 📂 **tests/**
- 📄 `README.md`
---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.
