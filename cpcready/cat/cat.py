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
import shutil
from cpcready.utils import console, system, DriveManager,cassetteManager
from cpcready.utils.click_custom import CustomCommand, RichCommand, CustomGroup, RichGroup, RichCommand
from cpcready.utils.console import info2, ok, debug, warn, error, message, blank_line, banner
from cpcready.utils.version import add_version_option
from cpcready.utils.update import show_update_notification
from cpcready.pydsk import DSK, DSKError
from rich.console import Console
from rich.panel import Panel

# Crear consolas separadas para stdout y stderr
console = Console()
@add_version_option
@click.command(cls=RichCommand)
@click.option("-A", "--drive-a", is_flag=True, help="List files in the virtual disc from drive A")
@click.option("-B", "--drive-b", is_flag=True, help="List files in the virtual disc from drive B")
def cat(drive_a, drive_b):
    """
    List all files in the virtual disc (DSK image) for the selected drive.

    This command displays the file list of the disc inserted in drive A or B, with rich formatting. If no option is selected, the currently active drive is used.

    Options:
        -A : List files from drive A
        -B : List files from drive B

    Examples:
        cpc cat -A         # List files in disc from drive A
        cpc cat -B         # List files in disc from drive B
        cpc cat            # List files in disc from currently selected drive (Defined executed cpc A or cpc B)

    Notes:
        - Only one drive can be specified at a time.
        - If no disc is inserted, an error is shown and the drive table is displayed.
        - The file list includes deleted files and file types.
        - Useful for quickly viewing the contents of a disc image.
        - If neither -A nor -B is specified, the default drive (cpc A or cpc B) currently defined in CPCReady will be used.
    """
    show_update_notification()
    # estandarizamos nombre del disc
    drive_manager = DriveManager()

       # Validar que solo se especifique una unidad
    if drive_a and drive_b:
        error("Cannot specify both -A and -B options. Choose one drive.")
        return

    drive = None
    if drive_a:
        drive = 'A'
        disc_name = drive_manager.read_drive_a()
    elif drive_b:
        drive = 'B'
        disc_name = drive_manager.read_drive_b()
    else:
        drive = drive_manager.read_drive_select().upper()
        if drive == 'A':
            disc_name = drive_manager.read_drive_a()
        else:
            disc_name = drive_manager.read_drive_b()
    
   
    if disc_name == "":
        blank_line(1)
        error(f"Drive {drive}: disc missing\n")
        drive_manager.drive_table()
        return

    disc_path = Path(f"{disc_name}")
    if not disc_path.exists():
        error(f"{disc_name} assigned to drive {drive} does not exist.")
        drive_manager.eject(drive)
        drive_manager.drive_table()
        return
        
    dsk = DSK(disc_name)
    blank_line(1)
    dsk.list_files(simple=False, use_rich=True)



