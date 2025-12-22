

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
import tempfile
from cpcready.utils import console, system, DriveManager, cassetteManager, SystemCPM
from cpcready.utils.click_custom import CustomCommand, RichCommand, CustomGroup
from cpcready.utils.console import info2, ok, debug, warn, error, message,blank_line,banner
from cpcready.utils.version import add_version_option_to_group
from rich.console import Console
from rich.panel import Panel
from cpcready.pydsk.dsk import DSK
from cpcready.pycdt import CDT, DataHeader

console = Console()

def convert_to_dos(file_path):
    """Convert file from Unix (LF) to DOS (CRLF) format."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Convertir LF a CRLF (Unix to DOS)
        # Primero eliminar cualquier CR existente para evitar duplicados
        content = content.replace(b'\r\n', b'\n')
        content = content.replace(b'\r', b'\n')
        # Luego convertir todos los LF a CRLF
        content = content.replace(b'\n', b'\r\n')
        
        # Crear archivo temporal con el contenido convertido
        tmp = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.tmp')
        tmp.write(content)
        tmp.close()
        
        return tmp.name
    except Exception as e:
        debug(f"Error converting to DOS format: {e}")
        return None

def is_header(ruta):
    with open(ruta, "rb") as f:
        cabecera = f.read(128)
        if len(cabecera) < 128:
            return None, None
        
        # El byte 0 debe estar en el rango válido de tipos AMSDOS (0-2 normalmente)
        if cabecera[0] > 2:
            return None, None
        
        # Verificar que nombre y extensión sean ASCII válidos (letras/números)
        try:
            nombre_str = cabecera[1:9].decode("ascii").strip()
            ext_str = cabecera[9:12].decode("ascii").strip()
            # Debe tener al menos un carácter válido en el nombre
            if not nombre_str or not nombre_str.replace(" ", "").isalnum():
                return None, None
        except:
            return None, None
        
        # Load address: bytes 21-22 (little endian)
        load_addr = cabecera[21] + (cabecera[22] << 8)
        
        # Exec address: bytes 26-27 (little endian)
        exec_addr = cabecera[26] + (cabecera[27] << 8)
        
        return load_addr, exec_addr

def add_ASCII_to_tape(tape_name, input_file, speed, name):
    tape_path = Path(tape_name)
    if not tape_path.exists():
        error(f"Tape file not found: {tape_name}")
        return
    try:
        cdt = CDT(str(tape_path))
        with open(input_file, 'rb') as f:
            content = bytearray(f.read())
        amsdos_name = name if name else Path(input_file).name.upper()
        if len(amsdos_name) > 16:
            amsdos_name = amsdos_name[:16]
        header = cdt.create_data_header(
            filename=amsdos_name,
            load_addr=0,
            exec_addr=0,
            file_type=DataHeader.FT_ASCII
        )
        # Guardar el nombre real en el último bloque añadido
        cdt.add_file(content, header, int(speed))
        # Buscar el último bloque tipo TurboSpeed con sync byte 0x16 y añadir atributo filename_real
        for block in reversed(cdt.blocks):
            if hasattr(block, 'data') and len(block.data) > 0 and block.data[0] == 0x16:
                block.filename_real = amsdos_name
                break
        debug(f"Bloques CDT tras añadir: {[type(b).__name__ for b in cdt.blocks]}")
        cdt.save()
        ok(f"File '{input_file}' saved successfully.")
    except Exception as e:
        error(f"Error adding ASCII file to tape: {e}")  


def aux_int(value_str):
    """Helper para convertir string a int soportando hex (0x)"""
    if isinstance(value_str, int):
        return value_str
    if value_str.startswith('0x') or value_str.startswith('&') or value_str.startswith('$'):
        return int(value_str.replace('&', '0x').replace('$', '0x'), 16)
    return int(value_str)

def add_BIN_to_tape(tape_name, input_file, speed, name, load_addr, exec_addr):
    tape_path = Path(tape_name)
    if not tape_path.exists():
        error(f"Tape file not found: {tape_name}")
        return
    try:
        cdt = CDT(str(tape_path))
        with open(input_file, 'rb') as f:
            content = bytearray(f.read())
        amsdos_name = name if name else Path(input_file).name.upper()
        if len(amsdos_name) > 16:
            amsdos_name = amsdos_name[:16]
        load_addr = aux_int(load) if load else 0
        exec_addr = aux_int(exec) if exec else 0
        header = cdt.create_data_header(
            filename=amsdos_name,
            load_addr=load_addr,
            exec_addr=exec_addr,
            file_type=DataHeader.FT_BIN
        )
        type_str = f"[blue]BIN[/blue] (load: {hex(load_addr)}, exec: {hex(exec_addr)})"
        console.print(f"Adding [cyan]{input_file}[/cyan] as [yellow]{amsdos_name}[/yellow] {type_str}...")
        cdt.add_file(content, header, int(speed))
        cdt.save()
        ok(f"File '{input_file}' added successfully.")
        
    except Exception as e:
        error(f"Error adding BIN file to tape: {e}")

def add_RAW_to_tape(tape_name, input_file, speed):
    tape_path = Path(tape_name)
    if not tape_path.exists():
        error(f"Tape file not found: {tape_name}")
        return
    try:
        cdt = CDT(str(tape_path))
        with open(input_file, 'rb') as f:
            content = bytearray(f.read())
        # RAW: no se pasa cabecera, solo los datos y la velocidad
        cdt.add_file(content, None, int(speed))
        cdt.save()
        ok(f"File '{input_file}' added as RAW to '{tape_path.name}'.")
    except Exception as e:
        error(f"Error adding RAW file to tape: {e}")



@click.command(cls=RichCommand)
@click.argument("file_name", required=True)
@click.argument("type_file", required=False, type=click.Choice(["a", "b", "p", "r"], case_sensitive=True))
@click.argument("load_addr", required=False)
@click.argument("exec_addr", required=False)
@click.option("-A", "--drive-a", is_flag=True, help="Save file to virtual disc in drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Save file to virtual disc in drive B")
def save(file_name, type_file, load_addr, exec_addr, drive_a, drive_b):
    """
    Save a file to a virtual tape or disc (DSK image) in CPCReady.

    This command allows you to save files in different formats to a virtual disc (A/B) or tape, automatically converting line endings to DOS format (CRLF) for compatibility.

    Type options:
        a : ASCII/Data file (no AMSDOS header)
                - Use for plain text or BASIC files (.BAS) without AMSDOS header.
                - Example: save myfile.bas a -A

        b : Binary file with AMSDOS header
                - Requires load_addr and optionally exec_addr.
                - Adds AMSDOS header if missing.
                - Example: save myfile.bin b 0x4000 0x4000 -A

        p : Program file with AMSDOS header
                - Preserves existing AMSDOS header if present.
                - Example: save myprog.bin p -A
                
        r : RAW file (no AMSDOS header)

    Arguments:
        file_name   : Path to the file to save.
        type_file   : File type (a, b, p). If omitted, auto-detects based on file extension/header.
        load_addr   : (For type 'b') Load address in hex (e.g., 0x4000 or &4000).
        exec_addr   : (For type 'b') Exec address in hex (optional).

    Options (only for disc saving):
        -A, --drive-a   : Save to virtual disc in drive A
        -B, --drive-b   : Save to virtual disc in drive B

    Examples (disc saving):
        cpc save myfile.bas a -A
        cpc save myfile.bin b 0x4000 0x4000 -B
        cpc save myprog.bin p -A
        cpc save myfile.txt        # Auto-detect type and save
        
    Examples (tape saving):
        cpc save myfile.bas a
        cpc save myfile.bin b 0x4000 0x4000
        cpc save myprog.bin p
        cpc save myfile.txt        # Auto-detect type and save
        
    Notes:
        - Command Tape/Disc is determined by current storage mode in CPCReady settings.
        - If no type is specified, the command will auto-detect based on file extension and header.
        - For binary files ('b'), load_addr is required. Exec_addr is optional (defaults to load_addr).
        - ASCII files ('a') are saved without AMSDOS header.
        - Program files ('p') preserve any existing AMSDOS header.
        - The file is converted to DOS format (CRLF) before saving.
        - After saving, the updated file list will be shown.
        - If neither -A nor -B is specified, the default drive (cpc A or cpc B) currently defined in CPCReady will be used.

    """
    

    
    # Verificar que el archivo existe
    if not Path(file_name).exists():
        blank_line(1)
        error(f"File '{file_name}' not found.")
        blank_line(1)
        return    
    
    # Obtener el nombre del disco usando DriveManager
    drive_manager = DriveManager()
    system_cpm = SystemCPM()
    
    cassette_mgr = cassetteManager()
    storage_mode = system_cpm.get_storage()
    blank_line(1)
    if storage_mode == "disc":
        console.print(Panel.fit("[bold white]Saving to virtual disc (DSK)[/bold white]", style="bright_yellow"))
    elif storage_mode == "tape":
        console.print(Panel.fit("[bold white]Saving to virtual tape (CDT)[/bold white]", style="bright_yellow"))

    disc_name = drive_manager.get_disc_name(drive_a, drive_b)
    
    if disc_name is None:
        error("No disc inserted in the specified drive.")
        return
    
    # Obtener el user number (por defecto 0)
    user_number = str(system_cpm.get_user_number())

    # Convertir archivo a formato DOS (CRLF)
    blank_line(1)
    info2("Converting file to DOS format (CRLF)...")
    dos_file = convert_to_dos(file_name)
    
    if dos_file is None:
        warn("Could not convert to DOS format, using original file")
        dos_file = file_name
        cleanup_temp = False
    else:
        debug(f"Converted to DOS format: {dos_file}")
        cleanup_temp = True
    
    try:
        # Verificar si el archivo tiene cabecera AMSDOS
        header_load_addr, header_exec_addr = is_header(dos_file)
    
        if header_load_addr is not None:
            info2(f"File '{file_name}' has AMSDOS header.")
            console.print(f"  [blue]Load address:[/blue] [yellow]&{header_load_addr:04X}[/yellow]")
            console.print(f"  [blue]Exec address:[/blue] [yellow]&{header_exec_addr:04X}[/yellow]")
            # Si el archivo tiene cabecera y no se especificó tipo, preservarla
            # NO forzamos type_file aquí, dejamos que el usuario o el auto-detect decidan
        else:
            info2(f"File '{file_name}' has no AMSDOS header.")
        
        if type_file is None:
            # Sin tipo especificado: detectar automáticamente
            
            if storage_mode == "disc":
                try:
                    # Guardar en disco
                    dsk = DSK(disc_name)
                    
                    # Obtener nombre del archivo sin path
                    file_base_name = Path(file_name).name.upper()
                    
                    # Si tiene cabecera AMSDOS, preservarla usando file_type=0 (binario)
                    # El método write_file detectará la cabecera existente y la preservará
                    if header_load_addr is not None:
                        dsk.write_file(dos_file, dsk_filename=file_base_name, file_type=0, 
                                    user=int(user_number), force=True)
                    # Detectar tipo según extensión para archivos sin cabecera
                    elif file_base_name.endswith('.BAS'):
                        # BASIC ASCII (sin cabecera AMSDOS - guardar como RAW)
                        debug("Auto-detected as BASIC ASCII file (.BAS)")
                        dsk.write_file(dos_file, dsk_filename=file_base_name, file_type=-1, user=int(user_number), force=True)
                    elif file_base_name.endswith('.BIN'):
                        # Binario sin cabecera - añadir cabecera AMSDOS
                        debug("Auto-detected as BINARY file (.BIN)")
                        dsk.write_file(dos_file, dsk_filename=file_base_name, file_type=2, 
                                    load_addr=0x4000, exec_addr=0x4000, 
                                    user=int(user_number), force=True)
                    else:
                        # Por defecto: ASCII sin cabecera (RAW)
                        debug("Plain file without header, saving as RAW")
                        dsk.write_file(dos_file, dsk_filename=file_base_name, file_type=-1, 
                                    user=int(user_number), force=True)
                    
                    dsk.save()
                    ok(f"File '{file_name}' saved successfully.")
                    
                    # Mostrar listado actualizado
                    blank_line(1)
                    dsk.list_files(simple=False, use_rich=True)
                except Exception as e:
                    error(f"Failed to save file: {e}")
                    return
            elif storage_mode == "tape":
                # Guardar en cinta
                tape_name = cassette_mgr.get_tape()
                cdt = CDT(str(tape_name))
                add_ASCII_to_tape(tape_name, file_name, "2000", Path(file_name).stem.upper())
                blank_line(1)
                # Recargar CDT desde disco para mostrar el listado actualizado
                cdt = CDT(str(tape_name))
                cdt.list_files(show_title=True, title=Path(tape_name).name)

        elif type_file == "a":
            if storage_mode == "disc":
                # ASCII/Data file sin cabecera AMSDOS
                try:
                    dsk = DSK(disc_name)
                    file_base_name = Path(file_name).name.upper()
                    # Modo -1 = RAW (sin cabecera AMSDOS)
                    dsk.write_file(dos_file, dsk_filename=file_base_name, file_type=-1, user=int(user_number), force=True)
                    dsk.save()
                    ok(f"File '{file_name}' saved successfully.")
                    blank_line(1)
                    dsk.list_files(simple=False, use_rich=True)
                except Exception as e:
                    error(f"Failed to save file: {e}")
                    return
            elif storage_mode == "tape":
                try:
                    tape_name = cassette_mgr.get_tape()
                    cdt = CDT(str(tape_name))
                    add_ASCII_to_tape(tape_name, file_name, "2000", Path(file_name).stem.upper())
                    blank_line(1)
                    cdt = CDT(str(tape_name))
                    cdt.list_files(show_title=True, title=Path(tape_name).name)
                    blank_line(1)
                except Exception as e:
                    error(f"Failed to save file to tape: {e}")
                    return
        elif type_file == "r":
            if storage_mode == "tape":
                try:
                    tape_name = cassette_mgr.get_tape()
                    cdt = CDT(str(tape_name))
                    add_RAW_to_tape(tape_name, file_name, "2000")
                    blank_line(1)
                    cdt = CDT(str(tape_name))
                    cdt.list_files(show_title=True, title=Path(tape_name).name)
                    blank_line(1)
                except Exception as e:
                    error(f"Failed to save RAW file to tape: {e}")
                    return
            elif storage_mode == "disc":
                try:
                    dsk = DSK(disc_name)
                    file_base_name = Path(file_name).name.upper()
                    # RAW puro: file_type=-1, sin cabecera AMSDOS
                    dsk.write_file(dos_file, dsk_filename=file_base_name, file_type=-1, user=int(user_number), force=True)
                    dsk.save()
                    ok(f"File '{file_name}' saved as RAW to disc.")
                    blank_line(1)
                    dsk.list_files(simple=False, use_rich=True)
                except Exception as e:
                    error(f"Failed to save RAW file to disc: {e}")
                    return
                
        elif type_file == "p":
            # Program file con cabecera AMSDOS
            if storage_mode == "disc":
                try:
                    dsk = DSK(disc_name)
                    file_base_name = Path(file_name).name.upper()
                    # Modo 0 = Binario con cabecera AMSDOS
                    dsk.write_file(dos_file, dsk_filename=file_base_name, file_type=0, 
                                load_addr=header_load_addr or 0, exec_addr=header_exec_addr or 0,
                                user=int(user_number), force=True, read_only=True)
                    dsk.save()
                    ok(f"File '{file_name}' saved successfully.")
                    blank_line(1)
                    dsk.list_files(simple=False, use_rich=True)
                except Exception as e:
                    error(f"Failed to save file: {e}")
                    return
            elif storage_mode == "tape":
                try:
                    tape_name = cassette_mgr.get_tape()
                    cdt = CDT(str(tape_name))
                    # Añadir como BIN conservando cabecera AMSDOS si existe
                    if header_load_addr is not None:
                        add_BIN_to_tape(tape_name, file_name, "2000", Path(file_name).stem.upper(), header_load_addr, header_exec_addr)
                    else:
                        # Si no hay cabecera, grabar como ASCII (sin cabecera AMSDOS)
                        add_ASCII_to_tape(tape_name, file_name, "2000", Path(file_name).stem.upper())
                    blank_line(1)
                    cdt = CDT(str(tape_name))
                    cdt.list_files(show_title=True, title=Path(tape_name).name)
                    blank_line(1)
                except Exception as e:
                    error(f"Failed to save program file to tape: {e}")
                    return
                
        elif type_file == "b":
            # Binary file con direcciones específicas

            # Validar que se proporcionaron las direcciones
            if load_addr is None:
                error("Binary type 'b' requires load address. Usage: save file.bin b 0x4000 [0x4000]")
                return

            dsk = DSK(disc_name)
            file_base_name = Path(file_name).name.upper()
            
            # Convertir direcciones hexadecimales
            if isinstance(load_addr, str):
                if load_addr.startswith(('0x', '0X')):
                    load_address = int(load_addr, 16)
                elif load_addr.startswith('&'):
                    load_address = int(load_addr[1:], 16)
                else:
                    load_address = int(load_addr)
            else:
                load_address = int(load_addr)
            
            # Exec address: usar load_address si no se especifica
            if exec_addr is None:
                exec_address = load_address
            elif isinstance(exec_addr, str):
                if exec_addr.startswith(('0x', '0X')):
                    exec_address = int(exec_addr, 16)
                elif exec_addr.startswith('&'):
                    exec_address = int(exec_addr[1:], 16)
                else:
                    exec_address = int(exec_addr)
            else:
                exec_address = int(exec_addr)
            
            if storage_mode == "disc":
                # Modo 2 = Binario con cabecera AMSDOS
                dsk.write_file(file_name, dsk_filename=file_base_name, file_type=2, 
                            load_addr=load_address, exec_addr=exec_address,
                            user=int(user_number), force=True)
                dsk.save()
                ok(f"File '{file_name}' saved successfully.")
                blank_line(1)
                dsk.list_files(simple=False, use_rich=True)
            elif storage_mode == "tape":
                add_BIN_to_tape(cassette_mgr.get_tape(), file_name, "2000", Path(file_name).stem.upper(), load_address, exec_address)
                blank_line(1)
                # recargamos CDT para mostrar el listado de ficheros actualizado
                cdt = CDT(str(cassette_mgr.get_tape()))
                cdt.list_files(show_title=True, title=Path(cassette_mgr.get_tape()).name)
    finally:
        # Limpiar archivo temporal si se creó
        if cleanup_temp and dos_file and dos_file != file_name:
            import os
            try:
                os.unlink(dos_file)
                debug(f"Temporary DOS file deleted: {dos_file}")
            except Exception:
                pass  # Ignorar errores al eliminar archivo temporal

