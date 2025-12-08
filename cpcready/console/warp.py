"""
Warp-style Interactive Console using Textual
Permite ejecutar comandos CPC con selección de texto, scroll y diseño moderno
"""

import click
import subprocess
import os
import sys
import shlex
from pathlib import Path
from collections import deque
from typing import Optional, List
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer, Grid
from textual.widgets import Static, Input, Label, RichLog, Button, OptionList
from textual.widgets.option_list import Option
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual import events
from rich.text import Text
from rich.style import Style

from cpcready.utils.toml_config import ConfigManager
from cpcready.utils.console import console as rich_console
from cpcready.utils.click_custom import CustomCommand

# Importar comandos CPC directamente (solo los que existen como comandos simples)
from cpcready.save.save import save as cmd_save
from cpcready.cat.cat import cat as cmd_cat
from cpcready.drive.drive import drive as cmd_drive
from cpcready.run.run import run as cmd_run
from cpcready.list.list import list as cmd_list
from cpcready.era.era import era as cmd_era
from cpcready.user.user import user as cmd_user
from cpcready.ren.ren import ren as cmd_ren
from cpcready.model.model import model as cmd_model
from cpcready.mode.mode import mode as cmd_mode
from cpcready.filextr.filextr import filextr as cmd_filextr
from cpcready.disc.disc import disc as cmd_disc
from cpcready.m4.m4 import m4 as cmd_m4


class StatusBar(Static):
    """Barra de estado superior con información de drives"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drive_a = "No disc"
        self.drive_b = "No disc"
    
    def compose(self) -> ComposeResult:
        yield Label(id="status-content")
    
    def on_mount(self) -> None:
        self.update_status()
    
    def update_drives(self, drive_a: str, drive_b: str):
        """Actualiza el estado de los drives"""
        self.drive_a = drive_a
        self.drive_b = drive_b
        self.update_status()
    
    def update_status(self):
        """Renderiza la barra de estado"""
        # Estados de drives con indicadores
        a_status = "●" if self.drive_a != "No disc" else "○"
        b_status = "●" if self.drive_b != "No disc" else "○"
        
        status_text = Text()
        status_text.append("  ", style="bold white")
        status_text.append(f"{a_status} Drive A: ", style="bold cyan")
        status_text.append(self.drive_a if self.drive_a != "No disc" else "disc missing", 
                          style="green" if self.drive_a != "No disc" else "red")
        status_text.append("  |  ", style="bold white")
        status_text.append(f"{b_status} Drive B: ", style="bold cyan")
        status_text.append(self.drive_b if self.drive_b != "No disc" else "disc missing",
                          style="green" if self.drive_b != "No disc" else "red")
        
        label = self.query_one("#status-content", Label)
        label.update(status_text)


class OutputLog(RichLog):
    """Log de salida con scroll automático y selección de texto"""
    
    def __init__(self, **kwargs):
        super().__init__(
            highlight=True,
            markup=True,
            auto_scroll=True,
            max_lines=10000,
            **kwargs
        )


class PromptInput(Input):
    """Input para comandos con historial"""
    
    def __init__(self, **kwargs):
        super().__init__(placeholder="Escribe un comando...", **kwargs)
        self.history = deque(maxlen=1000)
        self.history_index = -1
        self.temp_input = ""
    
    def add_to_history(self, command: str):
        """Añade comando al historial"""
        if command.strip() and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = -1
        self.temp_input = ""
    
    def on_key(self, event: events.Key) -> None:
        """Maneja navegación del historial con flechas"""
        if event.key == "up":
            event.prevent_default()
            if self.history:
                if self.history_index == -1:
                    self.temp_input = self.value
                    self.history_index = len(self.history) - 1
                elif self.history_index > 0:
                    self.history_index -= 1
                
                if 0 <= self.history_index < len(self.history):
                    self.value = self.history[self.history_index]
                    self.cursor_position = len(self.value)
        
        elif event.key == "down":
            event.prevent_default()
            if self.history and self.history_index != -1:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.value = self.history[self.history_index]
                else:
                    self.history_index = -1
                    self.value = self.temp_input
                self.cursor_position = len(self.value)


class SelectionModal(ModalScreen[str]):
    """Modal para seleccionar opciones (reemplaza questionary)"""
    
    DEFAULT_CSS = """
    SelectionModal {
        align: center middle;
    }
    
    #modal-container {
        width: 60;
        height: auto;
        background: #000000;
        border: round solid white;
        padding: 1 2;
    }
    
    #modal-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: cyan;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #modal-options {
        width: 100%;
        height: auto;
        max-height: 10;
        background: #000000;
        border: solid white;
        margin-bottom: 1;
    }
    
    #modal-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    Button {
        min-width: 12;
        margin: 0 1;
        border: round;
    }
    """
    
    def __init__(self, title: str, choices: List[str], default: Optional[str] = None):
        super().__init__()
        self.modal_title = title
        self.choices = choices
        self.default = default
    
    def compose(self) -> ComposeResult:
        with Vertical(id="modal-container"):
            yield Label(self.modal_title, id="modal-title")
            
            # Crear opciones
            options = [Option(choice, id=choice) for choice in self.choices]
            option_list = OptionList(*options, id="modal-options")
            
            # Seleccionar default si existe
            if self.default and self.default in self.choices:
                option_list.highlighted = self.choices.index(self.default)
            
            yield option_list
            
            with Horizontal(id="modal-buttons"):
                yield Button("Select", variant="primary", id="btn-select")
                yield Button("Cancel", variant="default", id="btn-cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-select":
            option_list = self.query_one("#modal-options", OptionList)
            if option_list.highlighted is not None:
                selected = self.choices[option_list.highlighted]
                self.dismiss(selected)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Permite seleccionar con Enter en la lista"""
        selected = event.option.id
        self.dismiss(selected)


