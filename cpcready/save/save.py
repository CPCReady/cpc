
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
import os
import tempfile
from pathlib import Path
from cpcready.utils import DriveManager, SystemCPM
from cpcready.utils.click_custom import CustomCommand
from cpcready.utils.console import info2, ok, debug, error, blank_line
from rich.console import Console
from cpcready.pydsk.dsk import DSK

console = Console()

@click.command(cls=CustomCommand)
@click.argument("file_name", required=True)
@click.option(
    "-t", "--type", "file_type",
    type=click.Choice(["0", "1", "2"]),
    help="File type: 0=ASCII, 1=BINARY, 2=RAW"
)
@click.option("-c", "--load", "load_addr", help="Load address (hex, e.g., C000)")
@click.option("-e", "--exec", "exec_addr", help="Execute address (hex, e.g., C000)")
@click.option("-f", "--force", is_flag=True, help="Force overwrite if file exists")
@click.option("-o", "--read-only", is_flag=True, help="Mark as read-only")
@click.option("-s", "--system", is_flag=True, help="Mark as system file")
@click.option("-u", "--user", type=int, help="User number (0-15)")
@click.option("-A", "--drive-a", is_flag=True, help="Use drive A")
@click.option("-B", "--drive-b", is_flag=True, help="Use drive B")
def save(
    file_name, file_type, load_addr, exec_addr,
    force, read_only, system, user, drive_a, drive_b
):
    """Import file to DSK (exactly like iDSK -i).
    
    FILE_NAME: File to import
    
    Types (same as iDSK):
      -t 0: ASCII mode - saves file without AMSDOS header (text files)
      -t 1: BINARY mode - adds AMSDOS header (default for .BAS files)
      -t 2: RAW mode - no processing at all
    
    Default behavior (no -t):
      - Adds AMSDOS header to the file (like iDSK)
      - Does NOT tokenize BASIC files
    
    Examples:
      cpc save file.bas                    # Add header (default)
      cpc save prog.bas -t 0               # No header (pure data)
      cpc save prog.bin -t 1 -c 4000       # Binary at 0x4000
      cpc save file.txt -t 2               # Raw copy
    """
    
    # Verificar archivo existe
    if not Path(file_name).exists():
        blank_line(1)
        error(f"File '{file_name}' not found.")
        blank_line(1)
        return
    
    # Obtener disco
    drive_manager = DriveManager()
    system_cpm = SystemCPM()
    
    disc_name = drive_manager.get_disc_name(drive_a, drive_b)
    if disc_name is None:
        error("No disc inserted.")
        return
    
    # User number
    if user is None:
        user_number = system_cpm.get_user_number()
    else:
        if not (0 <= user <= 15):
            error("User number must be 0-15.")
            return
        user_number = user
    
    # Leer archivo completo
    with open(file_name, "rb") as f:
        file_data = bytearray(f.read())
    
    # Verificar si tiene header AMSDOS
    has_header = False
    if len(file_data) >= 128:
        checksum = sum(file_data[0:67]) & 0xFFFF
        stored_checksum = file_data[67] | (file_data[68] << 8)
        has_header = (checksum == stored_checksum)
    
    # Default type: 1 (BINARY) like iDSK
    if file_type is None:
        file_type = "1"
    
    # COMPORTAMIENTO EXACTO DE iDSK:
    # Si hay -c o -e, fuerza modo BINARY (tipo 1)
    if load_addr or exec_addr:
        file_type = "1"
    
    blank_line(1)
    
    # MODE_ASCII (0): Save WITHOUT AMSDOS header
    if file_type == "0":
        info2("MODE_ASCII (no header)")
        # In ASCII mode, delete the header if there is one
        if has_header:
            debug("File has AMSDOS header, removing it")
            file_data = file_data[128:]
        else:
            debug("File has no AMSDOS header")
    
    # MODE_BINAIRE (1): Add AMSDOS header if not present
    elif file_type == "1":
        info2("MODE_BINAIRE (add header if needed)")
        if not has_header:
            debug("Automatically generating header for file")
            
            # Parse addresses
            load = int(load_addr, 16) if load_addr else 0
            exec = int(exec_addr, 16) if exec_addr else 0
            
            # Crear header AMSDOS
            file_size = len(file_data)
            if file_size >= 0x10000:
                error("Creating header for files larger than 64K not supported")
                return
            
            header = bytearray(128)
            # User number
            header[0] = user_number
            # Filename (8 chars)
            base_name = Path(file_name).stem.upper()[:8]
            for i, c in enumerate(base_name):
                header[1 + i] = ord(c)
            # Padding con espacios para completar 15 bytes del nombre
            for i in range(len(base_name), 8):
                header[1 + i] = ord(' ')
            # Extension (3 chars)
            ext = Path(file_name).suffix[1:].upper()[:3] if Path(file_name).suffix else ""
            for i, c in enumerate(ext):
                header[9 + i] = ord(c)
            for i in range(len(ext), 3):
                header[9 + i] = ord(' ')
            # Completar FileName hasta byte 15 (0x01-0x0F)
            for i in range(12, 16):
                header[i] = 0
            
            # Block number, last block, file type
            header[0x10] = 0  # Block number
            header[0x11] = 0  # Last block  
            header[0x12] = 2  # File type (2=BINARY, like iDSK)
            
            # Data length
            header[0x18] = file_size & 0xFF
            header[0x19] = (file_size >> 8) & 0xFF
            
            # Load address
            header[0x15] = load & 0xFF
            header[0x16] = (load >> 8) & 0xFF
            
            # First block (always 0 for user files)
            header[0x17] = 0
            
            # Entry address
            header[0x1A] = exec & 0xFF
            header[0x1B] = (exec >> 8) & 0xFF
            
            # Logical length (same as data length for most files)
            header[0x40] = file_size & 0xFF
            header[0x41] = (file_size >> 8) & 0xFF
            
            # Calcular checksum
            checksum = sum(header[0:67]) & 0xFFFF
            header[67] = checksum & 0xFF
            header[68] = (checksum >> 8) & 0xFF
            
            # Insertar header
            file_data = header + file_data
            
            debug(f"Load: &{load:04X}, Exec: &{exec:04X}")
        else:
            debug("File already has an header")
    
    # MODE_RAW (2): No header processing
    elif file_type == "2":
        info2("Using raw mode, no header")
    
    # Escribir archivo procesado al DSK
    try:
        dsk = DSK(disc_name)
        file_base_name = Path(file_name).name.upper()
        
        # Guardar archivo modificado temporalmente
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name
        
        try:
            # Escribir con file_type=-1 (RAW) porque ya procesamos el header
            dsk.write_file(tmp_path, dsk_filename=file_base_name, file_type=-1,
                         user=user_number, force=force,
                         read_only=read_only, system=system)
            dsk.save()
            
            ok(f"File '{file_name}' imported successfully.")
            blank_line(1)
            dsk.list_files(simple=False, use_rich=True)
        finally:
            import os
            os.unlink(tmp_path)
        
    except Exception as e:
        blank_line(1)
        error(f"Failed to import: {e}")
        import traceback
        traceback.print_exc()

