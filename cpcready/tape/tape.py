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
from cpcready.utils import console, system
from cpcready.utils import console, system, DriveManager, SystemCPM, cassetteManager
from cpcready.utils.click_custom import CustomCommand, RichCommand, CustomGroup, RichGroup, RichCommand
from cpcready.utils.console import ok, error, warn, blank_line
from cpcready.utils.version import add_version_option_to_group
from cpcready.utils.update import show_update_notification
from cpcready.pycdt import CDT, DataHeader
from rich.console import Console
from rich.table import Table
import sys

console = Console()

@add_version_option_to_group
@click.group(cls=RichGroup, invoke_without_command=True, show_banner=False)
@click.pass_context
def tape(ctx):
    """
    Manage tape images (CDT).

        Examples:
            cpc tape new mytape.cdt         # Create a new tape image
            cpc tape info mytape.cdt        # Show info about a tape
            cpc tape cat mytape.cdt         # List blocks in a tape
            cpc tape add mytape.cdt file.bin --type BIN --load 0x1000 --exec 0x1000
            cpc tape check mytape.cdt       # Verify tape integrity
        """
    # Mostrar notificación de actualización si la hay
    show_update_notification()

    if ctx.invoked_subcommand is None:
        System = SystemCPM()
        System.set_storage("tape")
        blank_line(1)
        ok("'tape' Selected for CPCReady session.")
        blank_line(1)

@tape.command(cls=RichCommand)
@click.argument("tape_name", required=True)
@click.option("-C", "--cassette", is_flag=True, help="Insert cassette into virtual tape drive")
def new(tape_name, cassette):
    """Create a new empty tape image (CDT)."""
    tape_name = str(system.process_cdt_name(tape_name))
    
    # Asegurarnos de que tenga extensión .cdt (aunque process_dsk_name suele pensar en dsk)
    if not tape_name.lower().endswith('.cdt'):
        tape_name += '.cdt'
        
    tape_path = Path(tape_name)
    
    if tape_path.exists():
        blank_line(1)
        warn(f"Tape '{tape_path.name}' already exists.")
        if cassette:
            cassette_mgr = cassetteManager()
            cassette_mgr.set_tape(str(tape_path))
            blank_line(1)
            ok(f"Cassette '{tape_path.name}' inserted into virtual tape drive.")
            
        blank_line(1)
        return

    try:
        cdt = CDT(str(tape_path))
        cdt.create()
        cdt.save()
        blank_line(1)
        ok(f"Tape '{tape_path.name}' created successfully!")
        blank_line(1)
        if cassette:
            cassette_mgr = cassetteManager()
            cassette_mgr.set_tape(str(tape_path))
            ok(f"Cassette '{tape_path.name}' inserted into virtual tape drive.")
            blank_line(1)
        # console.print(table)
        cdt.list_files(simple=False, use_rich=True, title=tape_path.name, show_title=True)

    except Exception as e:
        error(f"Error creating tape: {e}")
    
@tape.command(cls=RichCommand)
@click.argument("tape_name", required=True)
def insert(tape_name):
    """Show detailed information about a tape file."""

    tape_name = str(system.process_cdt_name(tape_name))
    tape_path = Path(f"{tape_name}")
    
    if not tape_path.exists():
        error(f"\nTape file not found: {tape_name}\n")
        return
        
    cassette_mgr = cassetteManager()
    current_tape =cassette_mgr.get_tape()
    if current_tape == tape_name:
        blank_line(1)
        warn(f"Cassette '{tape_path.name}' is already inserted in the virtual tape drive.")
        blank_line(1)
        return
    cdt = CDT(str(tape_path))
    cdt.check()
    blank_line(1)
    ok(f"Tape '{tape_path.name}' verifies OK.")
    
    cassette_mgr.set_tape(str(tape_path))
    ok(f"Cassette '{tape_path.name}' inserted into virtual tape drive.")
    blank_line(1)
    cdt.list_files(simple=False, use_rich=True, title=tape_path.name, show_title=True)
    
@tape.command(cls=RichCommand)
def eject():
    """List blocks and structure of the tape."""
    # Reutilizamos la lógica de info ya que hacen lo mismo (cdt.dump)
    # pero mantenemos el nombre 'cat' por consistencia con cdt.py original y cpcready
    
    cassette_mgr = cassetteManager()
    tape_name = cassette_mgr.get_tape()
    print(tape_name)
    if tape_name == "":
        error("No tape inserted in the cassette drive.\n")
        return
    cassette_mgr.eject()
    blank_line(1)
    ok(f"Cassette '{tape_name}' ejected from virtual tape drive.\n")
    
