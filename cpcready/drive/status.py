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
from cpcready.utils.console import info2, ok, debug, message,blank_line,banner
from pathlib import Path
from cpcready.utils.manager import DriveManager
from cpcready.utils.click_custom import CustomCommand
from cpcready.utils.version import add_version_option

@add_version_option
@click.command(cls=CustomCommand, show_banner=True)
def status():
    """Show the status of disc drives."""
    blank_line(1)
    # message("[DRIVE STATUS]\n")

    drive_manager = DriveManager()
    drive_manager.drive_table()