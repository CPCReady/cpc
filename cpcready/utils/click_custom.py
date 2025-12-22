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
import sys
import io

class FormattedStderr:
    """Wrapper for stderr that adds formatting to Click error messages"""
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.error_started = False
        self.error_ended = False
    
    def write(self, text):
        if isinstance(text, str):
            # Si empieza con "Usage:", es el inicio del mensaje de error
            if text.startswith('Usage:') and not self.error_started:
                self.error_started = True
                self.original_stderr.write('\n')  # Línea en blanco antes
                # Escribir en rojo
                self.original_stderr.write('\033[91m')  # Color rojo
                self.original_stderr.write(text)
                return len(text)
            
            # Si estamos en un error, seguir escribiendo en rojo
            if self.error_started and not self.error_ended:
                self.original_stderr.write(text)
                
                # Si encontramos la línea con "Error:", es el final
                if 'Error:' in text:
                    self.error_ended = True
                    self.original_stderr.write('\033[0m')  # Reset color
                    self.original_stderr.write('\n')  # Línea en blanco después
                
                return len(text)
        
        # Pasar todo lo demás directamente
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

def format_as_rich_table(items, headers, header_style="bold bright_yellow", border_style="yellow", col_styles=None, col_widths=None):
    """
    Helper function to format a list of items (tuples) as a Rich table.
    items: list of tuples (col1, col2)
    headers: tuple of (header1, header2)
    col_widths: tuple of (width1, width2) or None
    """
    if not items:
        return ""

    from rich.console import Console
    from rich.table import Table
    from rich import box
    import io

    table = Table(
        box=box.ROUNDED, 
        show_header=True, 
        header_style=header_style,
        border_style=border_style, 
        expand=False,
        padding=(0, 2),
        show_lines=False
    )
    
    col1_style = col_styles[0] if col_styles and len(col_styles) > 0 else "bold green"
    col2_style = col_styles[1] if col_styles and len(col_styles) > 1 else "white"
    
    width1 = col_widths[0] if col_widths and len(col_widths) > 0 else None
    width2 = col_widths[1] if col_widths and len(col_widths) > 1 else None

    table.add_column(headers[0], style=col1_style, width=width1)
    table.add_column(headers[1], style=col2_style, width=width2)

    for col1, col2 in items:
        table.add_row(col1, col2)

    sio = io.StringIO()
    console_temp = Console(file=sio, force_terminal=True)
    console_temp.print(table)
    return sio.getvalue()

