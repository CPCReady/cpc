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

"""
Clase principal CDT para gestión de imágenes de cinta Amstrad CPC (formato TZX/CDT)
"""

import os
from .structures import (
    CDTHeader, BlockNormalSpeed, BlockTurboSpeed, BlockPureTone, 
    BlockDifferentPulses, BlockPureData, BlockPause, BlockGroupStart, 
    BlockGroupEnd, BlockDescription, BlockArchiveInfo, DataHeader,
    AUX_GET_CRC, DEF_PAUSE_HEADER, DEF_PAUSE_DATA, DEF_PAUSE_FILE
)
from .exceptions import CDTError, CDTFormatError, CDTFileNotFoundError, CDTReadError, CDTWriteError

class CDT:
    """
    Clase para manipular imágenes de cinta CDT/TZX
    """

    BLOCKS = {
        BlockNormalSpeed.ID: BlockNormalSpeed,
        BlockTurboSpeed.ID: BlockTurboSpeed,
        BlockPureTone.ID: BlockPureTone,
        BlockDifferentPulses.ID: BlockDifferentPulses,
        BlockPureData.ID: BlockPureData,
        BlockPause.ID: BlockPause,
        BlockGroupStart.ID: BlockGroupStart,
        BlockGroupEnd.ID: BlockGroupEnd,
        BlockDescription.ID: BlockDescription,
        BlockArchiveInfo.ID: BlockArchiveInfo
    }

    def __init__(self, filename=None):
        self.header = CDTHeader()
        self.blocks = []
        self.filename = filename
        
        if filename and os.path.exists(filename):
            self.load(filename)

    def compose(self):
        content = bytearray()
        content.extend(self.header.compose())
        for block in self.blocks:
            content.extend(block.compose())
        return content

    def add_block(self, content):
        if len(content) > 0:
            ID = content[0]
            content = content[1:]
            if ID in self.BLOCKS:
                b = self.BLOCKS[ID]()
                content = b.set(content)
                self.blocks.append(b)
                self.add_block(content)
            else:
                raise CDTFormatError(f"unsupported block ID {hex(ID)}")

    def set(self, content):
        content = self.header.set(content)
        self.blocks = []
        self.add_block(content)

    def create(self):
        """Create new empty CDT (replaces format)"""
        self.header = CDTHeader()
        self.blocks = []
        start_block = BlockPause()
        self.blocks = [start_block]

    def format(self):
        """Alias for create (compatibility)"""
        self.create()

    def save(self, outputfile=None):
        """Save CDT to file"""
        if outputfile:
            self.filename = outputfile
            
        if not self.filename:
            raise CDTWriteError("No filename specified for save")
            
        content = self.compose()
        try:
            with open(self.filename, 'wb') as fd:
                fd.write(content)
        except IOError as e:
            raise CDTWriteError(f"Error trying to create the file {self.filename}: {e}")
            
    def write(self, outputfile):
        """Alias for save (compatibility)"""
        self.save(outputfile)

    def load(self, inputfile):
        """Load CDT from file"""
        if not os.path.exists(inputfile):
            raise CDTFileNotFoundError(f"File not found: {inputfile}")
            
        self.filename = inputfile
        content = bytearray()
        chunksz = 512
        try:
            with open(inputfile, 'rb') as fd:
                bytes_read = fd.read(chunksz)
                while bytes_read:
                    content.extend(bytes_read)
                    bytes_read = fd.read(chunksz)
            self.set(content)
            return True      
        except IOError as e:
            raise CDTReadError(f"Could not read file {inputfile}: {e}")
        except CDTFormatError:
            raise
        except Exception as e:
            raise CDTError(f"Error processing file: {e}")
            
    def read(self, inputfile):
        """Alias for load (compatibility)"""
        return self.load(inputfile)

    def _add_file(self, incontent, header, speed):
        # calculate total number of data segments of 256 bytes
        segments = []
        while len(incontent) > 0:
            segment = incontent[0:256]
            segments.append(segment)
            incontent = incontent[256:]

        while len(segments) > 0:
            """ Header """
            blocksegments = segments[0:8]
            header.block_sz = 0
            for s in blocksegments:
                header.block_sz = header.block_sz + len(s)
            header.last_block = 0x00 if len(segments) > 8 else 0xFF
            hblock = BlockTurboSpeed(speed, DEF_PAUSE_HEADER)
            hblock.data = header.compose()
            self.blocks.append(hblock)

            dblock = BlockTurboSpeed(speed, DEF_PAUSE_DATA)
            data = bytearray(b'\x16')  # sync byte for data
            """ data segments up to 8 (256 * 8 = 2K) """
            for s in blocksegments:
                # Check padding, all segments must be of 256 bytes
                if len(s) < 256: s.extend(0x00 for i in range(len(s), 256))
                crc = AUX_GET_CRC(s)
                data.extend(s)
                data.extend(crc.to_bytes(2, 'big'))  # !!! MSB first here
            data.extend(b'\xFF\xFF\xFF\xFF')  # trail
            dblock.data = data
            self.blocks.append(dblock)
            segments = segments[8:]
            header.block_id = header.block_id + 1
            header.first_block = 0x00

        endpause = BlockPause(DEF_PAUSE_FILE)
        self.blocks.append(endpause)

    def _add_raw(self, incontent, speed):
        block = BlockTurboSpeed(speed, DEF_PAUSE_FILE)
        data = bytearray(b'\x16')  # sync byte for data
        crc = AUX_GET_CRC(incontent)
        data.extend(data)
        data.extend(incontent)
        data.extend(crc.to_bytes(2, 'big'))
        data.extend(b'\xFF\xFF\xFF\xFF')
        block.data = data
        self.blocks.append(block)

    def add_file(self, incontent, header, speed):
        if header is not None:
            self._add_file(incontent, header, speed)
        else:
            self._add_raw(incontent, speed)
    
    def check(self):
        self.header.check()
        for b in self.blocks: b.check()

    def dump(self):
        self.header.dump()
        print("")
        print(len(self.blocks), "BLOCKS:")
        for b in self.blocks: b.dump()


    def create_data_header(self, filename: str, load_addr: int = 0, exec_addr: int = 0, 
                          file_type: int = DataHeader.FT_BIN) -> DataHeader:
        """Helper para crear una cabecera de datos"""
        header = DataHeader()
        
        # Limpiar y ajustar nombre (max 16 chars)
        if len(filename) > 16:
            filename = filename[:16]
        
        header.filename = filename
        header.addr_load = load_addr
        header.addr_start = exec_addr # Call address
        header.type = file_type
        
        return header

    def get_info(self) -> dict:
        """
        Obtiene información general de la cinta
        
        Returns:
            Diccionario con información de la cinta
        """
        return {
            'title': self.header.title,
            'version': f"{self.header.major}.{self.header.minor}",
            'blocks': len(self.blocks),
            'files': len(self._get_blocks_with_headers())
        }

    def _get_blocks_with_headers(self):
        """
        Identifica bloques que contienen cabeceras de archivos
        Returns:
            Lista de tuplas (bloque_datos, cabecera_parseada)
        """
        found = []
        for i, block in enumerate(self.blocks):
            # Solo considerar bloques TurboSpeed con cabecera AMSDOS (0x2C) o ASCII (0x16)
            if hasattr(block, 'data') and len(block.data) > 0:
                if block.data[0] == 0x2C:
                    try:
                        header = DataHeader()
                        header.set(block.data[1:])
                        # Solo añadir si el nombre es válido y tipo es BIN o ASCII
                        if header.filename.strip() and header.type in (0, 2):
                            found.append((block, header))
                    except Exception:
                        pass
                elif block.data[0] == 0x16:
                    header = DataHeader()
                    filename_real = getattr(block, 'filename_real', None)
                    if filename_real:
                        header.filename = filename_real
                    else:
                        # Buscar el nombre real en el bloque anterior si es cabecera AMSDOS
                        prev_block = self.blocks[i-1] if i > 0 else None
                        prev_name = None
                        if prev_block and hasattr(prev_block, 'data') and len(prev_block.data) > 0 and prev_block.data[0] == 0x2C:
                            try:
                                prev_header = DataHeader()
                                prev_header.set(prev_block.data[1:])
                                prev_name = prev_header.filename
                            except Exception:
                                pass
                        if prev_name:
                            header.filename = prev_name
                        else:
                            # Si no, usar el nombre del archivo CDT si existe
                            if self.filename and isinstance(self.filename, str):
                                header.filename = Path(self.filename).stem.upper()
                            else:
                                header.filename = "FILE"
                    header.type = 0  # ASCII
                    header.length = len(block.data) - 1
                    header.addr_load = 0
                    header.addr_start = 0
                    header.block_id = i+1
                    # Solo añadir si el nombre es válido
                    if header.filename.strip():
                        found.append((block, header))
        return found

    def list_files(self, simple: bool = False, use_rich: bool = True, show_title: bool = True, title: str = None) -> str:
        """
        Lista los archivos contenidos en la cinta
        
        Args:
            simple: Si True, formato compacto; si False, tabla detallada
            use_rich: Si True y Rich está disponible, usa formato Rich con colores
            show_title: Si True, muestra el título
        """
        files = self._get_blocks_with_headers()
        
        # Intentar usar Rich si está disponible y solicitado
        if use_rich and not simple:
            try:
                from rich.console import Console
                from rich.table import Table
                from rich.panel import Panel
                from rich import box

                console = Console()

                # Evitar markup en el título para prevenir errores de cierre de etiquetas
                table_title = title if title is not None else (f" ▶ {self.header.title}" if show_title else None)

                table = Table(
                    title=(" ▶ " + table_title.upper()) if table_title else None,
                    title_justify="left",
                    show_header=True,
                    header_style="bold white",
                    border_style="bright_yellow",
                    title_style="bold yellow",
                    box=box.ROUNDED
                )
                
                # Definir columnas
                table.add_column("File", style="cyan", no_wrap=True, width=16)
                table.add_column("Type", style="dim", width=12)
                table.add_column("Size", justify="right", style="green", width=8)
                table.add_column("Load", justify="center", style="yellow", width=10)
                table.add_column("Exec", justify="center", style="yellow", width=10)
                table.add_column("Block ID", justify="center", width=8)

                for block, header in files:
                    # Determinar tipo
                    file_type_str = "[dim]UNKNOWN[/dim]"
                    style = "[white]"
                    if header.type == 0:
                        file_type_str = "[cyan]ASCII[/cyan]"
                        style = "[bold cyan]"
                    elif header.type == 2:
                        file_type_str = "[blue]BIN[/blue]"
                        style = "[bold yellow]"
                    else:
                        file_type_str = f"[dim]Type {header.type}[/dim]"
                        style = "[white]"
                    filename = header.filename.rstrip('\x00')
                    table.add_row(
                        f"{style}{filename}[/]",
                        file_type_str,
                        str(header.length),
                        f"&{header.addr_load:04X}",
                        f"&{header.addr_start:04X}",
                        str(header.block_id)
                    )
                
                if not files:
                    # Si no hay archivos con cabecera, mostrar resumen de bloques raw
                     table.add_row("[dim](No headers found)[/dim]", "", "", "", "", "")

                console.print(table)
                
                # Mostrar resumen de bloques
                blocks_summary = f"[bold green]{len(self.blocks)}[/bold green] blocks total"
                console.print(Panel(blocks_summary, style="bright_yellow", expand=False))
                console.print()
                
                return None
                
            except ImportError:
                pass
        
        # Fallback texto simple
        output = []
        output.append(f"Tape: {self.header.title} (v{self.header.major}.{self.header.minor})")
        output.append("-" * 60)
        output.append(f"{'File':<16} {'Type':<10} {'Size':>6} {'Load':>6} {'Exec':>6} {'Blk':>3}")
        output.append("-" * 60)
        
        for block, header in files:
            filename = header.filename.rstrip('\x00')
            ftype = "BIN"
            if header.type == 0: ftype = "BAS"
            elif header.type == 1: ftype = "BAS+"
            
            output.append(f"{filename:<16} {ftype:<10} {header.length:>6} {hex(header.addr_load):>6} {hex(header.addr_start):>6} {header.block_id:>3}")
            
        return "\n".join(output)
