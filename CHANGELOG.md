# Changelog

All notable changes to CPCReady will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for 1.1.0
- PyPI package distribution
- Extended documentation with video tutorials
- Performance optimizations
- Batch file operations

## [1.0.0] - 2025-11-23

### Added
- Initial release
- Drive management (A/B drives)
- Disk operations (create, list, catalog)
- File operations (save, extract, rename, delete)
- CP/M user area support (0-15)
- Emulator integration (RetroVirtualMachine)
- CPC configuration (model, video mode)
- GUI configuration tool (PySide6)
- TOML-based configuration system
- Command-line interface with multiple commands

### Features
- `cpc drive` - Manage virtual drives
- `cpc disc` - Create and manage disk images
- `cpc cat` - List files on disk
- `cpc save` - Save files to disk (ASCII, Binary, Program)
- `cpc list` - List BASIC programs
- `cpc era` - Delete files
- `cpc ren` - Rename files
- `cpc filextr` - Extract files
- `cpc run` - Launch emulator
- `cpc user` - Manage CP/M user numbers
- `cpc model` - Set CPC model (464/664/6128)
- `cpc mode` - Set video mode


[Unreleased]: https://github.com/CPCReady/cpc/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/CPCReady/cpc/releases/tag/v1.0.0
