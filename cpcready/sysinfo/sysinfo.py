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
from cpcready.utils.console import error, warn, blank_line
from cpcready.utils.manager import DriveManager, SystemCPM, cassetteManager
from cpcready.utils.click_custom import CustomCommand
from cpcready.utils.version import add_version_option
from cpcready.utils.update import show_update_notification
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

@add_version_option
@click.command(cls=CustomCommand, show_banner=True)
def sysinfo():
    """System information."""
    show_update_notification()
    drive_manager = DriveManager()
    System = SystemCPM()
        
    blank_line(1)
    console.print(
        Panel(
            "Drive Information",
            border_style="yellow",
            width=22,
            style="bold white",
        )
    )
    
    drive_manager.drive_table()

    
    console.print(
        Panel(
            "System Information",
            border_style="yellow",
            width=22,
            style="bold white",
        )
    )

    emulator = drive_manager.read_emulator()
    cpc_model = System.get_model()
    screen = System.get_mode()
    ip = drive_manager.read_m4board_ip()
    user = System.get_user_number()

    table = Table(
        border_style="bright_yellow",
        box=box.ROUNDED
    )
    
    table.add_column("CPC Model", justify="center")
    table.add_column("User", justify="center")
    table.add_column("Screen", justify="center")
    table.add_column("Emulator", justify="center")
    table.add_column("M4Board IP", justify="center")
    
    table.add_row(
        str(cpc_model),
        str(user),
        str(screen),
        str(emulator),
        str(ip)
    )
    
    # Mostrar tabla
    console.print(table)
    blank_line(1)
    
