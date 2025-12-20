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
import sys
import io

class FormattedStderr:
    """Wrapper for stderr that adds formatting to Click error messages"""
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.buffer = []
        self.in_error_sequence = False
    
    def write(self, text):
        if isinstance(text, str):
            # Detectar inicio de secuencia de error
            if text.startswith('Usage:') and not self.in_error_sequence:
                self.in_error_sequence = True
                self.original_stderr.write('\n')  # Línea en blanco antes
                self.original_stderr.write(text)
                return len(text)
            elif 'Error:' in text and self.in_error_sequence:
                self.original_stderr.write(text)
                self.original_stderr.write('\n')  # Línea en blanco después
                self.in_error_sequence = False
                return len(text)
            else:
                self.original_stderr.write(text)
                return len(text)
        else:
            return self.original_stderr.write(text)
    
    def flush(self):
        return self.original_stderr.flush()
    
    def __getattr__(self, name):
        return getattr(self.original_stderr, name)

# Aplicar el wrapper solo cuando se inicializa el módulo
if not hasattr(sys.stderr, '_cpcready_wrapped'):
    sys.stderr = FormattedStderr(sys.stderr)
    sys.stderr._cpcready_wrapped = True

class CustomCommand(click.Command):
    def __init__(self, *args, **kwargs):
        self.show_banner = kwargs.pop('show_banner', False)
        super().__init__(*args, **kwargs)
    
    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        if self.show_banner:
            try:
                from cpcready.utils.version import show_banner
                show_banner()  # Imprime el banner con Rich en color
            except ImportError:
                pass
        return f"\n{help_text}\n"

class CustomGroup(click.Group):
    def __init__(self, *args, **kwargs):
        self.show_banner = kwargs.pop('show_banner', False)
        super().__init__(*args, **kwargs)
    
    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        if self.show_banner:
            try:
                from cpcready.utils.version import show_banner
                show_banner()  # Imprime el banner con Rich en color
            except ImportError:
                pass
        return f"\n{help_text}\n"
    
    def command(self, *args, **kwargs):
        """Override command to use CustomCommand by default"""
        kwargs.setdefault('cls', CustomCommand)
        return super().command(*args, **kwargs)

class RichGroup(CustomGroup):
    """
    Grupo de comandos Click que muestra la lista de comandos usando una tabla Rich.
    """
    def format_commands(self, ctx, formatter):
        """
        Sobreescribe el formateo de comandos para usar una tabla Rich.
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue
            commands.append((subcommand, cmd))

        if commands:
            # Importaciones aquí para evitar dependencias circulares si las hubiera
            # y mantener limpio el namespace global si no se usa
            from rich.console import Console
            from rich.table import Table
            from rich import box
            from rich.style import Style
            import io

            # Preparamos la tabla
            table = Table(
                box=box.ROUNDED, 
                show_header=True, 
                header_style="bold bright_yellow",
                border_style="yellow", 
                expand=False,
                padding=(0, 2),
                show_lines=False
            )
            table.add_column("Command", style="bold green")
            table.add_column("Description", style="white")

            for subcommand, cmd in commands:
                help_text = cmd.get_short_help_str(120)
                table.add_row(subcommand, help_text)

            sio = io.StringIO()
            # force_terminal=True para asegurar códigos de color ANSI
            # No forzamos width para que sea 'auto' o default
            console_temp = Console(file=sio, force_terminal=True)
            console_temp.print(table)
            table_str = sio.getvalue()

            # Escribimos en el formatter de Click
            # Usamos write_paragraph no, mejor write directo pero dentro de una sección para consistencia visual
            # Aunque la tabla ya tiene su propio 'heading' visual, click añade 'Commands:'
            # Vamos a inyectarlo "raw"
            
            with formatter.section('Commands'):
                 formatter.write(f"\n{table_str}")
