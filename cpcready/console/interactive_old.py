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

"""
CPCReady Interactive Console with fixed layout and scrollable output
"""

import click
import subprocess
import shlex
import os
import sys
from pathlib import Path
from typing import List, Tuple
from collections import deque
from datetime import datetime
from threading import Thread, Event
import time

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.columns import Columns
from rich.markup import escape

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout

from cpcready.utils.toml_config import ConfigManager
from cpcready.utils.click_custom import CustomCommand


class OutputBuffer:
    """Buffer for command output with scrolling"""
    
    def __init__(self, max_lines: int = 1000):
        self.lines: deque = deque(maxlen=max_lines)
        self.max_lines = max_lines
    
    def add(self, text: str, style: str = ""):
        """Add text to buffer (text is NOT escaped, use markup safely)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        for line in text.split('\n'):
            if line or text.endswith('\n'):  # Preserve empty lines if text ends with newline
                self.lines.append((timestamp, line, style))
    
    def clear(self):
        """Clear buffer"""
        self.lines.clear()
    
    def get_renderable(self, height: int = 20):
        """Get renderable output (last N lines)"""
        lines_to_show = list(self.lines)[-height:]
        
        if not lines_to_show:
            return Panel(
                Align.center("[dim]No output yet. Type 'help' for assistance.[/dim]", vertical="middle"),
                title="[bold cyan]Output[/bold cyan]",
                border_style="cyan",
                height=height + 2
            )
        
        output_lines = []
        for timestamp, line, style in lines_to_show:
            if style:
                # If style is provided, it means line may contain markup already
                # Just prepend timestamp without escaping
                output_lines.append(f"[dim]{timestamp}[/dim] [{style}]{line}[/{style}]")
            else:
                # No style, line may or may not have markup
                output_lines.append(f"[dim]{timestamp}[/dim] {line}")
        
        content = "\n".join(output_lines)
        
        return Panel(
            content,
            title=f"[bold cyan]Output[/bold cyan] [dim]({len(self.lines)} lines)[/dim]",
            border_style="cyan",
            height=height + 2
        )


class StatusBar:
    """Status bar with system information"""
    
    @staticmethod
    def get_renderable():
        """Get status bar renderable"""
        config = ConfigManager()
        
        # Model info
        try:
            model = config.get("system", "model", "464")
            kb_map = {"464": "64K", "664": "64K", "6128": "128K"}
            kb = kb_map.get(model, "N/A")
            model_text = f"[bold][red]●[/red][green]●[/green][blue]●[/blue][/bold] CPC {model} {kb}"
        except:
            model_text = "[bold][red]●[/red][green]●[/green][blue]●[/blue][/bold] CPC N/A"
        
        # Drive A
        try:
            drive_select = config.get("drive", "selected_drive", "a").upper()
            drive_a_path = config.get("drive", "drive_a", "")
            disk_a_path = Path(drive_a_path)
            disk_a_name = disk_a_path.name if disk_a_path.exists() else "Empty"
            icon_a = '●' if drive_select == "A" else '○'
            status_a = '✓' if disk_a_path.exists() else '○'
            drive_a_text = f"A:{icon_a} {status_a} {disk_a_name}"
        except:
            drive_a_text = "A: N/A"
        
        # Drive B
        try:
            drive_select = config.get("drive", "selected_drive", "a").upper()
            drive_b_path = config.get("drive", "drive_b", "")
            disk_b_path = Path(drive_b_path)
            disk_b_name = disk_b_path.name if disk_b_path.exists() else "Empty"
            icon_b = '●' if drive_select == "B" else '○'
            status_b = '✓' if disk_b_path.exists() else '○'
            drive_b_text = f"B:{icon_b} {status_b} {disk_b_name}"
        except:
            drive_b_text = "B: N/A"
        
        # Emulator
        try:
            emulator = config.get("emulator", "selected", "N/A")
            if emulator == "RetroVirtualMachine":
                emu_text = "EMU: RVM"
            elif emulator == "M4Board":
                m4_ip = config.get("m4board", "ip", "N/A")
                emu_text = f"EMU: M4 ({m4_ip})"
            else:
                emu_text = f"EMU: {emulator}"
        except:
            emu_text = "EMU: N/A"
        
        # Video mode
        try:
            video_mode = config.get("system", "mode", 2)
            mode_text = f"Mode: {video_mode}"
        except:
            mode_text = "Mode: N/A"
        
        # Create table for status
        table = Table.grid(padding=(0, 2))
        table.add_column(justify="left")
        table.add_column(justify="left")
        table.add_column(justify="left")
        table.add_column(justify="left")
        table.add_column(justify="left")
        
        table.add_row(model_text, drive_a_text, drive_b_text, emu_text, mode_text)
        
        return Panel(
            table,
            border_style="yellow",
            height=3
        )


class CommandParser:
    """Parse and execute commands"""
    
    CPC_COMMANDS = [
        "save", "cat", "disc", "drive", "run", "version",
        "rvm", "emu", "m4", "list", "era", "user", "ren", 
        "model", "mode", "filextr"
    ]
    
    @staticmethod
    def parse(command_line: str) -> Tuple[str, list]:
        """Parse command line"""
        if not command_line.strip():
            return ('empty', [])
        
        parts = shlex.split(command_line)
        if not parts:
            return ('empty', [])
        
        cmd = parts[0]
        
        if cmd in ('exit', 'quit', 'q'):
            return ('exit', [])
        
        if cmd in ('help', '?'):
            return ('help', parts[1:])
        
        if cmd == 'clear':
            return ('clear', [])
        
        if cmd in CommandParser.CPC_COMMANDS:
            return ('cpc', parts)
        
        return ('system', parts)
    
    @staticmethod
    def execute_cpc(args: list, output_buffer: OutputBuffer) -> int:
        """Execute CPC command"""
        try:
            # Execute using Click context
            from cpcready.cli import cli
            from click.testing import CliRunner
            
            runner = CliRunner(mix_stderr=False)
            result = runner.invoke(cli, args)
            
            if result.output:
                # Escape output to prevent markup interpretation
                from rich.markup import escape
                output_buffer.add(escape(result.output))
            
            if result.exception and not isinstance(result.exception, SystemExit):
                from rich.markup import escape
                output_buffer.add(f"Error: {escape(str(result.exception))}", "red")
                return 1
            
            return result.exit_code
            
        except Exception as e:
            from rich.markup import escape
            output_buffer.add(f"Error executing CPC command: {escape(str(e))}", "red")
            return 1
    
    @staticmethod
    def execute_cd(args: list, output_buffer: OutputBuffer) -> int:
        """Execute cd command"""
        try:
            if len(args) == 1:
                os.chdir(os.path.expanduser("~"))
                output_buffer.add(f"Changed to: {os.getcwd()}", "green")
            else:
                target = os.path.expanduser(args[1])
                os.chdir(target)
                output_buffer.add(f"Changed to: {os.getcwd()}", "green")
            return 0
        except FileNotFoundError:
            from rich.markup import escape
            path = args[1] if len(args) > 1 else '~'
            output_buffer.add(f"cd: no such file or directory: {escape(path)}", "red")
            return 1
        except Exception as e:
            from rich.markup import escape
            output_buffer.add(f"cd: {escape(str(e))}", "red")
            return 1
    
    @staticmethod
    def execute_system(args: list, output_buffer: OutputBuffer) -> int:
        """Execute system command"""
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True
            )
            
            from rich.markup import escape
            
            if result.stdout:
                output_buffer.add(escape(result.stdout.rstrip()))
            
            if result.stderr:
                output_buffer.add(escape(result.stderr.rstrip()), "yellow")
            
            return result.returncode
            
        except FileNotFoundError:
            from rich.markup import escape
            output_buffer.add(f"Command not found: {escape(args[0])}", "red")
            return 127
        except Exception as e:
            from rich.markup import escape
            output_buffer.add(f"Error: {escape(str(e))}", "red")
            return 1
    
    @staticmethod
    def show_help(output_buffer: OutputBuffer):
        """Show help"""
        help_text = """[bold cyan]CPCReady Interactive Console Help[/bold cyan]

