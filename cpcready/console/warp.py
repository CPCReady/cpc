"""
Warp-style Interactive Console using Textual
Permite ejecutar comandos CPC con selección de texto, scroll y diseño moderno
"""

import click
import subprocess
import os
import sys
from pathlib import Path
from collections import deque
from typing import Optional, List

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
from cpcready.utils.click_custom import CustomCommand, RichCommand, RichCommand


def file_exists(path: str) -> bool:
    """Devuelve True si el archivo existe, False si no."""
    return Path(path).is_file()


class StatusBar(Static):
    """Barra de estado superior con información de drives"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drive_a = "No disc inserted"
        self.drive_b = "No disc inserted"
        self.selected_drive = "A"

    def compose(self) -> ComposeResult:
        with Horizontal(id="status-content"):
            yield Label(id="status-left")
            yield Label(id="status-right")

    def on_mount(self) -> None:
        self.update_status()

    def update_drives(self, drive_a: str, drive_b: str, selected_drive: str = "A"):
        """Actualiza el estado de los drives"""
        self.drive_a = drive_a
        self.drive_b = drive_b
        self.selected_drive = selected_drive
        self.update_status()

    def update_status(self):
        """Renderiza la barra de estado"""

        left_text = Text()
        model = ConfigManager().get('system', 'model', '6128')
        left_text.append("CPCReady |", style="bold yellow")
        if model == '464':
            left_text.append(" AMSTRAD 64k COLOUR PERSONAL COMPUTER ", style="bright_white")
            right_text = Text()
            right_text.append("CPC464 🟥🟩🟦 COLOUR", style="bright_white")
        elif model == '664':
            left_text.append(" AMSTRAD 64k COLOUR PERSONAL COMPUTER ", style="bright_white")
            right_text = Text()
            right_text.append("CPC664 🟥🟩🟦 COLOUR", style="bright_white")
        else:
            left_text.append(" AMSTRAD 128K ORDENADOR PERSONAL ", style="bright_white")
            right_text = Text()
            right_text.append("🟥🟩🟦 ", style="bright_white")

        # Actualizar labels
        label_left = self.query_one("#status-left", Label)
        label_right = self.query_one("#status-right", Label)
        label_left.update(left_text)
        label_right.update(right_text)


class OutputLog(RichLog):
    """Log de salida con scroll automático"""

    def __init__(self, **kwargs):
        super().__init__(
            highlight=True,
            markup=True,
            auto_scroll=True,
            max_lines=10000,
            wrap=False,
            **kwargs
        )
        # Habilitar selección de texto

        self.can_focus = True


class PromptInput(Input):
    """Input para comandos con historial"""

    def __init__(self, **kwargs):
        super().__init__(placeholder="Type a command...", **kwargs)
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


class InfoModal(ModalScreen):
    """Modal simple con borde para mostrar información."""
    DEFAULT_CSS = """
    InfoModal {
        align: center middle;
    }
    #info-modal-container {
        width: 60;
        height: 20;
        background: #111111;
        border: round cyan;
        padding: 2 4;
    }
    #info-modal-content {
        color: white;
        content-align: center middle;
        padding: 1 0;
    }
    #info-modal-buttons {
        width: 100%;
        align: center middle;
        margin-top: 1;
    }
    Button {
        min-width: 12;
        margin: 0 1;
        border: round;
    }
    """
    def __init__(self, message: str, title: str = "Información"):
        super().__init__()
        self.message = message
        self.title_text = title

    def compose(self) -> ComposeResult:
        with Vertical(id="info-modal-container"):
            yield Label(self.title_text, id="info-modal-title")
            yield Label(self.message, id="info-modal-content")
            with Horizontal(id="info-modal-buttons"):
                yield Button("Cerrar", variant="primary", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()


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
        layout: horizontal;
    }
    
    #status-left {
        width: 1fr;
        height: 1;
        content-align: left middle;
    }
    
    #status-right {
        width: auto;
        height: 1;
        content-align: right middle;
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
    
    #prompt-container {
        height: auto;
        min-height: 5;
        background: #000000;
        border: round grey;
        padding: 0;
    }
    
    #path-bar {
        width: auto;
        height: auto;
        min-height: 1;
        background: #000000;
        border: round grey;
        padding: 0 1;
        margin: 0;
        color: #808080;
        text-style: dim;
    }
    
    #input-row {
        height: auto;
        min-height: 1;
        padding: 0 1;
    }
    
    #prompt-label {
        width: auto;
        height: auto;
        content-align: left middle;
        color: #4ec9b0;
        text-style: bold;
    }
    
    PromptInput {
        width: 1fr;
        height: auto;
        min-height: 1;
        background: #000000;
        border: none;
        color: #d4d4d4;
    }
    
    PromptInput:focus {
        border: none;
        background: #000000;
    }
    
    #main-container {
        width: 1fr;
        height: 1fr;
    }
    
    #left-panel {
        width: 3fr;
        height: 1fr;
    }
    
    #right-panel {
        width: 1fr;
        min-width: 0;
        height: 1fr;
    }
    
    .info-panel {
        background: #000000;
        border: round grey;
        padding: 1 2;
        margin: 0 0 0 1;
    }
    
    .info-panel.selected-drive {
        border: round green !important;
    }
    .info-panel.unselected-drive {
        border: round grey !important;
    }
    
    #drive-a-panel, #drive-b-panel {
        width: 100%;
        height: 9;
        min-width: 0;
    }
    #drive-a-title-panel, #drive-b-title-panel {
        width: 100%;
        border: round grey;
        layout: horizontal;
        content-align: center middle;
        padding: 0 1;
        height: 3;
    }
    
    .drive-letter-left {
        width: auto;
        color: #ffffff;
        background: red;
        text-style: bold;
        content-align: left middle;
    }
    
    .drive-letter-right {
        width: auto;
        color: #ffffff;
        background: red;
        text-style: bold;
        content-align: right middle;
    }
    
    .info-title {
        color: #000000;
        background: white;
        text-style: bold;
        content-align: center middle;
        width: 1fr;
    }
    
    .system-title {
        color: yellow;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #drive-a-status-row, #drive-b-status-row {
        width: 100%;
        layout: horizontal;
        height: auto;
        margin-top: 0;
    }
    
    #drive-a-status, #drive-b-status {
        width: 1fr;
    }
    
    .eject-button {
        width: 5;
        height: 2;
        border: round grey;
        background: #000000;
    }
    
    .info-content {
        color: #d4d4d4;
    }

    #system-panel {
        height: 1fr;
    }
    
    #footer-bar {
        height: 1;
        width: 100%;
        background: #000000;
        color: grey;
        content-align: center middle;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Salir", show=True),
        Binding("ctrl+l", "clear", "Limpiar", show=True),
        Binding("f1", "show_info", "Info", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.current_dir = Path.cwd()
        self.panels_visible = False  # Controla visibilidad del panel derecho
        self.cpc_commands = {
            'save', 
            'cat', 
            'disc', 
            'drive', 
            'run', 
            'version', 
            'rvm', 
            'emu',
            'm4', 
            'list', 
            'era', 
            'user', 
            'ren', 
            'model', 
            'mode', 
            'filextr',
            "--help",
            "a",
            "b",
            "A",
            "B"
        }

    def compose(self) -> ComposeResult:
        """Compone la interfaz de la consola"""
        with Vertical():
            yield StatusBar(id="status-bar")
            with Horizontal(id="main-container"):
                with Vertical(id="left-panel"):
                    with ScrollableContainer(id="output-container"):
                        yield OutputLog(id="output-log")
                    with Vertical(id="prompt-container"):
                        yield Label(id="path-bar")
                        with Horizontal(id="input-row"):
                            yield Label("❯", id="prompt-label")
                            yield PromptInput(id="prompt-input")
                with Vertical(id="right-panel"):
                    with Container(classes="info-panel", id="drive-a-panel"):
                        with Horizontal(id="drive-a-title-panel"):
                            yield Label(" ⬆ A ", classes="drive-letter-left", id="drive-a-letter-left")
                            yield Label("No disc inserted", classes="info-title", id="drive-a-name")
                            yield Label(" ⬇ A ", classes="drive-letter-right", id="drive-a-letter-right")
                        with Horizontal(id="drive-a-status-row"):
                            yield Label("○", classes="info-content", id="drive-a-status")
                            yield Label("", classes="eject-button", id="drive-a-eject")
                    with Container(classes="info-panel", id="drive-b-panel"):
                        with Horizontal(id="drive-b-title-panel"):
                            yield Label(" ⬆ B ", classes="drive-letter-left", id="drive-b-letter-left")
                            yield Label("No disc inserted", classes="info-title", id="drive-b-name")
                            yield Label(" ⬇ B ", classes="drive-letter-right", id="drive-b-letter-right")
                        with Horizontal(id="drive-b-status-row"):
                            yield Label("○", classes="info-content", id="drive-b-status")
                            yield Label("", classes="eject-button", id="drive-b-eject")
                    with Container(classes="info-panel", id="system-panel"):
                        yield Label("System", classes="system-title")
                        yield Label("User: 0", classes="info-content", id="system-user")
                        yield Label("Mode: 1", classes="info-content", id="system-mode")
                        yield Label("RetroVirtualMachine", classes="info-content", id="emulator-info")
            yield Static("Ctrl+C - Exit  |  Ctrl+L - Clear Screen ", id="footer-bar")

    def on_mount(self) -> None:
        """Inicializa la consola al montarse"""
        self.title = "CPCReady Console"
        self.update_drive_status()
        self.update_path_bar()
        
        # Aplicar estado inicial de paneles (ocultos por defecto)
        right_panel = self.query_one("#right-panel")
        left_panel = self.query_one("#left-panel")
        right_panel.styles.display = "none"
        left_panel.styles.width = "1fr"

        # Mensaje de bienvenida simple (sin centrado manual)
        output = self.query_one("#output-log", OutputLog)

        output.write(Text("  ░██████  ░█████████    ░██████  ░█████████                               ░██            ", style="bright_yellow"))
        output.write(Text(" ░██   ░██ ░██     ░██  ░██   ░██ ░██     ░██                              ░██            ", style="bright_yellow"))
        output.write(Text("░██        ░██     ░██ ░██        ░██     ░██  ░███████   ░██████    ░████████ ░██    ░██ ", style="bright_yellow"))
        output.write(Text("░██        ░█████████  ░██        ░█████████  ░██    ░██       ░██  ░██    ░██ ░██    ░██ ", style="bright_yellow"))
        output.write(Text("░██        ░██         ░██        ░██   ░██   ░█████████  ░███████  ░██    ░██ ░██    ░██ ", style="bright_yellow"))
        output.write(Text(" ░██   ░██ ░██          ░██   ░██ ░██    ░██  ░██        ░██   ░██  ░██   ░███ ░██   ░███ ", style="bright_yellow"))
        output.write(Text("  ░██████  ░██           ░██████  ░██     ░██  ░███████   ░█████░██  ░█████░██  ░█████░██ ", style="bright_yellow"))
        output.write(Text("                                                                                      ░██ ", style="bright_yellow"))
        output.write(Text("                                                                                 ░███████  ", style="bright_yellow"))
        # output.write(Text("▞▀▖▛▀▖▞▀▖▛▀▖        ▌   ", style="bright_yellow"))
        # output.write(Text("▌  ▙▄▘▌  ▙▄▘▞▀▖▝▀▖▞▀▌▌ ▌", style="bright_yellow"))
        # output.write(Text("▌ ▖▌  ▌ ▖▌▚ ▛▀ ▞▀▌▌ ▌▚▄▌", style="bright_yellow"))
        # output.write(Text("▝▀ ▘  ▝▀ ▘ ▘▝▀▘▝▀▘▝▀▘▗▄▘", style="bright_yellow"))
        output.write(Text("Ready\n", style="bright_yellow"))
        # output.write(Text("Comandos disponibles:", style="bold yellow"))
        # output.write(Text("  • Comandos CPC: save, cat, disc, drive, run, version, etc.", style="dim"))
        # output.write(Text("  • Comandos sistema: cd, ls, pwd, clear, exit", style="dim"))
        # output.write(Text("  • help - Muestra ayuda", style="dim"))
        # output.write(Text("  • Ctrl+C - Salir  |  Ctrl+L - Limpiar pantalla", style="dim"))
        # output.write(Text("  • Para copiar: Option/Alt + seleccionar con ratón", style="dim cyan"))
        output.write("")

        # Focus en el input
        self.query_one("#prompt-input", PromptInput).focus()


    def update_drive_status(self):
        """Actualiza el estado de los drives en la barra de estado"""
        # Recargar configuración desde el archivo
        self.config_manager = ConfigManager()
        drive_config = self.config_manager.get_section('drive')
        system_config = self.config_manager.get_section('system')

        drive_a = drive_config.get('drive_a', '')
        drive_b = drive_config.get('drive_b', '')
        selected_drive = drive_config.get('selected_drive', 'A')
        if isinstance(selected_drive, str):
            selected_drive = selected_drive.upper()
        else:
            selected_drive = 'A'

        # Datos del sistema
        user = system_config.get('user', 0)
        model = system_config.get('model', '6128')
        mode = system_config.get('mode', 1)

        # Si está vacío, mostrar "No disc"
        drive_a_display = 'No disc inserted'
        if drive_a:
            drive_a_display = Path(drive_a).name
        drive_b_display = 'No disc inserted'
        if drive_b:
            drive_b_display = Path(drive_b).name

        # Actualizar barra de estado
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_drives(drive_a_display, drive_b_display, selected_drive)
        status_a = Text()
        status_b = Text()

        # Si está vacío, mostrar "No disc"
        if file_exists(drive_a):
            drive_a_display = Path(drive_a).name
            status_a.append(" 🟩", style="bright_green")
        else:
            drive_a_display = 'No disc inserted'
            status_a.append(" 🟥", style="dim")

        if file_exists(drive_b):
            drive_b_display = Path(drive_b).name
            status_b.append(" 🟩", style="bright_green")
        else:
            drive_b_display = 'No disc inserted'
            status_b.append(" 🟥", style="dim")

        # Actualizar paneles laterales - nombres de disco
        drive_a_name = self.query_one("#drive-a-name", Label)
        drive_b_name = self.query_one("#drive-b-name", Label)

        # Actualizar paneles laterales - indicadores de estado
        drive_a_status = self.query_one("#drive-a-status", Label)
        drive_b_status = self.query_one("#drive-b-status", Label)

        # Actualizar borde de los paneles según el drive seleccionado
        drive_a_panel = self.query_one("#drive-a-panel", Container)
        drive_b_panel = self.query_one("#drive-b-panel", Container)
        # Eliminar clases previas
        drive_a_panel.remove_class("selected-drive")
        drive_b_panel.remove_class("selected-drive")
        drive_a_panel.remove_class("unselected-drive")
        drive_b_panel.remove_class("unselected-drive")
        if selected_drive == "A":
            drive_a_panel.add_class("selected-drive")
            drive_b_panel.add_class("unselected-drive")
        elif selected_drive == "B":
            drive_b_panel.add_class("selected-drive")
            drive_a_panel.add_class("unselected-drive")
        else:
            drive_a_panel.add_class("unselected-drive")
            drive_b_panel.add_class("unselected-drive")
        # Forzar refresco visual
        drive_a_panel.refresh()
        drive_b_panel.refresh()

        # Actualizar nombre Drive A (siempre negro, el estado lo muestra el indicador)
        name_a = Text()
        name_a.append(drive_a_display, style="black")

        # Actualizar nombre Drive B (siempre negro, el estado lo muestra el indicador)
        name_b = Text()
        name_b.append(drive_b_display, style="black")

        drive_a_name.update(name_a)
        drive_b_name.update(name_b)
        drive_a_status.update(status_a)
        drive_b_status.update(status_b)

        # Actualizar información del sistema
        system_user = self.query_one("#system-user", Label)
        system_mode = self.query_one("#system-mode", Label)

        system_user.update(Text(f"User    : {user}", style="white"))
        system_mode.update(Text(f"Mode    : {mode}", style="white"))

        # Actualizar emulador
        emulator = self.config_manager.get("emulator", "selected", "RetroVirtualMachine")
        ip = self.config_manager.get("emulator", "m4board_ip")
        if emulator == "M4Board":
            emulator += f" ({ip})" if ip else " (no IP set)"
        emulator_info = self.query_one("#emulator-info", Label)
        emulator_info.update(Text(f"Emulator: {emulator}", style="white"))

        # Forzar refresh de los widgets
        drive_a_name.refresh()
        drive_b_name.refresh()
        drive_a_status.refresh()
        drive_b_status.refresh()
        system_user.refresh()
        system_mode.refresh()
        emulator_info.refresh()

    def update_path_bar(self):
        """Actualiza la barra con el path actual"""
        path_bar = self.query_one("#path-bar", Label)
        # Mostrar path relativo a home si es posible
        try:
            rel_path = self.current_dir.relative_to(Path.home())
            display_path = f"~/{rel_path}"
        except ValueError:
            display_path = str(self.current_dir)

        path_bar.update(f"▶︎ {display_path}")

    def action_quit(self) -> None:
        """Acción para salir de la consola"""
        self.exit()

    def action_clear(self) -> None:
        """Acción para limpiar la pantalla"""
        output = self.query_one("#output-log", OutputLog)
        output.clear()

    async def action_show_info(self) -> None:
        """Acción para mostrar la ventana modal de info al pulsar F1"""
        self.show_info_modal("Este es un mensaje de información de ejemplo.", "Info")

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
        cmd_text.append("❯ ", style="bold green")
        cmd_text.append(command, style="bold yellow")
        output.write(cmd_text)
        output.write("")  # Línea en blanco antes del resultado

        # Ejecutar comando
        await self.execute_command(command)

    async def execute_command(self, command: str):
        output = self.query_one("#output-log", OutputLog)

        # Comandos especiales
        if command in ['exit', 'quit']:
            self.exit()
            return

        if command == 'clear':
            output.clear()
            output.write(Text("Ready", style="bright_yellow"))
            return

        if command == 'help':
            self.show_help()
            output.write("")
            self.update_drive_status()
            output.write(Text("Ready", style="bright_yellow"))
            return

        if command == 'info':
            self.show_info_modal("Este es un mensaje de información de ejemplo.", "Info")
            return

        color_map = {
            '0': '#000000', '1': '#0000AA', '2': '#0000FF', '3': '#AA0000', '4': '#AA00AA', '5': '#AA00FF',
            '6': '#FF0000', '7': '#FF00AA', '8': '#FF00FF', '9': '#00AA00', '10': '#00AAAA', '11': '#00AAFF',
            '12': '#AAAA00', '13': '#AAAAAA', '14': '#AAAAFF', '15': '#FFAA00', '16': '#FFAAAA', '17': '#FFAAFF',
            '18': '#00FF00', '19': '#00FFAA', '20': '#00FFFF', '21': '#AAFF00', '22': '#AAFFAA', '23': '#AAFFFF',
            '24': '#FFFF00', '25': '#FFFFAA', '26': '#FFFFFF'
        }
        if command.startswith('paper'):
            parts = command.split()
            color_code = '#ffffff'  # Por defecto blanco
            if len(parts) > 1 and parts[1] in color_map:
                color_code = color_map[parts[1]]
            elif len(parts) > 1:
                output.write(Text(f"Color no válido. Usa un número entre 0 y 26.", style="bold red"))
                return
            output.clear()
            self.set_outputlog_paper(color_code)
            output.write(Text(f"\nReady", style="bright_yellow"))
            return
        if command.startswith('border'):
            parts = command.split()
            color_code = '#000000'  # Por defecto blanco
            if len(parts) > 1 and parts[1] in color_map:
                color_code = color_map[parts[1]]
            elif len(parts) > 1:
                output.write(Text(f"Color no válido. Usa un número entre 0 y 26.", style="bold red"))
                return
            self.set_outputcontainer_bg(color_code)
            output.write(Text(f"Ready\n", style="bright_yellow"))
            return

        if command == 'sysinfo':
            self.toggle_panels()
            status = "visibles" if self.panels_visible else "ocultos"
            # output.write(Text(f"Paneles laterales ahora {status}.", style="bold green"))
            output.write(Text(f"Ready\n", style="bright_yellow"))
            return

        # Comando cd
        if command.startswith('cd '):
            self.execute_cd(command[3:].strip())
            output.write("")
            self.update_drive_status()
            output.write(Text("Ready", style="bright_yellow"))
            return

        # Comandos del sistema (ls, pwd, etc.)
        parts = command.split()
        cmd_name = parts[0] if parts else ''

        # Comando emu requiere modal interactivo
        if cmd_name == 'emu':
            await self.execute_emu_command()
            output.write("")
            self.update_drive_status()
            return

        # Verificar si es comando CPC
        if cmd_name in self.cpc_commands:
            if cmd_name == 'a' or cmd_name == 'b' or cmd_name == 'A' or cmd_name == 'B':
                command = f"drive {cmd_name.upper()}"
            await self.execute_cpc_command(command)
            output.write("")
            # Actualizar paneles después de ejecutar el comando
            self.update_drive_status()
        else:
            # Ejecutar como comando del sistema
            await self.execute_system_command(command)
            output.write("")
            output.write(Text("Ready", style="bright_yellow"))
            self.update_drive_status()

    def execute_cd(self, path: str):
        """Ejecuta comando cd"""
        output = self.query_one("#output-log", OutputLog)

        try:
            if path == '~':
                new_dir = Path.home()
            elif path == '-':
                output.write(Text("cd: OLDPWD not set", style="bright_red"))
                return
            else:
                new_dir = (self.current_dir / path).resolve()

            if new_dir.exists() and new_dir.is_dir():
                os.chdir(new_dir)
                self.current_dir = new_dir
                self.update_path_bar()
                output.write(Text(f"📁 {self.current_dir}", style="green"))
            else:
                output.write(Text(f"no such file or directory: {path}", style="bright_red"))
        except Exception as e:
            output.write(Text(f"cd: {str(e)}", style="bright_red"))

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

            # Actualizar paneles después de cambiar el emulador
            self.update_drive_status()

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
        """Ejecuta un comando CPC usando subprocess"""
        output = self.query_one("#output-log", OutputLog)

        try:
            # Ejecutar usando cpc directamente
            full_command = f"cpc {command}"
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                env=os.environ.copy()
            )

            # Mostrar stderr primero (mensajes de estado, advertencias)
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        # Mostrar en rojo si contiene 'error', 'failed' o el returncode es distinto de 0
                        if (
                            'error' in line.lower() or
                            'failed' in line.lower() or
                            result.returncode != 0
                        ):  
                            output.write(Text("sadfafasdf", style="bright_red"))
                            output.write(Text(line, style="bright_red"))
                        else:
                            output.write(Text(line, style="cyan"))

            # Luego mostrar stdout (tabla, resultados)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        # Mostrar en rojo si el returncode es distinto de 0
                        if result.returncode != 0:
                            output.write(Text(line, style="bright_red"))
                        else:
                            output.write(Text(line, style="bright_yellow"))
                            
                
            # Mostrar código de salida si no es 0 y no hubo salida
            if result.returncode != 0 and not result.stderr and not result.stdout:
                output.write(Text(f"Syntax error", style="bright_red"))
            output.write(Text("\nReady", style="bright_yellow"))
        except Exception as e:
            output.write(Text(f"Syntax error", style="bright_red"))
            output.write(Text("\nReady", style="bright_yellow"))
            import traceback
            traceback.print_exc()

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
                        output.write(Text(line, style="bright_red"))

            # Luego mostrar stdout (tabla, resultados)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="white"))

            # Mostrar código de salida si no es 0
            if result.returncode != 0:
                # output.write(Text(f"2Command exited with code {result.returncode}", style="bold red"))
                output.write(Text(f"Syntax error", style="bright_red"))

            # Actualizar estado de drives si el comando pudo cambiarlos
            if command.split()[0] in ['drive', 'save']:
                self.update_drive_status()

        except Exception as e:
            output.write(Text(f"Error: {str(e)}", style="bright_red"))

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
                        output.write(Text(line, style="bright_yellow"))

            # Mostrar stderr
            if result.stderr or result.returncode != 0:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        output.write(Text(line, style="bright_red"))

                output.write(Text(f"Syntax error", style="bright_red"))
 
        except Exception as e:
            output.write(Text(f"Syntax error", style="bright_red"))


    def set_outputlog_paper(self, color="#000000"):
        """Cambia el fondo de OutputLog al color dado (modo 'paper')."""
        output = self.query_one("#output-log", OutputLog)
        output.styles.background = color
        # Ajustar color de texto para contraste básico
        if color.lower() in ["#000000", "#0000aa", "#0000ff", "#aa0000", "#aa00aa", "#aa00ff", "#ff0000", "#ff00aa", "#ff00ff", "#00aa00", "#00aaaa", "#00aaff", "#aaaa00", "#aaaaaa", "#aaaaff", "#ffaa00", "#ffaaaa", "#ffaaff", "#00ff00", "#00ffaa", "#00ffff", "#aaff00", "#aaffaa", "#aaffff", "#ffff00", "#ffffaa"]:
            output.styles.color = "#222222" if color.lower() != "#000000" else "#d4d4d4"
        else:
            output.styles.color = "#222222"
        output.refresh()

    def set_outputcontainer_bg(self, color="#ffffff"):
        """Cambia el fondo de output-container al color dado."""
        container = self.query_one("#output-container")
        container.styles.background = color
        if color == "#000000":
            container.styles.border = ("round", "grey")
        else:
            container.styles.border = ("round", color)
        container.refresh()

    def toggle_panels(self):
        """Alterna la visibilidad del panel derecho (drives y sistema)."""
        self.panels_visible = not self.panels_visible
        right_panel = self.query_one("#right-panel")
        left_panel = self.query_one("#left-panel")
        
        if self.panels_visible:
            # Mostrar panel derecho
            right_panel.styles.display = "block"
            right_panel.styles.width = "1fr"
            left_panel.styles.width = "3fr"
        else:
            # Ocultar panel derecho
            right_panel.styles.display = "none"
            left_panel.styles.width = "1fr"
        
    def show_help(self):
        """Muestra la ayuda de la consola"""
        output = self.query_one("#output-log", OutputLog)

        output.write(Text("Commands:", style="bold yellow"))
        output.write(Text("  cat         List files in the virtual disc.", style="bright_yellow"))
        output.write(
            Text("  configweb   Configure CPCReady options via web interface (Streamlit).", style="bright_yellow"))
        output.write(Text("  disc        Create or manage virtual discs.", style="bright_yellow"))
        output.write(Text("  drive       Manage disc drives.", style="bright_yellow"))
        output.write(Text("  emu         Configure the emulator to use.", style="bright_yellow"))
        output.write(Text("  era         Erase files from virtual disc.", style="bright_yellow"))
        output.write(Text("  filextr     Extract files from virtual disc to current directory.", style="bright_yellow"))
        output.write(Text("  list        List BASIC file from virtual disc.", style="bright_yellow"))
        output.write(Text("  mode        Set or show current CPC screen mode.", style="bright_yellow"))
        output.write(Text("  model       Set or show current CPC model.", style="bright_yellow"))
        output.write(Text("  ren         Rename file on virtual disc.", style="bright_yellow"))
        output.write(
            Text("  run         Run a file from the selected drive in RetroVirtualMachine.", style="bright_yellow"))
        output.write(Text("  rvm         RetroVirtualMachine emulator management.", style="bright_yellow"))
        output.write(Text("  save        Save file to virtual disc.", style="bright_yellow"))
        output.write(Text("  user        Set user number (0-15) for current session.", style="bright_yellow"))
        output.write(Text("  version     Show version information.", style="bright_yellow"))
        output.write(Text("  warp        Consola interactiva estilo Warp con Textual", style="bright_yellow"))
        output.write(Text("  webconsole  Web console interface for CPCReady.", style="bright_yellow"))
        output.write("")



    def show_info_modal(self, message: str, title: str = "Información"):
        """Muestra una ventana modal de información encima de la consola."""
        self.push_screen(InfoModal(message, title))


@click.command(cls=CustomCommand, name='warp')
def warpconsole():
    """Consola interactiva estilo Warp con Textual"""
    app = WarpConsole()
    app.run()


if __name__ == "__main__":
    warpconsole()