class WarpConsole(App):
    """Consola interactiva estilo Warp con Textual"""
    
    CSS = """
    Screen {
        background: #000000;
    }
    
    #status-bar {
        height: 3;
        background: #000000;
        border: round grey;
        padding: 0 2;
    }
    
    #status-content {
        width: 100%;
        height: 1;
        content-align: left middle;
    }
    
    #output-container {
        height: 1fr;
        background: #000000;
        border: round grey;
        padding: 1 2;
    }
    
    OutputLog {
        background: #000000;
        color: #d4d4d4;
        border: none;
        scrollbar-background: #000000;
        scrollbar-color: white;
        scrollbar-size: 1 1;
    }
    
    #path-bar {
        height: 1;
        background: #000000;
        padding: 0 2;
        color: #4ec9b0;
    }
    
    #prompt-container {
        height: 3;
        background: #000000;
        border: round grey;
        padding: 0 2;
    }
    
    #prompt-label {
        width: auto;
        height: 1;
        content-align: left middle;
        color: #4ec9b0;
        text-style: bold;
    }
    
    PromptInput {
        width: 1fr;
        height: 1;
        background: #000000;
        border: none;
        color: #d4d4d4;
    }
    
    PromptInput:focus {
        border: none;
        background: #000000;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Salir", show=True),
        Binding("ctrl+l", "clear", "Limpiar", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.current_dir = Path.cwd()
        self.cpc_commands = {
            'save', 'cat', 'disc', 'drive', 'run', 'version', 'rvm', 'emu', 
            'm4', 'list', 'era', 'user', 'ren', 'model', 'mode', 'filextr'
        }
    
    def compose(self) -> ComposeResult:
        """Compone la interfaz de la consola"""
        with Vertical():
            yield StatusBar(id="status-bar")
            with ScrollableContainer(id="output-container"):
                yield OutputLog(id="output-log")
            yield Label(id="path-bar")
            with Horizontal(id="prompt-container"):
                yield Label("❯", id="prompt-label")
                yield PromptInput(id="prompt-input")
    
    def on_mount(self) -> None:
        """Inicializa la consola al montarse"""
        self.title = "CPC Console"
        self.update_drive_status()
        self.update_path_bar()
        
        # Mensaje de bienvenida
        output = self.query_one("#output-log", OutputLog)
        output.write(Text("╭─────────────────────────────────────────╮", style="bold cyan"))
        output.write(Text("│   CPC Console - Interactive Terminal   │", style="bold cyan"))
        output.write(Text("╰─────────────────────────────────────────╯", style="bold cyan"))
        output.write("")
        output.write(Text("Comandos disponibles:", style="bold yellow"))
        output.write(Text("  • Comandos CPC: save, cat, disc, drive, run, version, etc.", style="dim"))
        output.write(Text("  • Comandos sistema: cd, ls, pwd, clear, exit", style="dim"))
        output.write(Text("  • help - Muestra ayuda", style="dim"))
        output.write(Text("  • Ctrl+C - Salir  |  Ctrl+L - Limpiar pantalla", style="dim"))
        output.write("")
        
        # Focus en el input
        self.query_one("#prompt-input", PromptInput).focus()
    
    def update_drive_status(self):
        """Actualiza el estado de los drives en la barra de estado"""
        drive_config = self.config_manager.get_section('drive')
        
        drive_a = drive_config.get('drive_a', '')
        drive_b = drive_config.get('drive_b', '')
        
        # Si está vacío, mostrar "No disc"
        if not drive_a:
            drive_a = 'No disc'
        else:
            # Extraer solo el nombre del archivo si es una ruta
            drive_a = Path(drive_a).name
        
        if not drive_b:
            drive_b = 'No disc'
        else:
            drive_b = Path(drive_b).name
        
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_drives(drive_a, drive_b)
    
    def update_path_bar(self):
        """Actualiza la barra con el path actual"""
        path_bar = self.query_one("#path-bar", Label)
        # Mostrar path relativo a home si es posible
        try:
            rel_path = self.current_dir.relative_to(Path.home())
            display_path = f"~/{rel_path}"
        except ValueError:
            display_path = str(self.current_dir)
        
        path_bar.update(f"📁 {display_path}")
    
    def action_quit(self) -> None:
        """Acción para salir de la consola"""
        self.exit()
    
    def action_clear(self) -> None:
        """Acción para limpiar la pantalla"""
        output = self.query_one("#output-log", OutputLog)
        output.clear()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Maneja el evento de envío de comando"""
        prompt_input = self.query_one("#prompt-input", PromptInput)
        command = event.value.strip()
        
        if not command:
            return
        
        # Añadir al historial
        prompt_input.add_to_history(command)
        
        # Limpiar input
        prompt_input.value = ""
        
        # Mostrar comando en el output
        output = self.query_one("#output-log", OutputLog)
        cmd_text = Text()
        cmd_text.append("❯ ", style="bold cyan")
        cmd_text.append(command, style="bold white")
        output.write(cmd_text)
        output.write("")  # Línea en blanco antes del resultado
        
        # Ejecutar comando
        await self.execute_command(command)
    
    async def execute_command(self, command: str):
        """Ejecuta un comando y muestra el resultado"""
        output = self.query_one("#output-log", OutputLog)
        
        # Comandos especiales
        if command in ['exit', 'quit']:
            self.exit()
            return
        
        if command == 'clear':
            output.clear()
            return
        
        if command == 'help':
            self.show_help()
            return
        
        # Comando cd
        if command.startswith('cd '):
            self.execute_cd(command[3:].strip())
            return
        
        # Comandos del sistema (ls, pwd, etc.)
        parts = command.split()
        cmd_name = parts[0] if parts else ''
        
        # Comando emu requiere modal interactivo
        if cmd_name == 'emu':
            await self.execute_emu_command()
            return
        
        # Verificar si es comando CPC
        if cmd_name in self.cpc_commands:
            await self.execute_cpc_command(command)
        else:
            # Ejecutar como comando del sistema
            await self.execute_system_command(command)
    
    def execute_cd(self, path: str):
        """Ejecuta comando cd"""
        output = self.query_one("#output-log", OutputLog)
        
        try:
            if path == '~':
                new_dir = Path.home()
            elif path == '-':
                output.write(Text("cd: OLDPWD not set", style="bold red"))
                return
            else:
                new_dir = (self.current_dir / path).resolve()
            
            if new_dir.exists() and new_dir.is_dir():
                os.chdir(new_dir)
                self.current_dir = new_dir
                self.update_path_bar()  # Actualizar barra de path
                output.write(Text(f"📁 {self.current_dir}", style="green"))
            else:
                output.write(Text(f"cd: no such file or directory: {path}", style="bold red"))
        except Exception as e:
            output.write(Text(f"cd: {str(e)}", style="bold red"))
    
    async def execute_emu_command(self):
        """Ejecuta comando emu con modal interactivo"""
        output = self.query_one("#output-log", OutputLog)
        
        # Obtener emulador actual
        current_emulator = self.config_manager.get("emulator", "selected", "RetroVirtualMachine")
        
        # Mostrar emulador actual
        output.write(Text(f"Current emulator: {current_emulator}", style="cyan"))
        output.write("")
        
        # Opciones disponibles
        emulators = ["RetroVirtualMachine", "M4Board"]
        
        # Crear y mostrar modal
        def handle_selection(selected: Optional[str]) -> None:
            """Callback cuando se selecciona una opción"""
            output = self.query_one("#output-log", OutputLog)
            
            # Si el usuario cancela
            if selected is None:
                output.write(Text("Configuration cancelled.", style="bold yellow"))
                output.write("")
                return
            
            # Guardar selección
            self.config_manager.set("emulator", "selected", selected)
            
            output.write(Text(f"✓ Emulator set to: {selected}", style="bold green"))
            output.write("")
        
        # Mostrar modal con callback
        self.push_screen(
            SelectionModal(
                title="Select emulator to use:",
                choices=emulators,
                default=current_emulator if current_emulator in emulators else emulators[0]
            ),
            callback=handle_selection
        )
    
    async def execute_cpc_command(self, command: str):
        """Ejecuta un comando CPC llamando directamente a las funciones"""
        output = self.query_one("#output-log", OutputLog)
        
        try:
            # Parsear comando y argumentos usando shlex para respetar comillas
            parts = shlex.split(command)
            cmd_name = parts[0] if parts else ''
            args = parts[1:] if len(parts) > 1 else []
            
            # Mapeo de comandos a funciones
            cmd_map = {
                'save': cmd_save,
                'cat': cmd_cat,
                'drive': cmd_drive,
                'run': cmd_run,
                'list': cmd_list,
                'era': cmd_era,
                'user': cmd_user,
                'ren': cmd_ren,
                'model': cmd_model,
                'mode': cmd_mode,
                'filextr': cmd_filextr,
                'disc': cmd_disc,
                'm4': cmd_m4,
            }
            
            # Si el comando no está en el mapa, usar subprocess como fallback
            # (para comandos como version, rvm, etc.)
            if cmd_name not in cmd_map:
                # Fallback a subprocess para comandos no mapeados
                await self._execute_via_subprocess(command)
                return
            
            # Capturar stdout y stderr
            stdout_buffer = StringIO()
            stderr_buffer = StringIO()
            
            try:
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    # Crear contexto de click y ejecutar comando
                    ctx = click.Context(cmd_map[cmd_name])
                    ctx.obj = {}
                    
                    # Invocar comando con argumentos
                    cmd_map[cmd_name](args, standalone_mode=False)
                    
            except SystemExit:
                # Click lanza SystemExit, lo capturamos
                pass
            except Exception as e:
                output.write(Text(f"Error executing command: {str(e)}", style="bold red"))
                return
            
            # Obtener salidas
            stderr_output = stderr_buffer.getvalue()
            stdout_output = stdout_buffer.getvalue()
            
            # Mostrar stderr primero (mensajes de estado, advertencias)
            if stderr_output.strip():
                for line in stderr_output.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="bold red"))
            
            # Luego mostrar stdout (tabla, resultados)
            if stdout_output.strip():
                for line in stdout_output.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="white"))
            
            # Actualizar estado de drives si el comando pudo cambiarlos
            if cmd_name in ['drive', 'save']:
                self.update_drive_status()
        
        except Exception as e:
            output.write(Text(f"Error: {str(e)}", style="bold red"))
    
    async def _execute_via_subprocess(self, command: str):
        """Ejecuta un comando CPC usando subprocess como fallback"""
        output = self.query_one("#output-log", OutputLog)
        
        try:
            # Ejecutar usando poetry run cpc
            full_command = f"poetry run cpc {command}"
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_dir
            )
            
            # Mostrar stderr primero (mensajes de estado, advertencias)
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="bold red"))
            
            # Luego mostrar stdout (tabla, resultados)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="white"))
            
            # Mostrar código de salida si no es 0
            if result.returncode != 0:
                output.write(Text(f"⚠ Command exited with code {result.returncode}", style="bold yellow"))
            
            # Actualizar estado de drives si el comando pudo cambiarlos
            if command.split()[0] in ['drive', 'save']:
                self.update_drive_status()
        
        except Exception as e:
            output.write(Text(f"Error: {str(e)}", style="bold red"))
    
    async def execute_system_command(self, command: str):
        """Ejecuta un comando del sistema"""
        output = self.query_one("#output-log", OutputLog)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_dir
            )
            
            # Mostrar stdout
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="white"))
            
            # Mostrar stderr
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="bold red"))
            
            # Mostrar código de salida si no es 0
            if result.returncode != 0:
                output.write(Text(f"⚠ Command exited with code {result.returncode}", style="bold yellow"))
        
        except Exception as e:
            output.write(Text(f"Error: {str(e)}", style="bold red"))
    
    def show_help(self):
        """Muestra la ayuda de la consola"""
        output = self.query_one("#output-log", OutputLog)
        
        output.write(Text("═══════════════════════════════════════", style="bold cyan"))
        output.write(Text("  CPC Console - Ayuda", style="bold cyan"))
        output.write(Text("═══════════════════════════════════════", style="bold cyan"))
        output.write("")
        output.write(Text("Comandos CPC:", style="bold yellow"))
        output.write(Text("  save <file.dsk>    - Guarda estado actual en disco", style="dim"))
        output.write(Text("  cat                - Muestra tabla de drives", style="dim"))
        output.write(Text("  disc <file.dsk>    - Lista contenido del disco", style="dim"))
        output.write(Text("  drive A/B <file>   - Monta disco en drive", style="dim"))
        output.write(Text("  run <file.dsk>     - Ejecuta disco en emulador", style="dim"))
        output.write(Text("  version            - Muestra versión de CPC", style="dim"))
        output.write("")
        output.write(Text("Comandos del Sistema:", style="bold yellow"))
        output.write(Text("  cd <dir>           - Cambia directorio", style="dim"))
        output.write(Text("  ls, pwd, etc.      - Comandos Unix estándar", style="dim"))
        output.write("")
        output.write(Text("Atajos de Teclado:", style="bold yellow"))
        output.write(Text("  Ctrl+C             - Salir de la consola", style="dim"))
        output.write(Text("  Ctrl+L             - Limpiar pantalla", style="dim"))
        output.write(Text("  ↑/↓                - Navegar historial", style="dim"))
        output.write(Text("  Mouse              - Seleccionar texto para copiar", style="dim"))
        output.write("")


@click.command(cls=CustomCommand, name='warp')
def warpconsole():
    """Consola interactiva estilo Warp con Textual"""
    app = WarpConsole()
    app.run()


if __name__ == "__main__":
    warpconsole()
