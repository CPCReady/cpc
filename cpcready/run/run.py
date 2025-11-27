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
from pathlib import Path
from cpcready.utils.click_custom import CustomCommand
from cpcready.utils.console import info2, error, blank_line
from cpcready.utils.toml_config import ConfigManager
from cpcready.utils.manager import DriveManager
from cpcready.utils.retrovirtualmachine import RVM


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
    
    # Crear instancia de RVM y verificar versión
    rvm = RVM(ruta_rvm)
    
    is_valid, version_info = rvm.check_version()
    if not is_valid:
        error("RetroVirtualMachine version check failed.")
        error(version_info)
        return
    
    # Lanzar emulador
    rvm.launch(modelo, archivo_dsk=disc_name, archivo_ejecutar=file_to_run)
    blank_line(1)
