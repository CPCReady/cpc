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


import sys
from rich.console import Console
from rich.panel import Panel

# Crear consolas separadas para stdout y stderr
console = Console()
error_console = Console(stderr=True)

LEVELS = {"quiet": 0, "normal": 1, "verbose": 2, "debug": 3}
_current_level = LEVELS["normal"]

def set_level(level_name):
    global _current_level
    _current_level = LEVELS.get(level_name, 1)

def _should_show(required_level):
    return _current_level >= required_level

def info2(msg, level="normal"):
    if _should_show(LEVELS[level]):
        console.print(f"[cyan]◉[/cyan] {msg}")

def ok(msg, level="normal"):
    if _should_show(LEVELS[level]):
        console.print(f"[green]◉[/green] {msg}")

def warn(msg, level="normal"):
    if _should_show(LEVELS[level]):
        console.print(f"[yellow]◉[/yellow] {msg}")

def error(msg):
    # Usar la consola de error de Rich
    error_console.print(f"[red]◉[/red] {msg}")

def debug(msg):
    if _should_show(LEVELS["debug"]):
        console.print(f"[magenta][DEBUG][/magenta]  {msg}")

def banner(msg):
    console.print(Panel.fit(f"[bold green]▶ [/bold green][bold white]{msg}[/bold white]", border_style="white"))

def message(msg):
    if _should_show(LEVELS["normal"]):
        console.print(msg)

def blank_line(lines=1):
    for _ in range(lines):
        console.print("")