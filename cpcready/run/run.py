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

import click
import psutil
import subprocess
import sys
import time
from pathlib import Path
from cpcready.utils.click_custom import CustomCommand
from cpcready.utils.console import info2, ok, debug, warn, error, message,blank_line,banner
from cpcready.utils.toml_config import ConfigManager
from cpcready.utils.manager import DriveManager


# Nombres posibles del ejecutable RVM
NOMBRES_RVM = [
    "Retro Virtual Machine",
    "retrovirtualmachine",
    "RetroVirtualMachine.exe",
    "retrovirtualmachine.exe"
]


def matar_rvm():
    """Kill all previous RetroVirtualMachine instances."""
    debug("Searching for previous RetroVirtualMachine instances...")
    
    count = 0
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            nombre = proc.info["name"] or ""
            ruta = proc.info["exe"] or ""
            cmd = " ".join(proc.info["cmdline"] or [])

            if any(t.lower() in nombre.lower() for t in NOMBRES_RVM) or \
               any(t.lower() in ruta.lower() for t in NOMBRES_RVM) or \
               any(t.lower() in cmd.lower() for t in NOMBRES_RVM):

                debug(f"Closing: PID {proc.pid} ({nombre})")
                proc.kill()
                proc.wait()
                count += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if count > 0:
        info2(f"Closed {count} RetroVirtualMachine instance(s).")


def lanzar_rvm(ruta_ejecutable, modelo, archivo_dsk, archivo_ejecutar=None):
    """
    Launch RetroVirtualMachine with the specified parameters.
    
    Args:
        ruta_ejecutable: Path to RVM executable or .app
        modelo: CPC model (464, 664, 6128)
        archivo_dsk: DSK file to load
        archivo_ejecutar: File to execute automatically from disk
    """
    # Construir parámetros
    parametros = [f"-b=cpc{modelo}"]
    
    if archivo_dsk:
        parametros.extend(["-i", archivo_dsk])
    
    if archivo_ejecutar:
        # Comando para ejecutar el archivo: run"archivo"\n
        parametros.append(f'-c=run"{archivo_ejecutar}"\\n')
    
    debug(f"Parámetros: {' '.join(parametros)}")
    
    # Detectar si es macOS y la ruta es .app
    if sys.platform == "darwin" and ruta_ejecutable.endswith(".app"):
        # En macOS, usar 'open -a' para aplicaciones .app
        comando = ["open", "-a", ruta_ejecutable, "--args"] + parametros
        # info2(f"Launching: open -a '{ruta_ejecutable}' --args {' '.join(parametros)}")
    else:
        # Windows/Linux o ruta directa al binario
        comando = [ruta_ejecutable] + parametros
        info2(f"Launching: {' '.join(comando)}")
    
    try:
        if sys.platform.startswith("win"):
            # Windows: usar DETACHED_PROCESS para desconectar completamente
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen(
                comando, 
                creationflags=DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        else:
            # Unix/Linux/macOS: usar start_new_session
            subprocess.Popen(
                comando,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        
        ok("RetroVirtualMachine launched successfully.")
        
    except FileNotFoundError:
        error(f"Executable not found: {ruta_ejecutable}")
        error("Check the path in configuration (cpc configweb).")
    except Exception as e:
        error(f"Error launching RetroVirtualMachine: {e}")


@click.command(cls=CustomCommand)
@click.argument("file_to_run", required=False)
@click.option("-A", "--drive-a", is_flag=True, help="Use disk from drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Use disk from drive B")
def run(file_to_run, drive_a, drive_b):
    """Run a file from the selected drive in RetroVirtualMachine.
    
    FILE_TO_RUN: Name of the file to execute from the disk (e.g., DISC, GAME.BAS)
    
    If -A or -B is not specified, uses the currently selected drive.
    The file must exist in the disk of the selected drive.
    """
    
    # Cargar configuración
    config = ConfigManager()
    
    # Obtener modelo CPC de la configuración
    modelo = config.get("system", "model", "6128")
    
    # Obtener ruta del ejecutable RVM
    ruta_rvm = config.get("emulator", "retro_virtual_machine_path", "")
    
    if not ruta_rvm:
        error("RetroVirtualMachine path not configured.")
        error("Run 'cpc configweb' to configure the emulator.")
        return
    
    # Verificar que existe
    if not Path(ruta_rvm).exists():
        error(f"RetroVirtualMachine not found at: {ruta_rvm}")
        error("Check the path in configuration (cpc configweb).")
        return
    
    # Obtener disco de la unidad seleccionada
    drive_manager = DriveManager()
    disc_name = drive_manager.get_disc_name(drive_a, drive_b)
    
    if disc_name is None:
        error("No disk inserted in the selected drive.")
        return
    
    # Determinar letra de unidad
    if drive_a:
        drive_letter = "A"
    elif drive_b:
        drive_letter = "B"
    else:
        # Obtener la unidad seleccionada por defecto
        selected = config.get("drive", "selected_drive", "A")
        drive_letter = selected
    
    blank_line(1)
    info2(f"Using disk from Drive {drive_letter}: {Path(disc_name).name}")
    
    # Si se especificó archivo a ejecutar, verificar que existe en el disco
    if file_to_run:
        from cpcready.pydsk.dsk import DSK
        from cpcready.utils.manager import SystemCPM
        
        try:
            dsk = DSK(disc_name)
            system_cpm = SystemCPM()
            user_number = system_cpm.get_user_number()
            
            # Intentar leer el archivo para verificar que existe
            try:
                dsk.read_file(file_to_run, user=user_number)
                info2(f"Running file: {file_to_run}")
            except:
                error(f"File '{file_to_run}' not found on disk (user {user_number}).")
                return
        except Exception as e:
            error(f"Error verifying disk: {e}")
            return
    
    # Mostrar modelo
    info2(f"CPC Model: {modelo}")
    
    # Matar instancias previas
    matar_rvm()
    time.sleep(0.5)  # Asegurar cierre
    
    # Lanzar nueva instancia
    lanzar_rvm(ruta_rvm, modelo, disc_name, file_to_run)
    blank_line(1)
