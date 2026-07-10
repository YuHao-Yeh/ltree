# ltree

<div align="center">
  <!-- Metadata -->
  <p>
    <a href="https://pypi.org/project/ltree-cli/">
      <img src="https://img.shields.io/pypi/v/ltree-cli.svg" alt="PyPI version">
    </a>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/python-%3E%3D3.10-blue" alt="Python Version">
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
    </a>
  </p>
  <!-- CI & Coverage -->
  <p>
    <a href="https://github.com/YuHao-Yeh/ltree/actions">
      <img src="https://github.com/YuHao-Yeh/ltree/actions/workflows/tests.yml/badge.svg" alt="Tests">
    </a>
    <a href="https://coveralls.io/github/YuHao-Yeh/ltree">
      <img src="https://coveralls.io/repos/github/YuHao-Yeh/ltree/badge.svg" alt="Coverage">
    </a>
  </p>
</div>

**ltree** is a fast, highly customizable CLI utility used to visualize directory structures in a tree diagram. It features beautiful *Rich UI* console formatting, robust icon theme support (*Nerd Font / Emoji*), detailed metrics tracking, and versatile exporters (JSON, YAML, Markdown, HTML, and Graphviz).

```bash
>>> ltree tree ltree/core --no-mtime --no-git --no-perm
  📂 core/
  ├── 🐍 __init__.py
  ├── 🐍 config.py
  ├── 📂 filters/
  │   ├── 🐍 __init__.py
  │   ├── 🐍 base.py
  │   ├── 🐍 depth.py
  │   ├── 🐍 folders.py
  │   ├── 🐍 pipeline.py
  │   └── 🐍 sorting.py
  ├── 📂 metadata/
  │   ├── 🐍 __init__.py
  │   ├── 🐍 base.py
  │   ├── 🐍 code.py
  │   ├── 🐍 filesystem.py
  │   ├── 🐍 git.py
  │   ├── 🐍 models.py
  │   ├── 🐍 project.py
  │   ├── 🐍 registry.py
  │   └── 🐍 time.py
  ├── 🐍 models.py
  ├── 📂 scanners/
  │   ├── 🐍 __init__.py
  │   ├── 🐍 aggregation.py
  │   ├── 🐍 filters.py
  │   ├── 🐍 scanner.py
  │   ├── 🐍 sorting.py
  │   ├── 🐍 subtree.py
  │   └── 🐍 traversal.py
  └── 🐍 utils.py

Summary:
Visible:   3 directories,  26 files
Total  :   3 directories,  26 files
```

---

## Installation

You can install **ltree** directly from PyPI:

```bash
# Using pip
pip install ltree-cli

# Or using uv
uv pip install ltree-cli
```

For local development or source installations:

```bash
# Clone the repository
git clone https://github.com/YuHao-Yeh/ltree.git
cd ltree

# Install in editable mode using uv
uv pip install -e .

# Or using standard pip
pip install -e .
```

---

## VS Code Extension

**ltree** now comes with an official VS Code companion!

- **Quick Action**: Right-click any workspace file or folder in the explorer sidebar to generate a structure diagram.
- **Multiple Formats**: Select your desired generation format (Markdown List, JSON, Plain Text, or Markdown Code Blocks).
- **Customizable**: Seamlessly pass any CLI arguments directly from your VS Code Settings or input boxes.
- **Convenience**: The generated tree diagram will automatically save to your system **clipboard** for instant sharing.

To get started, check the [ltree-vscode](./ltree-vscode) directory for detailed installation instructions.

---

## Command-Line Usage

**ltree** organizes its functionality through logical subcommands. \
*Run `ltree --help` to inspect the full list of available subcommands.*

### 1. The `tree` Subcommand

Generate a directory tree diagram with advanced filtering, metadata inspection, and custom outputs.

> [!TIP]
> Executing `ltree` directly with a directory path or without any arguments automatically falls back to invoking the `tree` subcommand.

