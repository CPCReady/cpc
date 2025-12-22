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
from cpcready.utils.console import error, warn, blank_line
from cpcready.utils.manager import DriveManager, SystemCPM, cassetteManager
from cpcready.utils.click_custom import CustomCommand, RichCommand, RichCommand
from cpcready.utils.version import add_version_option
from cpcready.utils.update import show_update_notification
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

@add_version_option
@click.command(cls=RichCommand, show_banner=False)
def sysinfo():
    """
    Show system and drive information for the current CPCReady session.

    Examples:
        cpc sysinfo         # Show all system and drive info
        cpc sysinfo --help  # Show this help message
    """
    show_update_notification()
    
    drive_manager = DriveManager()
    cassete_manager = cassetteManager()
    System = SystemCPM()
    
    
    emulator = drive_manager.read_emulator()
    cpc_model = System.get_model()
    screen = System.get_mode()
    ip = drive_manager.read_m4board_ip()
    user = System.get_user_number()
    storage = System.get_storage()
    tape = cassete_manager.get_tape()
    
    blank_line(1)
    
    console.print()
    console.rule("Storage", style="bright_yellow", align="left")
    console.print()
    
    table = Table(
        show_header=False,
        border_style="bold yellow",
        box=box.ROUNDED
    )

    table.add_column("Select", style="bold cyan", no_wrap=True)
    table.add_column("Path", style="green", width=19)

    table.add_row("Select", storage)

    console.print(table)
    console.print()
    console.rule("Cassette Details", style="bright_yellow", align="left",)
    console.print()
    
    table = Table(
        show_header=True,
        border_style="bold yellow",
        box=box.ROUNDED
    )

    table.add_column("Tape", style="bright_green", no_wrap=True)
    table.add_column("Path", style="dim bright_green")
    if tape:
        from pathlib import Path as _Path
        tape_path = _Path(tape)
        table.add_row(tape_path.name, str(tape_path))
    else:
        table.add_row("[yellow]No cassette inserted[/yellow]", "")
    console.print(table)
    
    console.print()
    console.rule("Drive Details", style="bright_yellow", align="left")
    console.print()
    drive_manager.drive_table()
    console.print()
    console.rule("System Information", style="bright_yellow", align="left")
    console.print()
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

    console.print(table)
    blank_line(1)
    
