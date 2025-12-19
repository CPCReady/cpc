#!/usr/bin/env python3
"""
Ejemplos prácticos de acceso a datos del TOML
"""

from cpcready.utils.toml_config import ConfigManager

# ============================================================
# EJEMPLO 1: Lectura Básica
# ============================================================
def ejemplo_lectura_basica():
    print("\n" + "="*60)
    print("EJEMPLO 1: Lectura Básica")
    print("="*60)

    config = ConfigManager()

    # Acceso directo a valores individuales
    selected_drive = config.get('drive', 'selected_drive', 'A')
    user = config.get('system', 'user', 0)
    model = config.get('system', 'model', '6128')
    mode = config.get('system', 'mode', 1)

    print(f"Selected Drive: {selected_drive}")
    print(f"User: {user}")
    print(f"Model: {model}")
    print(f"Mode: {mode}")


# ============================================================
# EJEMPLO 2: Lectura de Sección Completa
# ============================================================
def ejemplo_lectura_seccion():
    print("\n" + "="*60)
    print("EJEMPLO 2: Lectura de Sección Completa")
    print("="*60)

    config = ConfigManager()

    # Obtener toda la sección system
    system = config.get_section('system')

    print("Configuración del Sistema:")
    for key, value in system.items():
        print(f"  {key}: {value}")


# ============================================================
# EJEMPLO 3: Modificar Valores
# ============================================================
def ejemplo_modificar_valores():
    print("\n" + "="*60)
    print("EJEMPLO 3: Modificar Valores")
    print("="*60)

    config = ConfigManager()

    # Leer valor actual
    selected_drive = config.get('drive', 'selected_drive', 'A')
    print(f"Selected Drive ANTES: {selected_drive}")

    # Cambiar valor (cambiar entre A y B)
    new_drive = 'B' if selected_drive.upper() == 'A' else 'A'
    config.set('drive', 'selected_drive', new_drive)

    # Leer nuevo valor
    selected_drive = config.get('drive', 'selected_drive', 'A')
    print(f"Selected Drive DESPUÉS: {selected_drive}")

    # Restaurar valor original
    config.set('drive', 'selected_drive', selected_drive)


# ============================================================
# EJEMPLO 4: Uso en una Función de Consola
# ============================================================
def ejemplo_funcion_consola():
    print("\n" + "="*60)
    print("EJEMPLO 4: Uso en Función de Consola")
    print("="*60)

    config = ConfigManager()

    # Simular obtención de datos para mostrar en consola
    drive_config = config.get_section('drive')
    system_config = config.get_section('system')

    # Construir mensaje de estado
    status = []
    status.append(f"Drive {drive_config['selected_drive'].upper()} seleccionado")
    status.append(f"Usuario {system_config['user']}")
    status.append(f"Modelo CPC {system_config['model']}")
    status.append(f"Modo {system_config['mode']}")

    print("\nEstado de la Consola:")
    for item in status:
        print(f"  ✓ {item}")


# ============================================================
# EJEMPLO 5: Validación de Configuración
# ============================================================
def ejemplo_validacion():
    print("\n" + "="*60)
    print("EJEMPLO 5: Validación de Configuración")
    print("="*60)

    config = ConfigManager()

    # Verificar que los valores son válidos
    selected_drive = config.get('drive', 'selected_drive', 'A')
    model = config.get('system', 'model', '6128')
    mode = config.get('system', 'mode', 1)

    # Validaciones
    valid_drives = ['A', 'B']
    valid_models = ['464', '664', '6128']
    valid_modes = [0, 1, 2, 3]

    print("Validando configuración...")

    if selected_drive.upper() in valid_drives:
        print(f"  ✓ Drive {selected_drive} es válido")
    else:
        print(f"  ✗ Drive {selected_drive} NO es válido")

    if model in valid_models:
        print(f"  ✓ Model {model} es válido")
    else:
        print(f"  ✗ Model {model} NO es válido")

    if mode in valid_modes:
        print(f"  ✓ Mode {mode} es válido")
    else:
        print(f"  ✗ Mode {mode} NO es válido")


# ============================================================
# EJEMPLO 6: Obtener Todo el Config
# ============================================================
def ejemplo_config_completo():
    print("\n" + "="*60)
    print("EJEMPLO 6: Configuración Completa")
    print("="*60)

    config = ConfigManager()

    # Obtener toda la configuración
    all_config = config.get_all()

    print("Configuración completa:")
    for section, values in all_config.items():
        print(f"\n[{section}]")
        for key, value in values.items():
            print(f"  {key} = {value}")


# ============================================================
# EJECUTAR TODOS LOS EJEMPLOS
# ============================================================
if __name__ == "__main__":
    print("\n" + "🟥🟩🟦 EJEMPLOS DE ACCESO AL TOML 🟥🟩🟦")

    ejemplo_lectura_basica()
    ejemplo_lectura_seccion()
    ejemplo_modificar_valores()
    ejemplo_funcion_consola()
    ejemplo_validacion()
    ejemplo_config_completo()

    print("\n" + "="*60)
    print("✓ Todos los ejemplos completados")
    print("="*60 + "\n")

