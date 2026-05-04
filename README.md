# list-tree-tool

A customizable CLI tool to display directory structures in a tree-like format.

## Features

- Tree-style directory visualization
- Flexible exclude rules (dirs, files, extensions, prefixes)
- Depth limiting (`--max-depth` or `-L`)
- File & directory statistics
- Optional colored output
- Subtree caching for improved performance

---

## Installation

### Using pip (local development)

```bash
pip install -e .
```

---

## Usage
```bash
list-tree [path] [options]
```

---

## Example:
```bash
list-tree . -o -
```

---

## Options

| Option              | Description                        |
| ------------------- | ---------------------------------- |
| `-o`, `--output`    | Output file (use `-` for stdout)   |
| `--no-color`        | Disable colored output             |
| `--ex-dirs`         | Exclude directories                |
| `--ex-files`        | Exclude files (supports wildcard)  |
| `--add-dirs`        | Re-include directories             |
| `--add-files`       | Re-include files                   |
| `--ex-ext`          | Exclude file extensions            |
| `--ex-prefix`       | Exclude by prefix                  |
| `-d`, `--dirs-only` | Show only directories              |
| `-L`, `--max-depth` | Limit directory depth              |
| `--dirs-first`      | List directories before files      |
| `--show-ellipsis`   | Show "..." when depth is truncated |

---

## Output Example
```
project/
├── src/
│   ├── main.py
│   └── utils.py
└── README.md
```

---

## Development
```bash
git clone <repo>
cd list-tree-tool
pip install -e .
```

