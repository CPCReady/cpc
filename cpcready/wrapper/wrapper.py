# Copyright 2025 David CH.F (destroyer)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

"""
CPCReady Environment - Crea un entorno de proyecto local para comandos cpc.

Similar a virtualenv de Python, permite ejecutar comandos sin el prefijo 'cpc'.
Compatible con Windows, Linux y macOS.
"""

import click
import os
import stat
import platform
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from cpcready.utils.click_custom import CustomCommand, CustomGroup
from cpcready.utils.console import ok, warn, error, blank_line
from cpcready.utils.version import add_version_option_to_group
from cpcready.utils.update import show_update_notification

console = Console()

# Detectar sistema operativo
IS_WINDOWS = platform.system() == 'Windows'
IS_POSIX = platform.system() in ['Linux', 'Darwin']  # Linux o macOS


# Lista de comandos disponibles para crear wrappers
AVAILABLE_COMMANDS = [
    'cat', 'disc', 'drive', 'emu', 'era', 'filextr',
    'list', 'mode', 'model', 'ren', 'run', 'rvm', 
    'save', 'user', 'sysinfo', 'a', 'b'
]


@add_version_option_to_group
@click.group(cls=CustomGroup, help="Create and manage CPCReady project environments.", 
             invoke_without_command=True, show_banner=True)
@click.pass_context
def wrapper(ctx):
    """CPCReady Environment - Project environment manager."""
    show_update_notification()
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _create_windows_scripts(bin_dir, project_dir, project_name):
    """Crear scripts para Windows (.bat y .ps1)."""
    created_scripts = []
    
    # Crear scripts .bat para cada comando
    for cmd in AVAILABLE_COMMANDS:
        bat_script = bin_dir / f"{cmd}.bat"
        bat_content = f"""@echo off
REM CPCReady Environment for '{cmd}' command
REM Auto-generated - do not edit manually

cpc-{cmd} %*
"""
        bat_script.write_text(bat_content)
        created_scripts.append(f"{cmd}.bat")
    
    # Crear activate.bat
    activate_bat = bin_dir / "activate.bat"
    activate_bat_content = f"""@echo off
REM CPCReady Environment activation script for Windows CMD
REM Usage: activate.bat

if defined CPCREADY_WRAPPER_PATH (
    echo WARNING: CPCReady Environment already activated
    echo   Current: %CPCREADY_PROJECT_ROOT%
    echo   Run 'deactivate' first to switch projects
    exit /b 1
)

set "CPCREADY_WRAPPER_PATH={bin_dir.absolute()}"
set "CPCREADY_PROJECT_ROOT={project_dir.absolute()}"
set "_OLD_PATH=%PATH%"
set "PATH={bin_dir.absolute()};%PATH%"

echo CPCReady Environment activated: {project_name}
echo   Commands available: {', '.join(AVAILABLE_COMMANDS[:5])}...
echo   To deactivate: deactivate
"""
    activate_bat.write_text(activate_bat_content)
    
    # Crear deactivate.bat
    deactivate_bat = bin_dir / "deactivate.bat"
    deactivate_bat_content = """@echo off
REM CPCReady Environment deactivation script

if not defined CPCREADY_WRAPPER_PATH (
    echo
    echo No CPCReady Environment is currently activated
    echo
    exit /b 1
)

set "PATH=%_OLD_PATH%"
set "CPCREADY_WRAPPER_PATH="
set "CPCREADY_PROJECT_ROOT="
set "_OLD_PATH="

echo CPCReady Environment deactivated
"""
    deactivate_bat.write_text(deactivate_bat_content)
    
    # Crear activate.ps1 para PowerShell
    activate_ps1 = bin_dir / "activate.ps1"
    activate_ps1_content = f"""# CPCReady Environment activation script for PowerShell
# Usage: . .\\bin\\activate.ps1  (or: . .\\bin\\activate)

if ($env:CPCREADY_WRAPPER_PATH) {{
    Write-Host ""
    Write-Host "WARNING: CPCReady Environment already activated" -ForegroundColor Yellow
    Write-Host "  Current: $env:CPCREADY_PROJECT_ROOT"
    Write-Host "  Run 'deactivate' first to switch projects"
    Write-Host ""
    return
}}

$env:CPCREADY_WRAPPER_PATH = "{bin_dir.absolute()}"
$env:CPCREADY_PROJECT_ROOT = "{project_dir.absolute()}"
$env:_OLD_PATH = $env:PATH
$env:PATH = "{bin_dir.absolute()};$env:PATH"

function global:deactivate {{
    $env:PATH = $env:_OLD_PATH
    Remove-Item Env:CPCREADY_WRAPPER_PATH
    Remove-Item Env:CPCREADY_PROJECT_ROOT
    Remove-Item Env:_OLD_PATH
    Remove-Item Function:deactivate
    Write-Host "CPCReady Environment deactivated" -ForegroundColor Green
}}
Write-Host ""
Write-Host " CPCReady Environment activated: {project_name}" -ForegroundColor Green
Write-Host "  Commands available: {', '.join(AVAILABLE_COMMANDS[:5])}..."
Write-Host "  To deactivate: deactivate"
Write-Host ""
"""
    activate_ps1.write_text(activate_ps1_content)
    
    return created_scripts