```bash
# Explicitly generate a tree
ltree tree [path] [options]

# Shortcut fallback (automatically executes the 'tree' subcommand)
ltree [path] [options]
```

#### Command Options

*Run `ltree tree --help` to see the full list of available parameters.*

<details>
<summary><b>View Full Parameter List</b></summary>

#### Basic Options

| Argument | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `start_path` | | `.` | Starting directory path. |
| `--output` | `-o` | `-` | Output file name. Use `-` for standard outout (stdout). |

#### Formatting & Theme
| Argument | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--format` | `-F` | `text` | Output format. Choices: `text`, `json`, `yaml`, `md`, `markdown`, `block`, `rich`, `html`, `graphviz`. |
| `--theme` | | `emoji` |	Default icon style. Choices: `emoji`, `nerd`, `none`. |
| `--color`, `--no-color` | `-c` | *Auto* | Toggles ANSI colored output. |

#### Metadata Flags
| Argument | Short | Description |
| :--- | :--- | :--- |
| `--perm`, `--no-perm` | | Toggle filesystem permissions (e.g., `drwxr-xr-x`). Default: active. |
| `--git`, `--no-git` | | Toggle git tracking and modification states. Default: active. |
| `--size`, `--no-size` | `-s` | Display file and aggregated directory sizes in bytes. |
| `--human` | `-H` | Formats size displays to human-readable scales (e.g., 1.5 K, 2.0 M). |
| `--mtime`, `--no-mtime` | | Toggle modification timestamps. Default: active. |
| `--code`, `--no-code` | | Toggle lightweight programming language. |
| `--project`, `--no-project` | | Toggle configurations parsing for project metadata (e.g., package names and version). |

#### Filtering & Exclusions
| Argument | Short | Description |
| :--- | :--- | :--- |
| `--all` | `-a` | Process hidden files and directories (starting with `.`). |
| `--dirs-only` | `-d` | Exclude file entries entirely from visualization layout. |
| `--exclude` | `-I` | Exclude paths matchin literal strings or wildcard patterns (e.g., `dist/`, `*.log`). |
| `--include` | `-A` | Re-include paths previously matching an exclusion filter. |
| `--re-ex` | | Exclude paths matching a specific Python regular expression. |
| `--gitignore`, `--no-gitignore` | | Toggle automatic evaluation of `.gitignore` exclusion configurations. |

#### Display Configurations
| Argument | Short | Description |
| :--- | :--- | :--- |
| `--max-depth` | `-L` | Restruct recursive scanning depth to a maximum integer. |
| `--full-path` | `-f` | Print the full relative path prefix instad of just the entry name. |
| `--dirs-first` | | List directories before files. |
| `--ellipsis`| | Render an ellipsis (`...`) showing truncated file statisticss on depth-limited branches. |

</details>

#### Examples

```bash
# Display current directory structure
ltree tree

# Output to console with color
ltree tree . -o - --color

# Save tree to a file
ltree tree /path/to/dir -o tree.txt

# For more help
ltree tree --help
```

#### Quick Configuration Presets

<details>
<summary>Click to expand configuration presets</summary>

| Use Case | Command |
| :--- | :--- |
| Export structure as JSON | `ltree tree -F json -o data.json` |
| Markdown List layout| `ltree tree -F md -o report.md` |
| Markdown Text Block layout| `ltree tree -F block -o report.md` |
| Restrict sacn depth | `ltree tree -L 2 --ellipsis` |
| Filter by Pattern | `ltree tree -I *.log -I *.tmp` |
| Filter by Regex | `ltree tree --re-ex "test_.*\.py"` |
| Directories-only Visualization | `ltree tree -d --dirs-first` |
| File size metrics | `ltree tree -s -H` |
| Rich + Nerd Fonts | `ltree tree . -F rich --theme nerd` |

</details>


### 2. The `theme` Subcommand

Discovers, lists, or previews available icon mappings.

```bash
ltree theme [action] [argument]
```

#### Actions & Options

<details>
<summary>Click to expand action details</summary>

| Action | Argument | Default | Description |
| :--- | :--- | :--- | :--- |
| `list` | | | Lists all registered icon themes with descriptions. |
| `preview` | theme_name | | Renders directory, file, and symlink mockups for a specific theme. Choices: `emoji`, `nerd`, `none`. |

</details>

#### Examples

```bash
# Discover what themes are built-in
ltree theme list

