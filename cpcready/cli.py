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
from cpcready.drive import drive_group
from cpcready.disc import disc
from cpcready.save import save
from cpcready.era import era
from cpcready.list import list
from cpcready.filextr.filextr import filextr
from cpcready.cat.cat import cat
from cpcready.user.user import user
from cpcready.settings import settings
from cpcready.ren.ren import ren
from cpcready.model.model import model
from cpcready.mode.mode import mode
from cpcready.run import run
from cpcready.rvm.rvm import status as rvm_status, config as rvm_config
# from cpcready.header import header
from cpcready.configweb import configweb
from cpcready.utils.click_custom import CustomGroup, CustomCommand
from cpcready.utils.console import message, blank_line
from cpcready import __version__
from cpcready.utils.version import add_version_option_to_group, show_version_info

@add_version_option_to_group
@click.group(cls=CustomGroup, invoke_without_command=True, show_banner=True)
@click.pass_context
def cli(ctx):
    """Toolchain CLI for Amstrad CPC."""
    # Si no hay comando, mostrar ayuda
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@cli.command(cls=CustomCommand)
def version():
    """Show version information."""
    show_version_info()

# Crear grupo para comandos rvm
@cli.group(cls=CustomGroup, name='rvm')
def rvm_group():
    """RetroVirtualMachine emulator management."""
    pass

# Añadir comandos al grupo rvm
rvm_group.add_command(rvm_status, name='status')
rvm_group.add_command(rvm_config, name='config')

# Reemplazar el tipo de comando/grupo de los subcomandos para personalizar la ayuda
drive_group.type = CustomGroup
cli.add_command(drive_group)
cli.add_command(disc)
cli.add_command(cat)
cli.add_command(save)
cli.add_command(era)
cli.add_command(user)
cli.add_command(list)
cli.add_command(settings)
cli.add_command(configweb)
cli.add_command(ren)
cli.add_command(filextr)
cli.add_command(model)
cli.add_command(mode)
cli.add_command(run)
# cli.add_command(header)

if __name__ == "__main__":
    import sys
    import os
    
    # Detectar el nombre con el que fue invocado el script
    invoked_name = os.path.basename(sys.argv[0])
    
    # Mapeo de nombres de comando a funciones
    command_map = {
        'cpc': cli,
        'disc': disc,
        'drive': drive_group,
        'catcpc': cat,
        'A': lambda: drive_group(['A'] + sys.argv[1:]),
        'B': lambda: drive_group(['B'] + sys.argv[1:]),
        'user': user,
        'save': save,
        'era': era,
        'list': list,
        'model': model,
        'mode': mode,
    }
    
    # Si fue invocado con un alias, ejecutar el comando directamente
    if invoked_name in command_map:
        if invoked_name in ['A', 'B']:
            # Para A y B, necesitamos invocar drive_group con el subcomando
            command_map[invoked_name]()
        else:
            command_map[invoked_name]()
    else:
        # Por defecto, ejecutar el CLI principal
        cli()

