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
from cpcready.utils import console, system, DriveManager, SystemCPM
from cpcready.utils.click_custom import CustomCommand, CustomGroup
from cpcready.utils.console import info2, ok, debug, warn, error, message,blank_line,banner
from cpcready.utils.version import add_version_option_to_group
from cpcready.utils.update import show_update_notification
from cpcready.pydsk import DSK
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich import box
import sys
from pathlib import Path

# Añadir PyDSK al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
console = Console()

   
@add_version_option_to_group
@click.group(cls=CustomGroup, help="Create or manage virtual discs.", invoke_without_command=True, show_banner=True)
@click.pass_context
def disc(ctx):
    """Select storage for CPC Ready session."""
    # Mostrar notificación de actualización si la hay
    show_update_notification()
    
    # Solo mostrar mensaje de selección si no se ejecuta un subcomando
    if ctx.invoked_subcommand is None:
        System = SystemCPM()
        System.set_storage("disc")
        blank_line(1)
        ok("'disc' Selected for CPCReady session.")
        blank_line(1)

@disc.command(cls=CustomCommand)
@click.argument("disc_name", required=True)
@click.argument("format", required=False, default="DATA", type=click.Choice(["DATA", "VENDOR", "SYSTEM"]))
@click.option("-A", "--drive-a", is_flag=True, help="Insert disc into drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Insert disc into drive B")
def new(disc_name, format, drive_a, drive_b):
    """Create a new virtual disc or insert existing disc into drive.
    """
    # Test step by step
    drive_manager = DriveManager()
    
    disc_name = str(system.process_dsk_name(disc_name))
    disc_path = Path(f"{disc_name}")
    
    dsk = DSK()
    
    # Validar que solo se especifique una unidad
    if drive_a and drive_b:
        print("Cannot specify both -A and -B options. Choose one drive.")
        return
    
    drive = None
    if drive_a:
        drive = 'A'
    elif drive_b:
        drive = 'B'
    
    blank_line(1)
  
    # Mapear formato a constante DSK
    format_map = {
        'DATA': DSK.FORMAT_DATA,
        'SYSTEM': DSK.FORMAT_SYSTEM,
        'VENDOR': DSK.FORMAT_VENDOR
    }
    format_type = format_map.get(format.upper(), DSK.FORMAT_DATA)
    
    if disc_path.exists():
        warn(f"disc '{disc_path.name}' exists not creating new one.")
        # console.print(f"   [blue]File:[/blue] [yellow]{disc_path.name}[/yellow]")
        # console.print(f"   [blue]Format:[/blue] [yellow]{format}[/yellow]")
        # console.print(f"   [blue]Capacity:[/blue] [yellow]180 KB[/yellow]")
        # console.print(f"   [blue]Free space:[/blue] [yellow]178 KB[/yellow]")
        blank_line(1)
        if drive_a or drive_b:
            drive_manager.drive_table()
        return
    else:
        dsk.create(
            nb_tracks=40,              # 40 pistas
            nb_sectors=9,              # 9 sectores por pista
            format_type=format_type
        )
        dsk.save(disc_path.name)
        # Mostrar información después de crear
        info = dsk.get_info()
        ok(f"'{disc_path.name}' created successfully!")
        blank_line(1)
        
        # Crear tabla para mostrar información del disco
        table = Table(show_header=False, box=None, padding=(0, 0))
        table.add_column(style="blue", justify="left")
        table.add_column(style="yellow", justify="left")
        
        table.add_row("File: ", disc_path.name)
        table.add_row("Format: ", info['format'])
        table.add_row("Capacity: ", f"{info['capacity_kb']} KB")
        table.add_row("Free space: ", f"{dsk.get_free_space()} KB")
        
        console.print(table)
        blank_line(1)
        if drive_a:
            drive_manager.insert_drive_a(disc_name)
            blank_line(1)
        elif drive_b:
            drive_manager.insert_drive_b(disc_name)
            blank_line(1)
        if drive_a or drive_b:
            drive_manager.drive_table()
        return