def _create_posix_scripts(bin_dir, project_dir, project_name):
    """Crear scripts para Linux/macOS (bash)."""
    created_scripts = []
    
    # Crear scripts bash para cada comando
    for cmd in AVAILABLE_COMMANDS:
        script_path = bin_dir / cmd
        script_content = f"""#!/bin/bash
# CPCReady Environment for '{cmd}' command
# Auto-generated - do not edit manually

exec cpc {cmd} "$@"
"""
        script_path.write_text(script_content)
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        created_scripts.append(cmd)
    
    # Crear script de activación bash
    activate_script = bin_dir / "activate"
    activate_content = f"""# Source this file to activate CPCReady Environment
    # Usage: source bin/activate

    # Check if already activated
    if [ -n "$CPCREADY_WRAPPER_PATH" ]; then
        echo
        echo "\033[1;33m🟡 CPCReady Environment already activated\033[0m"        
        echo "\033[1;33m   Current: $CPCREADY_PROJECT_ROOT\033[0m"
        echo "\033[1;33m   Run 'deactivate' first to switch projects\033[0m"
        echo ""
        echo "\033[1;33mReady\033[0m"
        echo
        return 1
    fi
    echo
    echo
    echo "\033[1;33m  ░██████  ░█████████    ░██████  ░█████████                               ░██            \033[0m"
    echo "\033[1;33m ░██   ░██ ░██     ░██  ░██   ░██ ░██     ░██                              ░██            \033[0m"
    echo "\033[1;33m░██        ░██     ░██ ░██        ░██     ░██  ░███████   ░██████    ░████████ ░██    ░██ \033[0m"
    echo "\033[1;33m░██        ░█████████  ░██        ░█████████  ░██    ░██       ░██  ░██    ░██ ░██    ░██ \033[0m"
    echo "\033[1;33m░██        ░██         ░██        ░██   ░██   ░█████████  ░███████  ░██    ░██ ░██    ░██ \033[0m"
    echo "\033[1;33m ░██   ░██ ░██          ░██   ░██ ░██    ░██  ░██        ░██   ░██  ░██   ░███ ░██   ░███ \033[0m"
    echo "\033[1;33m  ░██████  ░██           ░██████  ░██     ░██  ░███████   ░█████░██  ░█████░██  ░█████░██ \033[0m"
    echo "\033[1;33m                                                                                      ░██ \033[0m"
    echo "\033[1;33m                                                                                 ░███████  \033[0m"

    export CPCREADY_WRAPPER_PATH="{bin_dir.absolute()}"
    export CPCREADY_PROJECT_ROOT="{project_dir.absolute()}"

# Save original PS1
export _OLD_CPCREADY_PS1="$PS1"

# Add bin directory to PATH
if [[ ":$PATH:" != *":{bin_dir.absolute()}:"* ]]; then
    export PATH="{bin_dir.absolute()}:$PATH"
fi

# Set prompt to indicate wrapper is active
export PS1="(🟥🟩🟦) $PS1"
    echo
    echo "\033[1;32m🟢 CPCReady Environment activated: {project_name}\033[0m"
    echo "\033[1;32m   Commands available without 'cpc' prefix: {', '.join(AVAILABLE_COMMANDS[:5])}...\033[0m"
    echo "\033[1;32m   To deactivate: deactivate\033[0m"
    echo ""
    echo "\033[1;33mReady\033[0m"
    echo

# Function to deactivate
deactivate() {{
    # Remove bin directory from PATH
    export PATH=$(echo "$PATH" | sed -e "s|{bin_dir.absolute()}:||g")
    
    # Restore original prompt
    if [ -n "$_OLD_CPCREADY_PS1" ]; then
        export PS1="$_OLD_CPCREADY_PS1"
        unset _OLD_CPCREADY_PS1
    fi
    
    # Unset variables
    unset CPCREADY_WRAPPER_PATH
    unset CPCREADY_PROJECT_ROOT
    
    # Remove deactivate function
    unset -f deactivate
    echo
    echo "🟢 CPCReady Environment deactivated"
    echo
}}
"""
    activate_script.write_text(activate_content)
    
    return created_scripts