# Verify how Nerd Font glyphs render on your terminal environment
ltree theme preview nerd
```

---

### 3. The `config` Subcommand

Manage configuration files and  setting profiles across workspaces.

```bash
ltree config [action] [start_path]
```

#### Actions & Options

<details>
<summary>Click to expand action details</summary>

| Action | Argument | Default | Description |
| :--- | :--- | :--- | :--- |
| `show` | [start_path] | `.` | Resolves configurations at `start_path` (respecting settings hierarchies) and prints active configuration properties. |
| `locate` | [start_path] | `.` | Searches upwards from `start_path` and prints the locations of discovered `.ltreerc` or `pyproject.toml` files. |
| `validate` | [start_path] | `.` | Inspects and validates the formatting syntax of setting profiles found in the recursive path. |

</details>

#### Examples

```bash
# Print the merged configuration properties currently in effect.
ltree config show [start_path]

# Trace and locate setting files up through parent directories
ltree config locate [start_path]

# Validate setting syntaxes and formats for setting profiles
ltree config validate [start_path]
```

---

## Configuration

You can store configuration options in local files to aviod passing them manually on every run. `ltree` automatically scan upwards for the following configuration targets:

- `.ltreerc` (JSON formatted configuration)
- `pyproject.toml` (defined under the `[tool.ltree]` section)

### Precedence Priority
Settings are merged and overridden with the following priority order:
1. Command Line Arguments
2. Local Configuration File (`.ltreerc` or `pyproject.toml`)
3. Global Default Configurations

### Examples

#### `.ltreerc` (JSON)
```json
{
  "theme": "nerd",
  "size": true,
  "human": true,
  "dirs_first": true,
  "exclude": ["dist", "build", "target", "*.log", "*.tmp"]
}
```

#### `pyproject.toml` (TOML)
```toml
[tool.ltree]
theme = "emoji"
full_path = true
color = true
size = true
include = ["output", "temp"]
```

---

## Output Examples

### Plain Text (`-F text`)

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
├──  tests
└──  README.md

Summary:
Visible:   2 directories,   3 files
Total  :   2 directories,   3 files
```

### Markdown Lists (`-F md`)

- 📂 **ltree/**
  - 🐍 `core.py`
  - 🐍 `exporters.py`
- 📂 **tests/**
- 📖 `README.md`

---

## System Architecture

`ltree` is designed as a modular pipeline, where each stage has a single responsibility.

```text
              CLI
               │
               ▼
    ┌──────────────────────┐
    │     Configuration    │
    └──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │       Scanner        │
    │ • Traversal          │
    │ • Filters            │
    │ • Metadata Providers │
    └──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │      Tree Model      │
    └──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │      Serializer      │
    └──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │       Renderer       │
    └──────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │       Exporter       │
    └──────────────────────┘
               │
               ▼
        Console / File
```

- **Configuration** – Resolves command-line arguments and configuration files into a unified `TreeConfig`.
- **Scanner** – Traverses the filesystem, applies filters, and collects metadata.
- **Tree Model** – Stores the scanned directory hierarchy in memory.
- **Serializer** – Converts the tree model into a renderer-independent representation.
- **Renderer** – Produces output in the selected format.
- **Exporter** – Writes the rendered output to the console or a file.

Each layer has a single responsibility and can be extended independently, making ltree easy to customize and maintain.


---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.
