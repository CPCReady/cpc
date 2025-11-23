import curses
import os
import sys
from pathlib import Path
from datetime import datetime

# Añadir el path del proyecto para importar ConfigManager
sys.path.insert(0, str(Path(__file__).parent.parent))
from cpcready.utils.toml_config import ConfigManager

# ---------------------- Funciones auxiliares ----------------------

def load_config():
    """Carga la configuración desde TOML."""
    config_manager = ConfigManager()
    toml_config = config_manager.get_all()
    
    # Convertir a estructura de menú BIOS
    return {
        "Drive": {
            "Drive A": toml_config.get("drive", {}).get("drive_a", ""),
            "Drive B": toml_config.get("drive", {}).get("drive_b", ""),
            "Selected Drive": toml_config.get("drive", {}).get("selected_drive", "A")
        },
        "Emulator": {
            "Default Emulator": toml_config.get("emulator", {}).get("default", "RetroVirtualMachine"),
            "RVM Path": toml_config.get("emulator", {}).get("retro_virtual_machine_path", ""),
            "M4Board IP": toml_config.get("emulator", {}).get("m4board_ip", "")
        }
    }

def save_config(config):
    """Guarda la configuración en TOML."""
    config_manager = ConfigManager()
    
    # Convertir estructura de menú BIOS a TOML
    config_manager.set("drive", "drive_a", config["Drive"]["Drive A"])
    config_manager.set("drive", "drive_b", config["Drive"]["Drive B"])
    config_manager.set("drive", "selected_drive", config["Drive"]["Selected Drive"])
    
    config_manager.set("emulator", "default", config["Emulator"]["Default Emulator"])
    config_manager.set("emulator", "retro_virtual_machine_path", config["Emulator"]["RVM Path"])
    config_manager.set("emulator", "m4board_ip", config["Emulator"]["M4Board IP"])

def toggle_value(value):
    return "Disabled" if value == "Enabled" else "Enabled"

def edit_value(stdscr, prompt, current_value, validator=None):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, f"{prompt}: (current: {current_value})")
    stdscr.addstr(4, 2, "Nuevo valor: ")
    stdscr.refresh()
    while True:
        new_val = stdscr.getstr(4, 15).decode()
        if not new_val:
            new_val = current_value
        if validator:
            if validator(new_val):
                break
            else:
                stdscr.addstr(6, 2, "Valor inválido. Intente nuevamente.", curses.A_BOLD)
                stdscr.clrtoeol()
                stdscr.move(4, 15)
        else:
            break
    curses.noecho()
    return new_val

def validate_time(val):
    try:
        datetime.strptime(val, "%H:%M:%S")
        return True
    except:
        return False

def validate_date(val):
    try:
        datetime.strptime(val, "%d/%m/%Y")
        return True
    except:
        return False

def confirm_popup(stdscr, message):
    h, w = stdscr.getmaxyx()
    win_h, win_w = 5, len(message)+10
    win_y, win_x = (h - win_h)//2, (w - win_w)//2
    win = curses.newwin(win_h, win_w, win_y, win_x)
    win.bkgd(" ", curses.color_pair(4))
    win.box()
    win.addstr(1, 2, message)
    win.addstr(3, 2, "[Y]es / [N]o")
    win.refresh()
    while True:
        key = win.getch()
        if key in [ord('y'), ord('Y')]:
            return True
        elif key in [ord('n'), ord('N')]:
            return False

# ---------------------- BIOS AMI Aptio Azul Medio ----------------------

