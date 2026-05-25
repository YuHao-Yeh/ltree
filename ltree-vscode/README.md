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

This extension contributes the following settings:

### Added
- **UI Settings Integration**: Added native VS Code settings fields for `theme`, `showSize`, and `dirsFirst`, eliminating the need to manually pass these flags through command-line arguments.
- **Custom Argument Parsing**: Added a safe command-line argument splitter (`splitArguments`) to handle complex input arguments containing quotes and spaces in the custom prompt.

### Changed
- **Execution Engine**: Replaced the shell-dependent `exec` process invocation with `spawn` for executing the CLI tool, resolving potential path formatting anomalies across different OS environments.

### Security
- **Command Injection Prevention**: Migrated away from shell execution to direct process invocation (`spawn`), eliminating potential command injection vulnerabilities arising from crafted workspace directory names or custom arguments.

## Usage

1. Open the **Explorer** view in VS Code.
2. Right-click on any file or folder.
3. Select one of the **ltree** options from the context menu.
4. The tree diagram will be generated and copied to your **clipboard** automatically.
5. A notification will appear once the process is complete.

## Known Issues

- If you encounter a `ENOENT` error on Windows, please ensure your `ltree.pythonPath` is correctly set in the settings.

## Release Notes

### 0.1.0
- Initial release.
- Added right-click menu support for Text, JSON, and Markdown formats.
- Added UTF-8 encoding support for Windows compatibility.

---
**Enjoying ltree?** Check out the [core project on GitHub](https://github.com/YuHao-Yeh/ltree)!
```