@disc.command(cls=CustomCommand)
@click.argument("disc_name", required=False)
@click.option("-A", "--drive-a", is_flag=True, help="Show info for disc in drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Show info for disc in drive B")
def info(disc_name, drive_a, drive_b):
    """Show detailed information about a disc file."""
    drive_manager = DriveManager()
    dsk = DSK()
    
    
    # Validar que solo se especifique una opción
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
        error(f"Drive {drive}: disc not inserted\n")
        blank_line(1)
        return
    
    disc_path = Path(disc_name)
    if not disc_path.exists():
        error(f"disc file not found: {disc_name}")
        return
    
    # Obtener la ruta absoluta para mostrar
    disc_full_path = str(disc_path.resolve())
    
    dsk = DSK(disc_name)
    info = dsk.get_info()
    entries = dsk.get_directory_entries()
    
    # Calcular estadísticas
    archivos_activos = [e for e in entries if not e.is_deleted and e.num_page == 0]
    archivos_borrados = [e for e in entries if e.is_deleted]
    
    # Bloques usados
    bloques_usados = set()
    for entry in entries:
        if not entry.is_deleted:
            for block in entry.blocks:
                if block != 0:
                    bloques_usados.add(block)
    
    espacio_usado = len(bloques_usados)
    espacio_libre = dsk.get_free_space()
    porcentaje_usado = (espacio_usado / (espacio_usado + espacio_libre)) * 100 if (espacio_usado + espacio_libre) > 0 else 0
    
    # Contar tipos de archivos
    tipos_archivo = {
        'BINARY': 0,
        'BASIC': 0,
        'BASIC+': 0,
        'SCREEN$': 0,
        'ASCII': 0,
        'OTHER': 0
    }
    
    for entry in archivos_activos:
        if entry.blocks[0] != 0:
            try:
                block_data = dsk.read_block(entry.blocks[0])
                if dsk._check_amsdos_header(block_data):
                    ftype = block_data[0x12]
                    if ftype == 0:
                        tipos_archivo['BASIC'] += 1
                    elif ftype == 1:
                        tipos_archivo['BASIC+'] += 1
                    elif ftype == 2:
                        tipos_archivo['BINARY'] += 1
                    elif ftype == 22:
                        tipos_archivo['SCREEN$'] += 1
                    else:
                        tipos_archivo['OTHER'] += 1
                else:
                    tipos_archivo['ASCII'] += 1
            except:
                tipos_archivo['ASCII'] += 1
        else:
            tipos_archivo['ASCII'] += 1
    
    print()
    
    # Panel de título: DISC INFO
    title_content = f"[blue]Path:[/blue] [yellow]{disc_full_path}[/yellow]"
    
    title_panel = Panel(
        title_content,
        border_style="bright_yellow",
        padding=(1, 2),
        width=79
    )
    
    # Panel 1: Estructura Física
    physical_content = f"""
[green]Pistas:[/green]            [yellow]{info['tracks']}[/yellow]
[green]Caras:[/green]             [yellow]{info['heads']}[/yellow]
[green]Tamaño pista:[/green]      [yellow]{info['track_size']:,} bytes[/yellow]
[green]Tamaño total:[/green]      [yellow]{info['total_size']:,} bytes[/yellow]
"""
    
    physical_panel = Panel(
        physical_content,
        title="[bold green]PHYSICAL STRUCTURE[/bold green]",
        border_style="yellow",
        padding=(0, 2),
        width=39,
        height=8
    )
    
    # Panel 2: Formato
    format_content = f"""
[green]Tipo:[/green]            [yellow]{info['format']}[/yellow]
[green]Primer sector:[/green]   [yellow]0x{dsk.get_min_sector():02X}[/yellow]


"""
    
    format_panel = Panel(
        format_content,
        title="[bold green]FORMAT[/bold green]",
        border_style="yellow",
        padding=(0, 2),
        width=39,
        height=8
    )
    
    # Panel 3: Capacidad
    capacity_content = f"""
[green]Total:[/green]      [yellow]{info['capacity_kb']} KB[/yellow]
[green]Usado:[/green]      [yellow]{espacio_usado} KB ({porcentaje_usado:.1f}%)[/yellow]
[green]Libre:[/green]      [yellow]{espacio_libre} KB ({100-porcentaje_usado:.1f}%)[/yellow]

"""
    
    capacity_panel = Panel(
        capacity_content,
        title="[bold green]CAPACITY[/bold green]",
        border_style="yellow",
        padding=(0, 2),
        width=39,
        height=8
    )
    
    # Panel 4: Tipos de archivos
    filetype_content = f"""
[green]binary:[/green]   [yellow]{tipos_archivo['BINARY']}[/yellow]
[green]basic:[/green]    [yellow]{tipos_archivo['BASIC']}[/yellow]
[green]basic+:[/green]   [yellow]{tipos_archivo['BASIC+']}[/yellow]
[green]ascii:[/green]    [yellow]{tipos_archivo['ASCII']}[/yellow]

"""
    
    filetype_panel = Panel(
        filetype_content,
        title="[bold green]FILE TYPES[/bold green]",
        border_style="yellow",
        padding=(0, 2),
        width=39,
        height=8
    )
    
    # Panel 5: Bloques
    blocks_list = sorted(list(bloques_usados))[:10]
    blocks_str = ", ".join(str(b) for b in blocks_list)
    blocks_content = f"""
[green]Usados:[/green]  [yellow]{len(bloques_usados)}[/yellow]
[green]Primeros:[/green][yellow]{blocks_str}[/yellow]


"""
# [blue]Primeros:[/blue]        [yellow]{blocks_str}[/yellow]
    
    blocks_panel = Panel(
        blocks_content,
        title="[bold green]BLOQUES[/bold green]",
        border_style="yellow",
        padding=(0, 2),
        width=39,
        height=8
    )
    
    # Distribuir en dos columnas con ancho fijo
    columns_row1 = Columns([physical_panel, format_panel], padding=1)
    columns_row2 = Columns([capacity_panel, filetype_panel], padding=1)
    columns_row3 = Columns([blocks_panel], padding=1)
    
    console.print(title_panel)
    console.print(columns_row1)
    console.print(columns_row2)
    console.print(columns_row3)
    
    dsk.list_files(simple=False, use_rich=True, show_title=False)