[bold yellow]CPC Commands:[/bold yellow]
  save, cat, disc, drive, run, version, rvm, emu, m4
  list, era, user, ren, model, mode, filextr

[bold yellow]System Commands:[/bold yellow]
  cd <dir>  - Change directory
  <cmd>     - Execute any system command

[bold yellow]Console Commands:[/bold yellow]
  help      - Show this help
  clear     - Clear output buffer
  exit/quit - Exit console
"""
        output_buffer.add(help_text)


def get_all_completions() -> list:
    """Get all completions"""
    return (
        CommandParser.CPC_COMMANDS +
        ['exit', 'quit', 'q', 'help', 'clear', 'cd', 'ls', 'pwd', 
         'cat', 'grep', 'find', 'echo', 'mkdir', 'rm', 'cp', 'mv']
    )


@click.command(cls=CustomCommand)
def interactive():
    """
    Interactive console with Warp-style layout
    
    The console has a fixed layout:
    - Top: Scrollable output area (command history and results)
    - Bottom: Fixed prompt panel (always visible)
    """
    console = Console()
    output_buffer = OutputBuffer(max_lines=1000)
    parser = CommandParser()
    
    # Welcome message
    output_buffer.add("[bold cyan]Welcome to CPCReady Interactive Console![/bold cyan]")
    output_buffer.add("[dim]Type 'help' for assistance, 'exit' to quit[/dim]")
    output_buffer.add("")
    
    # Word completer
    completer = WordCompleter(
        get_all_completions(),
        ignore_case=True,
    )
    
    # History
    history_path = os.path.expanduser("~/.config/cpcready/interactive_history.txt")
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    
    session = PromptSession(
        completer=completer,
        complete_while_typing=True,
        history=FileHistory(history_path),
    )
    
    running = True
    
    def create_layout():
        """Create the layout with output and prompt"""
        # Get current directory
        current_dir = os.getcwd()
        home = os.path.expanduser("~")
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]
        
        # Calculate heights
        terminal_height = console.size.height
        output_height = max(10, terminal_height - 7)
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(output_buffer.get_renderable(height=output_height), name="output"),
            Layout(Panel(
                Text(f"CPCReady {current_dir} $", style="bold cyan"),
                title="[bold yellow]Command[/bold yellow]",
                border_style="cyan",
            ), name="prompt", size=4),
        )
        
        return layout
    
    try:
        with Live(create_layout(), console=console, refresh_per_second=4) as live:
            while running:
                # Update layout before prompt
                live.update(create_layout())
                
                # Get current directory for prompt
                current_dir = os.getcwd()
                home = os.path.expanduser("~")
                if current_dir.startswith(home):
                    current_dir = "~" + current_dir[len(home):]
                
                # Prompt
                try:
                    # Stop live to allow input
                    live.stop()
                    
                    prompt_html = f'<b><style fg="yellow">$</style> </b>'
                    command_line = session.prompt(HTML(prompt_html))
                    
                    # Restart live
                    live.start()
                    
                    # Add command to output
                    output_buffer.add(f"[bold white]$ {escape(command_line)}[/bold white]")
                    
                    # Parse and execute
                    cmd_type, args = parser.parse(command_line)
                    
                    if cmd_type == 'empty':
                        live.update(create_layout())
                        continue
                    
                    elif cmd_type == 'exit':
                        output_buffer.add("\n[bold green]Goodbye! 👋[/bold green]")
                        live.update(create_layout())
                        running = False
                    
                    elif cmd_type == 'help':
                        parser.show_help(output_buffer)
                        live.update(create_layout())
                    
                    elif cmd_type == 'clear':
                        output_buffer.clear()
                        output_buffer.add("[dim]Output cleared[/dim]")
                        live.update(create_layout())
                    
                    elif cmd_type == 'cpc':
                        parser.execute_cpc(args, output_buffer)
                        live.update(create_layout())
                    
                    elif cmd_type == 'system':
                        if args and args[0] == 'cd':
                            parser.execute_cd(args, output_buffer)
                        else:
                            parser.execute_system(args, output_buffer)
                        live.update(create_layout())
                    
                except KeyboardInterrupt:
                    live.start()
                    output_buffer.add("\n[yellow](Use 'exit' to quit)[/yellow]")
                    live.update(create_layout())
                    continue
                
                except EOFError:
                    live.start()
                    output_buffer.add("\n[bold green]Goodbye! 👋[/bold green]")
                    live.update(create_layout())
                    running = False
    
    except Exception as e:
        import traceback
        console.clear()
        error_msg = f"Fatal error: {escape(str(e))}"
        console.print(f"[bold red]{error_msg}[/bold red]")
        console.print("\n[dim]Traceback:[/dim]")
        tb = escape(traceback.format_exc())
        console.print(tb)
        return


if __name__ == "__main__":
    interactive()
