#!/bin/bash

# Carga la librería de funciones comunes
source "$CPCREADY_DIR/lib/cpcready-common.sh"

echo""

echo "Usage: cpc [command] [args...]"
echo ""
echo "Available commands:"
echo "  disc       Create a virtual disk"
echo "  commands   List available commands"
echo "  run        Run a program in the emulator"
echo "  save       Save a file to the virtual disk"
echo "  version    Show the software version"
echo "  help       Show this help message"
echo "" 
echo "For more details on a specific command, use: cpc [command] help"
echo ""
echo "Example: cpc save myfile.bas"
echo ""

# Ejemplo de acción:
# cp "$FILE_TO_SAVE" "$HOME/.cpc/saved_files/"

