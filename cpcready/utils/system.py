# Copyright (C) 2025 David CH.F (destroyer)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import subprocess
import click
from cpcready.utils import console
from pathlib import Path

def process_dsk_name(disc_image: str):
    path = Path(disc_image)

    # Asegurarse de que tenga la extensión .dsk
    if path.suffix.lower() != ".dsk":
        path = path.with_suffix(".dsk")

    # Obtener la ruta absoluta
    if len(path.parts) == 1:
        # Solo nombre de archivo - usar directorio actual
        absolute_path = Path.cwd() / path
    else:
        # Incluye una ruta (relativa o absoluta)
        if path.is_absolute():
            absolute_path = path
        else:
            absolute_path = path.resolve()

    # Crear el directorio si no existe
    parent_directory = absolute_path.parent
    if not parent_directory.exists():
        parent_directory.mkdir(parents=True, exist_ok=True)

    return absolute_path

def process_cdt_name(disc_image: str):
    path = Path(disc_image)
    
    # Asegurarse de que tenga la extensión .cdt
    if path.suffix.lower() != ".cdt":
        path = path.with_suffix(".cdt")
    
    # Obtener la ruta absoluta
    if len(path.parts) == 1:
        # Solo nombre de archivo - usar directorio actual
        absolute_path = Path.cwd() / path
    else:
        # Incluye una ruta (relativa o absoluta)
        if path.is_absolute():
            absolute_path = path
        else:
            absolute_path = path.resolve()

    # Crear el directorio si no existe
    parent_directory = absolute_path.parent
    if not parent_directory.exists():
        parent_directory.mkdir(parents=True, exist_ok=True)
    
    return absolute_path

def run_command(cmd, show_output=True, check=True):
    """
    Ejecuta un comando del sistema y muestra su salida en tiempo real.

    Args:
        cmd (str | list): Comando a ejecutar (por ejemplo, 'ls -l' o ['ls', '-l'])
        show_output (bool): Si True, muestra la salida directamente en consola.
        check (bool): Si True, lanza excepción si el comando devuelve error.

    Returns:
        subprocess.CompletedProcess: Resultado del comando.
    """
    console.debug(f"[DEBUG] Ejecutando comando: {cmd}")

    # Si se pasa como string, usar shell=True (para pipes o redirecciones)
    use_shell = isinstance(cmd, str)

    process = subprocess.Popen(
        cmd,
        shell=use_shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output_lines = []
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if show_output:
            click.echo(line)
        output_lines.append(line)

    process.wait()

    if check and process.returncode != 0:
        console.error(f"[ERROR] Comando falló con código {process.returncode}")
        raise subprocess.CalledProcessError(process.returncode, cmd)

    console.ok(f"[OK] Comando completado con código {process.returncode}")
    return subprocess.CompletedProcess(cmd, process.returncode, "\n".join(output_lines), "")
