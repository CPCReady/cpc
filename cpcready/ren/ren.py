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
from rich.console import Console
from cpcready.pydsk import DSK, DSKError, DSKFileNotFoundError, DSKFileExistsError
from rich.panel import Panel
console = Console()

@click.command(cls=RichCommand)
@click.argument("file_old", required=True)
@click.argument("file_new", required=True)
@click.option("-A", "--drive-a", is_flag=True, help="Rename file on virtual disc in drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Rename file on virtual disc in drive B")
def ren(file_old, file_new, drive_a, drive_b):
    """
    Rename a file on a virtual disc (DSK image) in CPCReady.

    This command renames a file stored on a virtual disc (A/B). You must specify the original file name and the new name.

    Arguments:
        file_old : Current name of the file to rename (e.g., OLDNAME.BAS)
        file_new : New name for the file (e.g., NEWNAME.BAS)

    Options:
        -A, --drive-a : Rename file on virtual disc in drive A
        -B, --drive-b : Rename file on virtual disc in drive B

    Behavior:
        - If neither -A nor -B is specified, the default drive (cpc A or cpc B) currently defined in CPCReady will be used.
        - The file must exist on the disk of the selected drive.
        - The new name must not already exist on the disk.

    Examples:
        cpc ren OLDNAME.BAS NEWNAME.BAS -A
        cpc ren DATA.BIN DATA2.BIN -B
        cpc ren PROG.BAS PROG2.BAS    # Uses currently selected drive (Defined executed cpc A or cpc B)

    Notes:
        - If the file does not exist, an error will be shown.
        - If the new name already exists, the operation will fail.
        - After renaming, the updated file list will be displayed.
        - Wildcards (*, ?) are allowed in file names for batch renaming (e.g., *.BAS, PROG?.BIN).
    """
    # Obtener el nombre del disco usando DriveManager
    system_cpm = SystemCPM()
    storage_mode = system_cpm.get_storage()
    
    if storage_mode != "disc":
        blank_line(1)
        error("The current storage mode is not set to 'disc'. Cannot erase files from disc.")
        blank_line(1)
        return 1
    
    drive_manager = DriveManager()
    disc_name = drive_manager.get_disc_name(drive_a, drive_b)
    
    if disc_name is None:
        error("No disc inserted in the specified drive.")
        return

    try:
        # Cargar DSK y renombrar archivo
        dsk = DSK(disc_name)
        dsk.rename_file(file_old, file_new)
        dsk.save()
        
        ok(f"File renamed: {file_old} → {file_new}")
        
        blank_line(1)
        
        # Mostrar contenido actualizado del disco
        dsk.list_files(simple=False, use_rich=True, show_title=True)
        
    except DSKFileNotFoundError as e:
        error(f"File not found: {file_old}")
        blank_line(1)
    except DSKFileExistsError as e:
        error(f"File already exists: {file_new}")
        blank_line(1)
    except DSKError as e:
        error(f"Error renaming file: {e}")
        blank_line(1)
    
  
