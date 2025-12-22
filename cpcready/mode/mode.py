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
from cpcready.utils import SystemCPM
from cpcready.utils.click_custom import CustomCommand, RichCommand, RichCommand
from cpcready.utils.console import ok, error, info2, blank_line
from rich.console import Console
console = Console()

@click.command(cls=RichCommand)
@click.argument("screen_mode", required=False, type=click.Choice(['0', '1', '2'], case_sensitive=False))
def mode(screen_mode):
    """
    Set or show the current CPC screen mode in CPCReady.

    This command allows you to set the CPC screen mode (0, 1, 2) for emulation and operations. The selected mode will affect how graphics and text are displayed in the emulator and some commands.

    Arguments:
        screen_mode : Mode to set (0, 1, 2). If omitted, shows the current mode.

    Examples:
        cpc mode 1      # Set CPC screen mode to 1
        cpc mode        # Show current CPC screen mode

    Notes:
        - Supported modes: 0 (high color, low resolution), 1 (medium color/resolution), 2 (low color, high resolution).
        - Changing the mode affects display and compatibility with some programs.
    """
    system_cpm = SystemCPM()
 

    if screen_mode:
        # Set new mode
        try:
            system_cpm.set_mode(screen_mode)
            blank_line(1)
            ok(f"CPC Screen Mode set to: {screen_mode}")
            blank_line(1)
        except Exception as e:
            error(f"Error setting mode: {e}")
    else:
        # Show current mode
        current_mode = system_cpm.get_mode()
        blank_line(1)
        info2(f"Current CPC Screen Mode: {current_mode}")
        blank_line(1)
