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
from cpcready.drive.status import status
from cpcready.drive.A import A
from cpcready.drive.B import B
from cpcready.drive.eject import eject
from cpcready.utils.click_custom import CustomGroup
from cpcready.utils.version import add_version_option_to_group

@add_version_option_to_group
@click.group(cls=CustomGroup, help="Manage disc drives.", invoke_without_command=True, show_banner=True)
@click.pass_context
def drive_group(ctx):
    """Manage disc drives."""
    # Si no hay comando, mostrar ayuda
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

drive_group.add_command(status)
drive_group.add_command(A)
drive_group.add_command(B)
drive_group.add_command(eject)
