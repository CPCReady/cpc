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