@wrapper.command(cls=CustomCommand)
@click.option("--force", is_flag=True, help="Overwrite existing environment")
def create(force):
    """Create a new CPCReady project environment.
    
    This creates a local 'bin' directory with wrapper scripts for all cpc commands,
    allowing you to use them without the 'cpc' prefix.
    
    Compatible with Windows (CMD/PowerShell), Linux and macOS.
    
    Examples:
        cpc environment create          # Create in current directory
    """
    # Determinar el directorio del proyecto
    name = ".cpcready"  # Nombre del directorio por defecto
    if name == ".":
        project_dir = Path.cwd()
        project_name = project_dir.name
    else:
        project_dir = Path.cwd() / name
        project_name = name
        
    bin_dir = project_dir / "bin"
    
    blank_line(1)
    
    # Verificar si ya existe
    if bin_dir.exists() and not force:
        warn(f"Environment already exists in '{project_dir}'")
        console.print(f"   Use --force to overwrite")
        blank_line(1)
        return
    
    # Crear directorio del proyecto si no existe
    project_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(exist_ok=True)
    
    # Crear scripts según el sistema operativo
    if IS_WINDOWS:
        created_scripts = _create_windows_scripts(bin_dir, project_dir, project_name)
        os_name = "Windows"
        activate_cmd = "bin\\activate.bat (CMD) or . .\\bin\\activate.ps1 (PowerShell)"
    else:
        created_scripts = _create_posix_scripts(bin_dir, project_dir, project_name)
        os_name = "Linux/macOS"
        activate_cmd = "source bin/activate"
    
    # Crear archivo .gitignore si no existe
    gitignore_path = project_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_content = """# CPCReady Environment
bin/

# DSK files
*.dsk
*.DSK

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
"""
        gitignore_path.write_text(gitignore_content)
    
    ok(f"CPCReady Environment created in '{project_dir}' ({os_name})")
    blank_line(1)
    
    # Mostrar tabla con información
    table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
    table.add_column(style="green", justify="left")
    table.add_column(style="yellow", justify="left")
    
    table.add_row("Environment:", project_name)
    table.add_row("Platform:", os_name)
    table.add_row("Location:", str(project_dir.absolute()))
    table.add_row("Scripts created:", str(len(created_scripts)))
    table.add_row("Activate:", activate_cmd)
    
    console.print(table)
    blank_line(1)
    
    console.print("[cyan]Available commands after activation:[/cyan]")
    console.print(f"  {', '.join(AVAILABLE_COMMANDS)}")
    blank_line(1)
    
    if IS_WINDOWS:
        console.print("[yellow]Windows Usage:[/yellow]")
        console.print("  CMD:        bin\\activate.bat")
        console.print("  PowerShell: . .\\bin\\activate.ps1")
        console.print("  Deactivate: deactivate")
        blank_line(1)


