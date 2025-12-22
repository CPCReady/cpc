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


import click
from pathlib import Path
from cpcready.utils.click_custom import CustomCommand, RichCommand, RichCommand
from cpcready.utils.console import info2, error, blank_line
from cpcready.utils.toml_config import ConfigManager
from cpcready.utils.manager import DriveManager, cassetteManager, SystemCPM
from cpcready.utils.retrovirtualmachine import RVM


@click.command(cls=RichCommand)
@click.argument("file_to_run", required=False)
@click.option("-A", "--drive-a", is_flag=True, help="Use disk from drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Use disk from drive B")
def run(file_to_run, drive_a, drive_b):
    """
    Run a file from the selected drive in RetroVirtualMachine (RVM).

    This command launches the RetroVirtualMachine emulator with the disk image from the selected drive (A/B) and optionally runs a file from that disk.

    Arguments:
        FILE_TO_RUN : Name of the file to execute from the disk (e.g., DISC, GAME.BAS). Optional. If omitted, only the emulator is launched with the disk.

    Options:
        -A, --drive-a : Use disk from drive A
        -B, --drive-b : Use disk from drive B

    Behavior:
        - If neither -A nor -B is specified, the default drive (cpc A or cpc B) currently defined in CPCReady will be used.
        - The file must exist on the disk of the selected drive and for the current user number.
        - The emulator path must be configured using the emu command.

    Examples (Only for disc storage mode):
        cpc run GAME.BAS -A         # Run GAME.BAS from drive A in RVM
        cpc run PROGRAM.BIN -B      # Run PROGRAM.BIN from drive B in RVM
        cpc run                     # Launch RVM with the current disk, no file executed
        cpc run GAME.BAS            # Run GAME.BAS from the currently selected drive (Defined executed cpc A or cpc B)
    
    Examples (Only for tape storage mode):
        cpc run                 # Launch RVM with the tape inserted in the Virtual cassette drive

    Notes:
        - If the file does not exist on the disk, an error will be shown.
        - The CPC model used in the emulator is the one defined with the command 'cpc model'.
        - The CPC model and emulator path are read from the configuration file.
        - You can change the selected drive with the drive command.
        - The emulator version is checked before launching.
        
    """
    
    # Cargar configuración
    config = ConfigManager()
    
    # Obtener modelo CPC de la configuración
    modelo = config.get("system", "model", "6128")
    
    # Obtener ruta del ejecutable RVM
    ruta_rvm = config.get("emulator", "retro_virtual_machine_path", "")
    
    if not ruta_rvm:
        blank_line(1)
        error("RetroVirtualMachine path not configured.")
        error("Configure the emulator using emu command.")
        blank_line(1)
        return
    
    # Verificar que existe
    if not Path(ruta_rvm).exists():
        error(f"RetroVirtualMachine not found at: {ruta_rvm}")
        error("Check the path in configuration file.")
        return
    
    # Obtener disco de la unidad seleccionada
    drive_manager = DriveManager()
    disc_name = drive_manager.get_disc_name(drive_a, drive_b)
    system_cpm = SystemCPM()
    storage_mode = system_cpm.get_storage()
    # Crear instancia de RVM y verificar versión
    rvm = RVM(ruta_rvm)
    if storage_mode == "disc":
        
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
        

        
        is_valid, version_info = rvm.check_version()
        if not is_valid:
            error("RetroVirtualMachine version check failed.")
            error(version_info)
            return
        
        # Lanzar emulador
        rvm.launch(modelo, archivo_dsk=disc_name, archivo_ejecutar=file_to_run)
        blank_line(1)
        
    elif storage_mode == "tape":
        cassette_mgr = cassetteManager()
        tape_name = cassette_mgr.get_tape()
        if tape_name is None:
            error("No tape inserted in the selected drive.")
            return

        # Mostrar modelo
        blank_line(1)
        info2(f"CPC Model: {modelo}")
        info2(f"Using cassette tape: {Path(tape_name).name}")
        rvm.launch(modelo, archivo_dsk=tape_name, archivo_ejecutar="only_tape")
        blank_line(1)
