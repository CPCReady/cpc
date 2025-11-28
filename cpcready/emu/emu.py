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
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import questionary
from cpcready.utils.click_custom import CustomCommand
from cpcready.utils.console import info2, ok, warn, blank_line
from cpcready.utils.toml_config import ConfigManager


@click.command(cls=CustomCommand)
def emu():
    """Configure the emulator to use.
    
    Select between M4Board or RetroVirtualMachine as the default emulator.
    """
    blank_line(1)
    
    # Obtener configuración actual
    config = ConfigManager()
    current_emulator = config.get("emulator", "selected", "RetroVirtualMachine")
    
    # Mostrar emulador actual
    info2(f"Current emulator: {current_emulator}")
    blank_line(1)
    
    # Opciones disponibles
    emulators = [
        "RetroVirtualMachine",
        "M4Board"
    ]
    
    # Prompt para seleccionar emulador
    selected = questionary.select(
        "Select emulator to use:",
        choices=emulators,
        default=current_emulator if current_emulator in emulators else emulators[0]
    ).ask()
    
    # Si el usuario cancela (Ctrl+C o ESC)
    if selected is None:
        blank_line(1)
        warn("Configuration cancelled.")
        blank_line(1)
        return
    
    # Guardar selección
    config.set("emulator", "selected", selected)
    
    blank_line(1)
    ok(f"Emulator set to: {selected}")
    blank_line(1)
