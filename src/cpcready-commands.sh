#!/bin/bash

# Carga la librería de funciones comunes
source "$CPCREADY_DIR/lib/cpcready-common.sh"

__cpcready_echo_green "Available commands:"
echo""
__cpcready_echo_command_help "  disc       " "Crea disco virtual"
__cpcready_echo_command_help "  commands   " "Listado de comandos disponibles"
__cpcready_echo_command_help "  run        " "Ejecuta un programa en el emulador"
__cpcready_echo_command_help "  save       " "Guarda un archivo en el disco virtual"
__cpcready_echo_command_help "  version    " "Muestra la versión del software"
echo ""

# Ejemplo de acción:
# cp "$FILE_TO_SAVE" "$HOME/.cpc/saved_files/"