@disc.command(cls=CustomCommand)
@click.argument("disc_name", required=True)
@click.option("-A", "--drive-a", is_flag=True, help="Show info for disc in drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Show info for disc in drive B")
def insert(disc_name, drive_a, drive_b):
    """Insert existing disc into specified drive."""
    drive_manager = DriveManager()
    
    # Validar que solo se especifique una opción
    if drive_a and drive_b:
        blank_line(1)
        error("Cannot specify both -A and -B options. Choose one drive.")
        blank_line(1)
        return
    
    if not drive_a and not drive_b:
        blank_line(1)
        error("Please specify a drive using -A or -B option.")
        blank_line(1)
        return
    
    if disc_name is None:
        blank_line(1)
        error("Please provide a disc name to insert.")
        blank_line(1)
        return
    
    
    disc_name = str(system.process_dsk_name(disc_name))
    disc_path = Path(f"{disc_name}")
    
    drive = None
    if drive_a:
        drive = 'A'
    elif drive_b:
        drive = 'B'
    else:
        error("Please specify a drive using -A or -B option.\n")
        return
    
    if not disc_path.exists():
        blank_line(1)
        error(f"disc file not found: {disc_path}")
        blank_line(1)
        return
    # Comprobar si el disco ya está insertado en la unidad
    already_in_a = drive_manager.read_drive_a() == disc_name
    already_in_b = drive_manager.read_drive_b() == disc_name
    
    if drive == 'A':
        if already_in_a or already_in_b:
            blank_line(1)
            warn(f"disc '{Path(disc_name).name}' is already inserted.")
            # console.print(f"   [blue]File:[/blue] [yellow]{Path(disc_name).name}[/yellow]")
            blank_line(1)
            drive_manager.drive_table()
            return
        # Si el disco existe pero no está en ninguna unidad, también mostrar el mensaje
        if disc_path.exists():
            # warn(f"disc {Path(disc_name).name} exists not creating new one.")
            # console.print(f"   [blue]File:[/blue] [yellow]{Path(disc_name).name}[/yellow]")
            blank_line(1)
            drive_manager.insert_drive_a(disc_name)
            blank_line(1)
            drive_manager.drive_table()
            return
        drive_manager.insert_drive_a(disc_name)
        blank_line(1)
        drive_manager.drive_table()
    elif drive == 'B':
        if already_in_b or already_in_a:
            blank_line(1)
            warn(f"disc '{Path(disc_name).name}' is already inserted.")
            # console.print(f"   [blue]File:[/blue] [yellow]{Path(disc_name).name}[/yellow]")
            blank_line(1)
            drive_manager.drive_table()
            return
        if disc_path.exists():
            # warn(f"disc {Path(disc_name).name} exists not creating new one.")
            blank_line(1)
            console.print(f"   [blue]File:[/blue] [yellow]{Path(disc_name).name}[/yellow]")
            blank_line(1)
            drive_manager.insert_drive_b(disc_name)
            blank_line(1)
            drive_manager.drive_table()
            return
        drive_manager.insert_drive_b(disc_name)
        blank_line(1)
        drive_manager.drive_table()
    blank_line(1)
    
@disc.command(cls=CustomCommand)
@click.option("-A", "--drive-a", is_flag=True, help="Show info for disc in drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Show info for disc in drive B")
def eject(drive_a, drive_b):
    """Eject disc from drive selected or specified."""
    drive_manager = DriveManager()
    disc_select = drive_manager.read_drive_select().upper()
    # Validar que solo se especifique una opción
    if drive_a and drive_b:
        blank_line(1)
        drive_manager.eject(disc_select)
        drive_manager.drive_table()
        blank_line(1)
        return
    else:
        drive = None
        if drive_a:
            disc_select = 'A'
        elif drive_b:
            disc_select = 'B'
        blank_line(1)
        drive_manager.eject(disc_select)
        drive_manager.drive_table()