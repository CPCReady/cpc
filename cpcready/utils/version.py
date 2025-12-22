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
Version utilities for cpcready commands.

Provides common version functionality for all commands.
"""

import click
from functools import wraps
from cpcready import __version__, __author__, __license__
from cpcready.utils.console import message, blank_line,warn
from rich.panel import Panel
from rich import print as rprint

def show_banner():
    """Display ASCII art banner."""
    from rich.console import Console
    console = Console()
    console.print(get_banner_string(), end='')

def get_banner_string():
    """Capture ASCII art banner as string."""
    from rich.console import Console
    import io
    
    sio = io.StringIO()
    console = Console(file=sio, force_terminal=True, width=81) 
    # Width 80 u otro para asegurar que no haga wrap raro dentro del panelç
    TextBanner=f"""
▞▀▖▛▀▖▞▀▖▛▀▖        ▌                              
▌  ▙▄▘▌  ▙▄▘▞▀▖▝▀▖▞▀▌▌ ▌                           
▌ ▖▌  ▌ ▖▌▚ ▛▀ ▞▀▌▌ ▌▚▄▌                           
▝▀ ▘  ▝▀ ▘ ▘▝▀▘▝▀▘▝▀▘▗▄▘  
CLI Toolchain v{__version__}                        
Copyright (c) 2025 {__author__}                        
License: {__license__}
    """


    
    TextInfo = """
Repository:https://github.com/CPCReady/cpc
Issue Tracker:https://github.com/CPCReady/cpc/issues
Docs:https://cpcready.github.io/docs
    """
    from rich.text import Text
    panel = Panel(Text(TextBanner, style="yellow"), border_style="yellow", style="yellow", width=81)
    panel_info = Panel(Text(TextInfo, style="yellow"), border_style="yellow", style="yellow", width=81)
    console.print(panel)
    # console.print(panel_info)
    
    
    # console.print(panel)
    # console.print("\n")
    # console.print("▞▀▖▛▀▖▞▀▖▛▀▖        ▌                              ", style="bold yellow")
    # console.print("▌  ▙▄▘▌  ▙▄▘▞▀▖▝▀▖▞▀▌▌ ▌                           ", style="bold yellow")
    # console.print("▌ ▖▌  ▌ ▖▌▚ ▛▀ ▞▀▌▌ ▌▚▄▌                           ", style="bold yellow")
    # console.print("▝▀ ▘  ▝▀ ▘ ▘▝▀▘▝▀▘▝▀▘▗▄▘                           ", style="bold yellow")
    # console.print(f"CLI Toolchain v{__version__}                        ", style="yellow", highlight=False)
    # console.print(f"Copyright (c) 2025 {__author__}                        ", style="yellow", highlight=False)
    # console.print(f"License: {__license__}                        ", style="yellow", highlight=False)
    # console.print("Repository: https://github.com/CPCReady/cpc                        ", style="yellow")
    # console.print("Issue Tracker: https://github.com/CPCReady/cpc/issues                        ", style="yellow")
    # console.print("Docs: https://cpcready.github.io/docs                        ", style="yellow")
    
    return sio.getvalue()


def show_version_info():
    """Display version information."""
    print(get_banner_string(), end='')
    print()  # Blank line after version info


def version_option_handler(ctx, param, value):
    """Click callback handler for --version option."""
    if not value or ctx.resilient_parsing:
        return
    show_version_info()
    ctx.exit()


def add_version_option(f):
    """
    Decorator to add --version option to any Click command.
    
    Usage:
        @add_version_option
        @click.command()
        def my_command():
            pass
    """
    return click.option('--version', is_flag=True, expose_value=False, 
                       is_eager=True, callback=version_option_handler,
                       help='Show version and exit')(f)


def add_version_option_to_group(f):
    """
    Decorator to add --version option to Click groups.
    
    Usage:
        @add_version_option_to_group
        @click.group()
        def my_group():
            pass
    """
    return click.option('--version', is_flag=True, expose_value=False,
                       is_eager=True, callback=version_option_handler,
                       help='Show version and exit')(f)