# ltree

`ltree-vscode` is the official VS Code companion for the [ltree](https://github.com/YuHao-Yeh/ltree) CLI tool. It allows you to quickly generate and copy directory tree structures directly from your file explorer.

## Features

- **Right-Click Integration**: Generate directory trees without leaving the editor.
- **Multiple Formats**: Support for `Text`, `JSON`, `Markdown`, and `Markdown Block`.
- **Smart Path Context**:
    - Right-click a **folder** to scan that folder.
    - Right-click a **file** to scan the directory containing that file.

## Requirements

This extension acts as a wrapper for the `ltree` Python package.

1. **Python 3.10+** must be installed on your system.
2. **ltree package**: Install the core tool from source:
   ```bash
   git clone https://github.com/YuHao-Yeh/ltree.git
   cd ltree
   pip install -e .
   ```

## Extension Settings

This extension contributes the following configuration options:

* `ltree.pythonPath`: Path to your Python executable (e.g., `python`, `python3`, or a full path to a virtual environment's interpreter).
* `ltree.theme`: Choose your default icon theme. Choices: `emoji` (default), `nerd`, or `none`.
* `ltree.showSize`: Enable this to display file/directory sizes in the output. Default is `false`.
* `ltree.dirsFirst`: When enabled, directories will be listed before files. Default is `false`.
* `ltree.args`: Default additional arguments to pass to the `ltree` CLI (e.g., `--all`, `-L 2`).
  *Note: The `-F` (format) argument is handled automatically by the menu options.*

## Usage

1. Open the **Explorer** view in VS Code.
2. Right-click on any file or folder.
3. Select one of the **ltree** options from the context menu.
4. The tree diagram will be generated and copied to your **clipboard** automatically.
5. A notification will appear once the process is complete.

## Known Issues

- If you encounter a `ENOENT` error on Windows, please ensure your `ltree.pythonPath` is correctly set in the settings.

## Release Notes

### 0.2.0
- **Native Settings UI**: Integrated settings for theme, showSize, and dirsFirst directly into VS Code Settings.
- **Security Upgrade**: Migrated backend execution engine to `spawn` for safe parameter parsing and cmd-injection prevention.
- **Improved Parsing**: Added a robust command-line argument splitter for the custom prompt.

### 0.1.0
- Initial release.
- Added right-click menu support for Text, JSON, and Markdown formats.
- Added UTF-8 encoding support for Windows compatibility.

---
**Enjoying ltree?** Check out the [core project on GitHub](https://github.com/YuHao-Yeh/ltree)!
```