def ami_aptio_bios_colors(stdscr):
    curses.curs_set(0)
    curses.start_color()
    
    # ---------------- Colores estilo AMI Aptio Azul Medio ----------------
    curses.init_color(1, 0, 0, 500)        # Azul oscuro (RGB 0,0,500)
    curses.init_pair(1, curses.COLOR_WHITE, 1)      # Menú superior y selección
    curses.init_pair(2, curses.COLOR_YELLOW, 1)     # Submenús/valores
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Barra inferior / ventana emergente gris
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE) # Panel lateral gris
    
    h, w = stdscr.getmaxyx()
    main_menu = ["Main", "Advanced", "Security", "Boot", "Exit"]
    config = load_config()
    current_main = 0
    current_sub = 0

    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(1))

        # ---------------- Título BIOS ----------------
        title = "AMI Aptio BIOS SETUP UTILITY"
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(0, (w - len(title)) // 2, title)
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # ---------------- Menú horizontal ----------------
        x = 2
        for idx, item in enumerate(main_menu):
            if idx == current_main:
                stdscr.attron(curses.color_pair(4) | curses.A_REVERSE)
                stdscr.addstr(2, x, f" {item} ")
                stdscr.attroff(curses.color_pair(4) | curses.A_REVERSE)
            else:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(2, x, f" {item} ")
                stdscr.attroff(curses.color_pair(1))
            x += len(item) + 4

        # ---------------- Submenú vertical ----------------
        submenu_items = list(config.get(main_menu[current_main], {}).keys())
        for i, option in enumerate(submenu_items):
            y = 5 + i
            val = config[main_menu[current_main]][option]
            display = f"{option}: {val}"
            if i == current_sub:
                stdscr.attron(curses.color_pair(4) | curses.A_REVERSE)
                stdscr.addstr(y, 4, display)
                stdscr.attroff(curses.color_pair(4) | curses.A_REVERSE)
            else:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, 4, display)
                stdscr.attroff(curses.color_pair(2))

        # ---------------- Panel lateral ----------------
        stdscr.attron(curses.color_pair(4))
        if submenu_items and 0 <= current_sub < len(submenu_items):
            panel_text = f"Selected: {submenu_items[current_sub]}"
        else:
            panel_text = "No hay elementos en el submenú"
        stdscr.addstr(5, w - len(panel_text) - 4, panel_text)
        stdscr.attroff(curses.color_pair(4))

        # ---------------- Barra inferior ----------------
        stdscr.attron(curses.color_pair(3))
        help_text = "← → Select Menu | ↑ ↓ Select Item | Enter: Edit/Toggle | F10: Save & Exit | Esc: Exit"
        stdscr.addstr(h - 2, 2, help_text[:w-4])
        stdscr.attroff(curses.color_pair(3))

        stdscr.refresh()
        key = stdscr.getch()

        # ---------------- Navegación ----------------
        if key == curses.KEY_RIGHT:
            current_main = (current_main + 1) % len(main_menu)
            current_sub = 0
        elif key == curses.KEY_LEFT:
            current_main = (current_main - 1) % len(main_menu)
            current_sub = 0
        elif key == curses.KEY_DOWN:
            current_sub = (current_sub + 1) % len(submenu_items)
        elif key == curses.KEY_UP:
            current_sub = (current_sub - 1) % len(submenu_items)
        elif key in [10, 13]:  # Enter
            selected_option = submenu_items[current_sub]
            current_val = config[main_menu[current_main]][selected_option]
            
            if str(current_val).lower() in ["enabled", "disabled"]:
                config[main_menu[current_main]][selected_option] = toggle_value(current_val)
            elif "Time" in selected_option:
                new_val = edit_value(stdscr, selected_option, current_val, validate_time)
                config[main_menu[current_main]][selected_option] = new_val
            elif "Date" in selected_option:
                new_val = edit_value(stdscr, selected_option, current_val, validate_date)
                config[main_menu[current_main]][selected_option] = new_val
            else:
                new_val = edit_value(stdscr, selected_option, current_val)
                config[main_menu[current_main]][selected_option] = new_val
        elif key == curses.KEY_F10:
            if confirm_popup(stdscr, "Save configuration?"):
                save_config(config)
            break
        elif key == 27:  # ESC
            if confirm_popup(stdscr, "Discard changes and exit?"):
                break

# ---------------------- Ejecutar BIOS ----------------------

if __name__ == "__main__":
    curses.wrapper(ami_aptio_bios_colors)