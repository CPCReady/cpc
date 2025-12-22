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

@click.command(cls=RichCommand)
@click.argument("model_type", required=False, type=click.Choice(['464', '664', '6128'], case_sensitive=False))
def model(model_type):
    """
    Set or show the current CPC model used in CPCReady.

    This command allows you to set the CPC model (464, 664, 6128) for emulation and operations. The selected model will be used by other commands, such as run, when launching the emulator.

    Arguments:
        model_type : Model to set (464, 664, 6128). If omitted, shows the current model.

    Examples:
        cpc model 6128      # Set CPC model to 6128
        cpc model           # Show current CPC model

    Notes:
        - The defined model here is used by the run command to select the CPC type in the emulator.
        - Changing the model affects emulation and compatibility with some disk/tape images.
    """
    system_cpm = SystemCPM()
    
    if model_type:
        # Set new model
        try:
            system_cpm.set_model(model_type)
            blank_line(1)
            ok(f"CPC Model set to: {model_type}")
            blank_line(1)
        except Exception as e:
            error(f"Error setting model: {e}")
    else:
        # Show current model
        current_model = system_cpm.get_model()
        blank_line(1)
        info2(f"Current CPC Model: {current_model}")
        blank_line(1)
