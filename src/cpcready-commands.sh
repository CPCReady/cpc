#!/bin/bash

# Carga la librería de funciones comunes
source "$CPCREADY_DIR/lib/cpcready-common.sh"
echo 
__cpcready_echo_green "Available commands:"
echo""
__cpcready_echo_command_help "  disc       " "Create a virtual disk"
__cpcready_echo_command_help "  commands   " "List available commands"
__cpcready_echo_command_help "  run        " "Run a program in the emulator"
__cpcready_echo_command_help "  save       " "Save a file to the virtual disk"
__cpcready_echo_command_help "  man        " "Show command manual"
__cpcready_echo_command_help "  help       " "Show this help message"
__cpcready_echo_command_help "  version    " "Show the software version"
echo ""

# Ejemplo de acción:
# cp "$FILE_TO_SAVE" "$HOME/.cpc/saved_files/"

