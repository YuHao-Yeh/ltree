# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.0] - 2026-05-26

### Added

- **Local Configuration Support**: Introduced automatic settings climbing search for local `.ltreerc` (JSON) and `pyproject.toml` (under `[tool.ltree]`) files.
- **Render Pipeline Overhaul**: Migrated `RichRenderer` from raw markup strings to a structured `rich.text.Text` pipeline to prevent style leakages into standard text/markdown exporters.
- **OOP Theme Abstraction**: Decoupled icon and style mapping into a pluggable registry-based `ThemeManager` with `EmojiTheme`, `NerdTheme`, and `NoTheme` classes.
- **Extended System Metadata**: Expanded `TreeNode` to capture rich filesystem metadata including symlink status, file permissions, executability, and lowercase file extensions.
- **Robust Quality Control**: Integrated comprehensive pre-commit hooks (checks, Ruff formatting/linting, and automated testing) and reached **100% unit test coverage**.

### Changed

- **Memory Optimization**: Configured core model dataclasses (`Stats` and `TreeNode`) with `slots=True` to minimize memory footprint during deep scanning.
- **Scanner Resilience**: Improved system root path (e.g., `/` or `C:\`) name fallback and added generic `OSError` catching to prevent scanner runtime crashes.
- **Console TTY Handling**: Refined TTY stream detection in Rich rendering and imposed a default width of 1000 characters for file-stream outputs.

---

## [0.1.0] - 2026-05-08

### Added

- **Initial Release**: Fast, customizable CLI tool to visualize directory structures.
- **Multi-Format Exporters**: Supported console text, Markdown list, Markdown code-block, and JSON exports.
- **Advanced Filtering**: Supported file/folder exclusions via extensions, prefixes, wildcards, regular expressions, and automated `.gitignore` rules loading.
- **Display Configurations**: Included toggles for depth limit (`-L`), full path prefix, colored output, directory-first listing, and classic or human-readable file sizes.
- **Theme Support**: Integrated initial support for Emoji, Nerd Font, and Plain Text (none) icon themes.

[Unreleased]: https://github.com/YuHao-Yeh/ltree/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/YuHao-Yeh/ltree/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/YuHao-Yeh/ltree/releases/tag/v0.1.0
