
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
