#!/usr/bin/env python3
"""
Script de prueba para acceder a los datos del archivo TOML
"""

from cpcready.utils.toml_config import ConfigManager

def main():
    # Crear instancia del ConfigManager
    config = ConfigManager()

    print("=" * 60)
    print("DATOS DEL ARCHIVO TOML")
    print("=" * 60)
    print()

    # Obtener sección drive
    print("📀 DRIVE:")
    drive_config = config.get_section('drive')
    print(f"  • Drive A: {drive_config.get('drive_a', '')}")
    print(f"  • Drive B: {drive_config.get('drive_b', '')}")
    print(f"  • Selected Drive: {drive_config.get('selected_drive', 'A')}")
    print()

    # Obtener sección system
    print("⚙️  SYSTEM:")
    system_config = config.get_section('system')
    print(f"  • User: {system_config.get('user', 0)}")
    print(f"  • Model: {system_config.get('model', '6128')}")
    print(f"  • Mode: {system_config.get('mode', 1)}")
    print()

    # Obtener sección emulator
    print("🎮 EMULATOR:")
    emulator_config = config.get_section('emulator')
    print(f"  • Default: {emulator_config.get('default', 'RetroVirtualMachine')}")
    print(f"  • RVM Path: {emulator_config.get('retro_virtual_machine_path', '')}")
    print(f"  • M4Board IP: {emulator_config.get('m4board_ip', '')}")
    print()

    # También mostrar como acceder a valores individuales
    print("🔍 ACCESO INDIVIDUAL:")
    selected_drive = config.get('drive', 'selected_drive', 'A')
    user = config.get('system', 'user', 0)
    model = config.get('system', 'model', '6128')
    mode = config.get('system', 'mode', 1)

    print(f"  • Selected Drive: {selected_drive}")
    print(f"  • User: {user}")
    print(f"  • Model: {model}")
    print(f"  • Mode: {mode}")
    print()

    print("=" * 60)
    print(f"📁 Archivo de configuración: {config.config_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()