def print_rich_panel_help(cmd, ctx):
    """Auxiliar para imprimir Usage y Help en un Panel Rich"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    import io

    # Construir Usage
    usage_pieces = cmd.collect_usage_pieces(ctx)
    usage_text = f"Usage: cpc {cmd.name} {' '.join(usage_pieces)}"
    
    # Construir Help text
    help_text = cmd.help or ""
    
    # Combinar en un Panel
    full_text = f"[bold white]{usage_text}[/bold white]\n\n[white]{help_text}[/white]"
    
    # Ancho calculado: 20 (col1) + 60 (col2) + 4 (padding interno) + 2 (bordes externos) + 1 (separador) = 87 aprox
    # Ajustamos a 86/88 para que coincida visualmente con las tablas que tienen padding (0,2)
    # Tabla: Border(1) + Pad(2) + 20 + Pad(2) + Border(1) + Pad(2) + 60 + Pad(2) + Border(1)
    # Total chars: 1+2+20+2+1+2+60+2+1 = 91 chars
    panel_width = 81
    
    panel = Panel(
        full_text,
        box=box.ROUNDED,
        border_style="bright_magenta",
        width=panel_width,
        padding=(1, 2)
    )
    
    sio = io.StringIO()
    console = Console(file=sio, force_terminal=True)
    console.print(panel)
    return sio.getvalue()

def print_rich_banner_panel():
    """Auxiliar para imprimir Banner en un Panel Rich"""
    from rich.console import Console
    from rich.panel import Panel
    from rich import box
    from cpcready.utils.version import get_banner_string
    import io

    banner_text = get_banner_string()

    panel_width = 81
    
    panel = Panel(
        banner_text,
        box=box.ROUNDED,
        border_style="bright_yellow",
        width=panel_width,
        padding=(1, 2)
    )
    
    sio = io.StringIO()
    console = Console(file=sio, force_terminal=True)
    console.print(panel)
    return sio.getvalue()

class RichCommand(CustomCommand):
    """
    Comando Click que muestra las opciones usando una tabla Rich y Panel de ayuda.
    """
    def get_help(self, ctx):
        """
        Sobreescribimos get_help para evitar la lógica del padre CustomCommand
        que imprime el banner en crudo. Aquí controlamos todo via format_help.
        """
        # Llamar directamente a la implementación base de click.Command
        formatter = ctx.make_formatter()
        self.format_help(ctx, formatter)
        return formatter.getvalue()

    def format_help(self, ctx, formatter):
        """
        Sobreescribe completamente el formato de ayuda.
        """
        # 1. Banner sin Panel (solo el texto formateado)
        if self.show_banner:
            try:
                from cpcready.utils.version import get_banner_string
                banner_str = get_banner_string()
                formatter.write(banner_str)
            except ImportError:
                pass
        
        # 2. Panel con Usage y Descripción
        # No usamos formatter.write_usage/heading sino que inyectamos el panel directo
        panel_str = print_rich_panel_help(self, ctx)
        formatter.write(f"\n{panel_str}")

        # 3. Opciones (esto llama a nuestro format_options que usa tablas)
        self.format_options(ctx, formatter)

        # 4. Epilog
        self.format_epilog(ctx, formatter)

    def format_options(self, ctx, formatter):
        """
        Sobreescribe el formateo de opciones para usar una tabla Rich.
        """
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)

        if opts:
            table_str = format_as_rich_table(
                opts, 
                ("Options", "Description"),
                header_style="bold bright_yellow",
                border_style="yellow",
                col_styles=("bold cyan", "white"),
                col_widths=(15, 55)
            )
            formatter.write(f"\n{table_str}")
        else:
             super().format_options(ctx, formatter)

class RichGroup(CustomGroup):
    """
    Grupo de comandos Click que muestra la lista de comandos y opciones usando tablas y paneles Rich.
    """
    def command(self, *args, **kwargs):
        """Override command to use RichCommand by default"""
        kwargs.setdefault('cls', RichCommand)
        return super().command(*args, **kwargs)

    def get_help(self, ctx):
        """
        Sobreescribimos get_help para evitar la lógica del padre CustomGroup
        que imprime el banner en crudo. Aquí controlamos todo via format_help.
        """
        # Llamar directamente a la implementación base de click.Group
        formatter = ctx.make_formatter()
        self.format_help(ctx, formatter)
        return formatter.getvalue()

    def format_help(self, ctx, formatter):
        """
        Sobreescribe completamente el formato de ayuda del grupo.
        """
        # 1. Banner sin Panel (solo el texto formateado)
        if self.show_banner:
            try:
                from cpcready.utils.version import get_banner_string
                banner_str = get_banner_string()
                formatter.write(banner_str)
            except ImportError:
                pass
        
        # 2. Panel con Usage y Descripción
        panel_str = print_rich_panel_help(self, ctx)
        formatter.write(f"\n{panel_str}")

        # 3. Opciones (nuestras tablas)
        self.format_options(ctx, formatter)

        # 4. Epilog
        self.format_epilog(ctx, formatter)

    def format_options(self, ctx, formatter):
        """
        Sobreescribe el formateo de opciones para usar una tabla Rich.
        """
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)

        if opts:
            table_str = format_as_rich_table(
                opts, 
                ("Options", "Description"),
                header_style="bold bright_yellow",
                border_style="yellow",
                col_styles=("bold cyan", "white"),
                col_widths=(15, 55)
            )
            formatter.write(f"\n{table_str}")
        
        self.format_commands(ctx, formatter)

    def format_commands(self, ctx, formatter):
        """
        Sobreescribe el formateo de comandos para usar una tabla Rich.
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue
            commands.append((subcommand, cmd.get_short_help_str(120)))

        if commands:
            table_str = format_as_rich_table(
                commands, 
                ("Command", "Description"),
                header_style="bold bright_yellow",
                border_style="yellow",
                col_styles=("bold green", "white"),
                col_widths=(15, 55)
            )
            formatter.write(f"\n{table_str}")
