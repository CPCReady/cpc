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


import os
import click
from cpcready.utils.manager import SystemCPM
from cpcready.utils.click_custom import CustomCommand, RichCommand, RichCommand
from cpcready.utils.console import ok, error, blank_line
from cpcready.utils.toml_config import ConfigManager


@click.command(cls=RichCommand)
@click.argument("user_number", type=click.IntRange(0, 15), required=False)
def user(user_number):
    """
    Set user number (0-15) for current session.

    If no user_number is provided, displays the current user number.

    Examples:
        cpc user 0        # Set user to 0
        cpc user 7        # Set user to 7
        cpc user          # Show current user
    """
    system_cpm = SystemCPM()
    config = ConfigManager()
    
    # Si no se pasa argumento, mostrar el valor actual
    if user_number is None:
        current_user = system_cpm.get_user_number()
        blank_line(1)
        ok(f"Current user: {current_user}")
        blank_line(1)
        return
    
    # Guardar en TOML
    try:
        config.set("system", "user", int(user_number))
    except Exception as e:
        error(f"Failed to set user: {e}")
        return

    blank_line(1)
    ok(f"User set to {user_number}")
    blank_line(1)


