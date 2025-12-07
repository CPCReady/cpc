# Changelog

## [0.1.1] - 2025-12-6

### Added

## [0.1.0] - 2025-11-23
- chore: cambios de comando para ser mas funcionalidades. Añadimos 'cpc-' como prefix
- chore: añadimos que version muestro urls del proyecto: doc,issue y repo
- chore: cambiamos mostrar como actualizar
- chore: desactivamos comando m4 hasta que este funcional 100%
- test: activamos test para astro
- chore: cambios en documentacion

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