@wrapper.command(cls=CustomCommand)
def info():
    """Show information about the current wrapper environment.
    
    Examples:
        cpc  info          # Info for current directory
        cpc wrapper info myproject  # Info for 'myproject' directory
    """
    # Determinar el directorio del proyecto
    name = ".cpcready"  # Nombre del directorio por defecto
    if name == ".":
        project_dir = Path.cwd()
        project_name = project_dir.name
    else:
        project_dir = Path.cwd() / name
        project_name = name
    
    bin_dir = project_dir / "bin"
    
    blank_line(1)
    
    # Verificar si existe el wrapper
    if not bin_dir.exists():
        error(f"No environment found in '{project_dir}'")
        console.print("   Run 'cpc environment create' to create one")
        blank_line(1)
        return
    
    # Contar scripts
    if IS_WINDOWS:
        scripts = list(bin_dir.glob("*.bat"))
        os_name = "Windows"
    else:
        scripts = [s for s in bin_dir.iterdir() if s.is_file() and s.name != "activate"]
        os_name = "Linux/macOS"
    
    # Verificar si está activado
    is_active = os.environ.get("CPCREADY_WRAPPER_PATH") == str(bin_dir.absolute())
    
    # Mostrar información
    ok(f"CPCReady Environment in '{project_name}' ({os_name})")
    blank_line(1)
    
    table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
    table.add_column(style="green", justify="left")
    table.add_column(style="yellow", justify="left")
    
    table.add_row("Environment:", project_name)
    table.add_row("Platform:", os_name)
    table.add_row("Location:", str(project_dir.absolute()))
    table.add_row("Status:", "✓ Active" if is_active else "○ Inactive")
    table.add_row("Scripts:", str(len(scripts)))
    
    console.print(table)
    blank_line(1)


@wrapper.command(cls=CustomCommand)
@click.argument("name", required=False, default=".")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def remove(yes):
    """Remove a wrapper environment.
    
    This deletes the 'bin' directory and all wrapper scripts.
    
    Examples:
        cpc wrapper remove          # Remove from current directory
        cpc wrapper remove myproject  # Remove from 'myproject' directory
    """
    # Determinar el directorio del proyecto
    name = ".cpcready"  # Nombre del directorio por defecto
    if name == ".":
        project_dir = Path.cwd()
        project_name = project_dir.name
    else:
        project_dir = Path.cwd() / name
        project_name = name
    
    bin_dir = project_dir / "bin"
    
    blank_line(1)
    
    # Verificar si existe
    if not bin_dir.exists():
        error(f"No environment found in '{project_dir}'")
        blank_line(1)
        return
    
    # Verificar si está activado
    if os.environ.get("CPCREADY_WRAPPER_PATH") == str(bin_dir.absolute()):
        warn("Warning: This environment is currently active")
        console.print("   You should deactivate it first")
        blank_line(1)
        if not yes:
            if not click.confirm("Do you want to continue anyway?"):
                console.print("Cancelled.")
                blank_line(1)
                return
    
    # Confirmar eliminación
    if not yes:
        console.print(f"[yellow]This will delete the environment directory in '{project_dir}'[/yellow]")
        if not click.confirm("Are you sure?"):
            console.print("Cancelled.")
            blank_line(1)
            return
    
    # Eliminar directorio bin
    import shutil
    shutil.rmtree(bin_dir)
    
    ok(f"Environment removed from '{project_dir}'")
    blank_line(1)
