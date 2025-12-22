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
import shutil
from cpcready.utils import console, system, DriveManager, SystemCPM,cassetteManager
from cpcready.utils.click_custom import CustomCommand, RichCommand, CustomGroup
from cpcready.utils.console import info2, ok, debug, warn, error, message,blank_line,banner
from cpcready.utils.version import add_version_option_to_group
from cpcready.pydsk import DSK
from cpcready.pydsk.basic_viewer import view_basic, detect_basic_format, view_basic_ascii, detokenize_basic
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
console = Console()

@click.command(cls=RichCommand)
@click.argument("file_name", required=True)
@click.option("-A", "--drive-a", is_flag=True, help="List BASIC file from virtual disc in drive A")
@click.option("-B", "--drive-b", is_flag=True, help="List BASIC file from virtual disc in drive B")
def list(file_name, drive_a, drive_b):
    """
    List the contents of a BASIC file from a virtual disc (DSK image) in CPCReady.

    This command displays the listing of a BASIC program stored on a virtual disc (A/B). The file must be a valid BASIC file; binary and screen files cannot be listed.

    Arguments:
        file_name : Name of the BASIC file to list (e.g., PROG.BAS)

    Options:
        -A, --drive-a : List BASIC file from virtual disc in drive A
        -B, --drive-b : List BASIC file from virtual disc in drive B

    Behavior:
        - If neither -A nor -B is specified, the default drive (cpc A or cpc B) currently defined in CPCReady will be used.
        - Only valid BASIC files can be listed. Binary and screen files are not supported.
        - The file must exist on the disk of the selected drive and for the current user number.

    Examples:
        cpc list PROG.BAS -A      # List BASIC file from drive A
        cpc list GAME.BAS -B      # List BASIC file from drive B
        cpc list DEMO.BAS         # List BASIC file from currently selected drive (Defined executed cpc A or cpc B)

    Notes:
        - If the file is not a valid BASIC program, an error will be shown.
        - The listing is displayed with syntax highlighting and line numbers.
        - After listing, the panel will show the file contents for review.
    """
    # Obtener el nombre del disco usando DriveManager
    drive_manager = DriveManager()
    system_cpm = SystemCPM()
    storage_mode = system_cpm.get_storage()
    
    if storage_mode != "disc":
        blank_line(1)
        error("The current storage mode is not set to 'disc'. Cannot erase files from disc.")
        blank_line(1)
        return 1
    
    disc_name = drive_manager.get_disc_name(drive_a, drive_b)
    
    if disc_name is None:
        error("No disc inserted in the specified drive.")
        return
    
    # Obtener el user number actual
    user_number = system_cpm.get_user_number()
    
    blank_line(1)
    
    try:
        dsk = DSK(disc_name)
        
        # Leer archivo con cabecera para verificar el tipo
        data_with_header = dsk.read_file(file_name, keep_header=True, user=user_number)
        
        # Verificar si tiene cabecera AMSDOS válida
        if len(data_with_header) >= 128 and dsk._check_amsdos_header(data_with_header):
            file_type = data_with_header[0x12]  # Byte de tipo de archivo
            
            # Tipo 2 = BINARY
            if file_type == 2:
                error(f"Cannot list binary file: {file_name}")
                blank_line(1)
                return
            
            # Tipo 22 = SCREEN$
            if file_type == 22:
                error(f"Cannot list screen file: {file_name}")
                blank_line(1)
                return
        
        # Leer archivo sin cabecera para procesarlo
        data = dsk.read_file(file_name, keep_header=False, user=user_number)
        
        # Intentar visualizar como BASIC - auto detectar formato
        listing = view_basic(data, auto_detect=True)
        
        # Si el listing está vacío, no es BASIC
        if not listing or not listing.strip():
            error(f"File does not appear to be a valid BASIC program: {file_name}")
            blank_line(1)
            return
        
        # Mostrar el listado directamente sin más validaciones
        syntax = Syntax(listing, "basic", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"Listing '{file_name}'", border_style="bright_blue"))
        
    except Exception as e:
        error(f"Error listing file: {e}")
    
    blank_line(1)

