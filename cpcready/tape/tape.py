
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

# Añadir PyCDT al path si es necesario (generalmente ya está por estar en el mismo paquete)
console = Console()

def aux_int(value_str):
    """Helper para convertir string a int soportando hex (0x)"""
    if isinstance(value_str, int):
        return value_str
    if value_str.startswith('0x') or value_str.startswith('&') or value_str.startswith('$'):
        return int(value_str.replace('&', '0x').replace('$', '0x'), 16)
    return int(value_str)

@add_version_option_to_group
@click.group(cls=RichGroup, invoke_without_command=True, show_banner=False)
@click.pass_context
def tape(ctx):
    """
    Manage tape images (CDT/TZX) for CPC Ready session.

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
def new(tape_name):
    """Create a new empty tape image (CDT)."""
    tape_name = str(system.process_dsk_name(tape_name))
    
    # Asegurarnos de que tenga extensión .cdt (aunque process_dsk_name suele pensar en dsk)
    if not tape_name.lower().endswith('.cdt'):
        tape_name += '.cdt'
        
    tape_path = Path(tape_name)
    
    if tape_path.exists():
        warn(f"Tape '{tape_path.name}' already exists.")
        return

    try:
        cdt = CDT(str(tape_path))
        cdt.create()
        cdt.save()
        
        ok(f"Tape '{tape_path.name}' created successfully!")
        blank_line(1)
        
        # Mostrar información básica
        table = Table(show_header=False, box=None, padding=(0, 0))
        table.add_column(style="blue", justify="left")
        table.add_column(style="yellow", justify="left")
        
        table.add_row("File: ", tape_path.name)
        table.add_row("Format: ", "CDT/TZX (Amstrad CPC)")
        table.add_row("Blocks: ", "1 (Empty Pause)")
        
        console.print(table)
        blank_line(1)
        
    except Exception as e:
        error(f"Error creating tape: {e}")

@tape.command(cls=RichCommand)
@click.argument("tape_name", required=True)
def info(tape_name):
    """Show detailed information about a tape file."""
    # Manejar extensión si falta
    if not tape_name.lower().endswith('.cdt') and not Path(tape_name).exists():
        if Path(tape_name + '.cdt').exists():
            tape_name += '.cdt'
            
    tape_path = Path(tape_name)
    
    if not tape_path.exists():
        error(f"Tape file not found: {tape_name}")
        return
        
    try:
        cdt = CDT(str(tape_path))
        # Al inicializar con filename, ya intenta cargar si existe. 
        # Si no existiera fallaría, pero ya checkeramos exists arriba.
        # De todos modos, para ser explicitos podemos llamar a load si no lo hizo el init (que si lo hace)
        if not cdt.blocks: # safety check si falló carga silenciosa o algo
             cdt.load(str(tape_path))
        
        info = cdt.get_info()
        
        blank_line(1)
        console.print(f"[bold blue]Tape Info:[/bold blue] [yellow]{tape_path.resolve()}[/yellow]")
        blank_line(1)
        
        # Usar el listado rico de alto nivel
        cdt.list_files(simple=False, use_rich=True, show_title=False)
        
    except Exception as e:
        error(f"Error reading tape: {e}")

@tape.command(cls=RichCommand)
@click.argument("tape_name", required=True)
def cat(tape_name):
    """List blocks and structure of the tape."""
    # Reutilizamos la lógica de info ya que hacen lo mismo (cdt.dump)
    # pero mantenemos el nombre 'cat' por consistencia con cdt.py original y cpcready
    ctx = click.get_current_context()
    ctx.invoke(info, tape_name=tape_name)
        
@tape.command(cls=RichCommand)
@click.argument("tape_name", required=True)
def check(tape_name):
    """Verify CDT tape format integrity."""
    # Manejar extensión si falta
    if not tape_name.lower().endswith('.cdt') and not Path(tape_name).exists():
        if Path(tape_name + '.cdt').exists():
            tape_name += '.cdt'
            
    tape_path = Path(tape_name)
    
    if not tape_path.exists():
        error(f"Tape file not found: {tape_name}")
        return
        
    try:
        cdt = CDT(str(tape_path))
        cdt.check()
        ok(f"Tape '{tape_path.name}' verifies OK.")
    except Exception as e:
        error(f"Tape verification FAILED: {e}")

@tape.command(cls=RichCommand)
@click.argument("tape_name", required=True)
@click.argument("input_file", required=True, type=click.Path(exists=True))
@click.option("--speed", type=click.Choice(['1000', '2000']), default='2000', help="Baud rate (def: 2000).")
@click.option("--type", type=click.Choice(['BIN', 'ASCII', 'RAW']), default='BIN', help="File type to add (def: BIN).")
@click.option("--name", help="AMSDOS filename (max 16 chars).")
@click.option("--load", help="Load address (dec/hex) for BIN files.")
@click.option("--exec", help="Execution address (dec/hex) for BIN files.")
def add(tape_name, input_file, speed, type, name, load, exec):
    """Add a file to the tape image.
    
    Supports adding BINARY (with load/exec addr), ASCII, or RAW files.
    """
    
    # Manejar extensión si falta
    if not tape_name.lower().endswith('.cdt') and not Path(tape_name).exists():
        if Path(tape_name + '.cdt').exists():
            tape_name += '.cdt'
            
    tape_path = Path(tape_name)
    if not tape_path.exists():
        error(f"Tape file not found: {tape_name}")
        return

    try:
        cdt = CDT(str(tape_path))
        # cdt.load(str(tape_path)) # Implicito en init
        
        with open(input_file, 'rb') as f:
            content = bytearray(f.read())
            
        header = None
        
        # Determinar nombre AMSDOS
        amsdos_name = name if name else Path(input_file).name.upper()
        if len(amsdos_name) > 16:
             amsdos_name = amsdos_name[:16]

        type_upper = type.upper()
        
        if type_upper == 'RAW':
            header = None # No header for RAW
            console.print(f"Adding [cyan]{input_file}[/cyan] as [yellow]RAW[/yellow] data...")
        else:
            # Tipos con cabecera
            ftype = DataHeader.FT_BIN
            if type_upper == 'ASCII':
                ftype = DataHeader.FT_ASCII # 0x16 
            
            # Parsear direcciones
            load_addr = 0
            exec_addr = 0
            
            if load:
                load_addr = aux_int(load)
            if exec:
                exec_addr = aux_int(exec)
                
            header = cdt.create_data_header(
                filename=amsdos_name,
                load_addr=load_addr,
                exec_addr=exec_addr,
                file_type=ftype
            )
            
            type_str = f"[blue]{type_upper}[/blue]"
            if type_upper == 'BIN':
                type_str += f" (load: {hex(load_addr)}, exec: {hex(exec_addr)})"
                
            console.print(f"Adding [cyan]{input_file}[/cyan] as [yellow]{amsdos_name}[/yellow] [{type_str}]...")
        
        cdt.add_file(content, header, int(speed))
        cdt.save() # Guarda en el fichero con el que se inicializo
        
        ok(f"File added successfully to '{tape_path.name}'.")
        
    except Exception as e:
        error(f"Error adding file to tape: {e}")
