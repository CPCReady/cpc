# CPCReady

<p align="center">
  <img src="Resources/icon_512x512.png" alt="CPCReady Logo" width="300"/>
</p>

[![Release](https://img.shields.io/github/v/release/CPCReady/cpc)](https://github.com/CPCReady/cpc/releases)
[![Build](https://img.shields.io/github/actions/workflow/status/CPCReady/cpc/release.yml)](https://github.com/CPCReady/cpc/actions)
[![Python](https://img.shields.io/badge/python-3.13+-blue)](https://www.python.org)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue)](https://python-poetry.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.md)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A command-line toolchain for managing Amstrad CPC disk images (.DSK files) and running them in emulators.

## Overview

CPCReady provides a comprehensive set of tools to work with Amstrad CPC virtual disks, managing files, and launching emulators with the correct configuration.

## Features

- **Disk Management**: Create, list, and manage .DSK disk images
- **Virtual Drives**: Simulate A and B drives with disk insertion/ejection
- **File Operations**: Save, list, extract, rename, and delete files on disks
- **CP/M User Areas**: Support for user numbers (0-15) like real CP/M systems
- **Emulator Integration**: Launch RetroVirtualMachine with automatic configuration
- **CPC Configuration**: Manage CPC model (464/664/6128), video mode, and settings
- **GUI Configuration**: PySide6-based graphical configuration editor

## Installation

### Prerequisites

- Python 3.13+
- Poetry (dependency manager)

### Install with Poetry

```bash
poetry install
```

## Main Commands

### Drive Management

```bash
cpc drive A <disk.dsk>    # Insert disk into drive A
cpc drive B <disk.dsk>    # Insert disk into drive B
cpc drive status          # Show current drive status
cpc drive eject A         # Eject disk from drive A
```

### Disk Operations

```bash
cpc disc <disk.dsk>       # Create or select a disk
cpc cat                   # List files on current disk
cpc save <file> [type]    # Save file to disk (a/b/p types)
cpc era <file>            # Delete file from disk
cpc ren <old> <new>       # Rename file on disk
```

### File Management

```bash
cpc list <file>           # List BASIC program
cpc filextr <file>        # Extract file from disk
```

### System Configuration

```bash
cpc user <0-15>           # Set CP/M user number
cpc model <464|664|6128>  # Set CPC model
cpc mode <0|1|2>          # Set video mode
cpc settings              # Show current settings
cpc configweb             # Launch GUI configuration
```

### Emulator

```bash
cpc run [file]            # Launch emulator with current disk
cpc run [file] -A         # Run from drive A
cpc run [file] -B         # Run from drive B
```

## File Types

When saving files, you can specify:

- `a` - ASCII/text file (no AMSDOS header)
- `b` - Binary file (requires load/exec addresses)
- `p` - Program file (preserves existing header)

Example:
```bash
cpc save game.bin b 0x4000 0x4000    # Binary at address 0x4000
cpc save data.txt a                  # ASCII file
```

## Configuration

Configuration is stored in TOML format at:
`~/.config/cpcready/cpcready.toml`

Structure:
```toml
[drive]
drive_a = "/path/to/disk.dsk"
drive_b = ""
selected_drive = "A"

[emulator]
default = "RetroVirtualMachine"
retro_virtual_machine_path = "/Applications/Retro Virtual Machine 2.app"

[system]
user = 0        # CP/M user area
model = "6128"  # CPC model
mode = 1        # Video mode
```

## Project Structure

```
cpcready/
├── cli.py              # Main CLI entry point
├── drive/              # Drive management (A/B)
├── disc/               # Disk operations
├── save/               # Save files to disk
├── list/               # List BASIC programs
├── cat/                # Catalog disk contents
├── era/                # Delete files
├── ren/                # Rename files
├── filextr/            # Extract files
├── run/                # Launch emulator
├── user/               # CP/M user management
├── model/              # CPC model configuration
├── mode/               # Video mode configuration
├── pydsk/              # DSK file format library
└── utils/              # Utilities and helpers

```

## Development

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Run in development mode
poetry run cpc <command>
```

## License

Apache License 2.0 - See [LICENSE.md](LICENSE.md) for details.

---

**Note**: This tool is designed for Amstrad CPC enthusiasts and retro computing hobbyists.
