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
from cpcready.utils import DriveManager
from cpcready.utils.click_custom import CustomCommand
from cpcready.utils.console import info2, ok, debug, warn, error, blank_line, banner
from cpcready.utils.version import add_version_option

@add_version_option
@click.command(cls=CustomCommand, show_banner=True)
@click.option("-A", "--drive-a", is_flag=True, help="Eject disc from drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Eject disc from drive B")
def eject(drive_a, drive_b):
    """Eject disc from specified drive."""
    from cpcready.utils.console import error
    
    drive_manager = DriveManager()

    # Validar que solo se especifique una unidad
    if drive_a and drive_b:
        blank_line(1)
        error("Cannot specify both -A and -B options. Choose one drive.")
        return
    
    if drive_a:
        blank_line(1)
        drive_manager.eject('A')
        drive_manager.drive_table()
    elif drive_b:
        blank_line(1)
        drive_manager.eject('B')
        drive_manager.drive_table()
    else:
        blank_line(1)
        warn("Please specify a drive using -A or -B option.\n")
        return
  