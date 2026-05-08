# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.0] - 2026-05-08

### Added

- **Right-click context menu** integration in the VS Code File Explorer.
- **Multiple format support** for tree generation:
  - Plain Text
  - JSON
  - Markdown List
  - Markdown Block
- **Custom Arguments Support**: New "Copy with Custom Arguments..." option to dynamically select format and input CLI flags at runtime.
- **Smart Path Context**: Automatically determines the target directory whether a file or a folder is selected.
- **Extension Settings**: 
  - `ltree.pythonPath`: Allows users to specify their Python interpreter.
  - `ltree.args`: Support for passing additional CLI arguments (e.g., `--all`, `--max-depth`).
- **Encoding Support**: Forced UTF-8 encoding for command execution to ensure Unicode tree characters display correctly on Windows.

[Unreleased]: https://github.com/YuHao-Yeh/ltree/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YuHao-Yeh/ltree/releases/tag/v0.1.0