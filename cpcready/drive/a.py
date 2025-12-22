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
from cpcready.utils.console import error, warn, blank_line
from cpcready.utils.manager import DriveManager, cassetteManager
from cpcready.utils.click_custom import CustomCommand, RichCommand
from cpcready.utils.version import add_version_option
from cpcready.utils.update import show_update_notification
from rich.console import Console
console = Console()

@add_version_option
@click.command(cls=RichCommand, show_banner=False)
@click.argument('action', type=click.Choice(['a'], case_sensitive=False), required=False)
def a(action):
    """
    Select drive A as the active drive in CPCReady.

    This command sets drive A as the current active drive for all subsequent operations (save, list, run, etc.).

    Arguments:
        action : Optional, must be 'a' (default behavior).

    Examples:
        cpc a         # Select drive A as active

    Notes:
        - Once drive A is selected, all commands that operate on disks will use drive A by default unless -B is specified.
        - The drive table will be shown after selection.
        - Useful for switching between drive A and B quickly.
    """
    show_update_notification()
    drive_manager = DriveManager()
    
    blank_line(1)
    drive_manager.select_drive("a")
    blank_line(1)
    drive_manager.drive_table()

    
